from red.servidor.sesion_pvp import SesionPVP
from utils.log import configurar_logger
from utils.log_decorator import log_async
from config.eventos_log import (
    SERVER_START, PLAYER_CONNECTED, QUEUE_ADD, PLAYER_DISCONNECTED,
    PLAYER_EXIT, PLAYER_CONNECTION_LOST, MATCH_CREATED
)
from red.helpers.enviar import enviar
from collections import deque
import asyncio
import json
import time


class Servidor:
    """
    Servidor TCP asíncrono encargado de gestionar las conexiones de clientes
    y emparejar jugadores en partidas PVP.
    """
    def __init__(self, host: str = "0.0.0.0", port: int = 8888) -> None:
        """
        Inicializa el servidor.

        Args:
            host (str): Dirección IP del servidor.
            port (int): Puerto en el que escuchar conexiones.
        """
        self.host = host
        self.port = port
        self.cola_espera = deque()
        self.cola_tiempos = {}  # Mapea writer -> timestamp de entrada a cola
        self.partidas_activas = []
        self._contador_jugadores = 1
        self._contador_partidas = 1
        self._ids = {}
        self.logger = configurar_logger()
        self.jugador_partida = {}
        self._lock_cola = asyncio.Lock()
        self._lock_contador = asyncio.Lock()
        self._lock_partida = asyncio.Lock()
        self.TIMEOUT_COLA = 15  # Segundos
        

    async def iniciar(self) -> None:
        """
        Inicia el servidor TCP y comienza a aceptar conexiones.
        El servidor se ejecuta indefinidamente mediante `serve_forever()`.

        Returns:
            None
        """
        server = await asyncio.start_server(
            self._manejar_cliente,
            self.host,
            self.port
        )

        self.logger.info(f"{SERVER_START} host={self.host} port={self.port}")
        
        asyncio.create_task(self._matchmaker())

        async with server:
            await server.serve_forever()


    @log_async
    async def _manejar_cliente(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Gestiona el ciclo de vida completo de un cliente conectado.

        Responsabilidades principales:
        - Asignar un identificador único al jugador.
        - Registrar su conexión en el servidor.
        - Añadirlo a la cola de espera para ser emparejado por el matchmaker.
        - Enviar el mensaje inicial de espera.
        - Recibir y procesar mensajes enviados por el cliente.
        - Redirigir los mensajes a la sesión de partida correspondiente si existe.
        - Detectar desconexiones o solicitudes de salida.
        - Liberar recursos y limpiar referencias cuando el cliente abandona.

        Args:
            reader (asyncio.StreamReader): Flujo de lectura del socket del cliente.
            writer (asyncio.StreamWriter): Flujo de escritura del socket del cliente.

        Returns:
            None
        """
        addr = writer.get_extra_info("peername")
        
        async with self._lock_contador:
            jugador_id = self._contador_jugadores
            self._contador_jugadores += 1
            self._ids[writer] = jugador_id
        
        self.logger.info(f"{PLAYER_CONNECTED} player={jugador_id} addr={addr}")
        
        async with self._lock_cola:
            self.cola_espera.append(writer)
            self.cola_tiempos[writer] = time.time()  # Guardar timestamp de entrada a cola
            self.logger.info(f"{QUEUE_ADD} player={jugador_id} waiting={len(self.cola_espera)}")


        await enviar(writer, {
            "tipo": "espera",
            "mensaje": "Esperando rival..."
        })

        try:
            while True:
                data = await reader.readline()
                
                if not data:
                    self.logger.info(f"{PLAYER_DISCONNECTED} player={jugador_id} addr={addr}")
                    
                    partida = None
                    async with self._lock_partida:
                        if writer in self.jugador_partida:
                            partida = self.jugador_partida[writer]
                    
                    if partida:
                        await partida.jugador_desconectado(writer, es_abandono=True)

                    break

                mensaje = json.loads(data.decode().strip())
                if mensaje.get("tipo") == "salir":
                    self.logger.info(f"{PLAYER_EXIT} player={jugador_id} addr={addr}")

                    partida = None
                    async with self._lock_partida:
                        if writer in self.jugador_partida:
                            partida = self.jugador_partida[writer]
                    
                    if partida:
                        await partida.jugador_desconectado(writer, es_abandono=True)

                    break

                partida = None
                async with self._lock_partida:
                    if writer in self.jugador_partida:
                        partida = self.jugador_partida[writer]
                
                if partida:
                    await partida.recibir_mensaje(writer, mensaje)

        except ConnectionResetError:
            self.logger.warning(f"{PLAYER_CONNECTION_LOST} player={jugador_id} addr={addr}")

            partida = None
            async with self._lock_partida:
                if writer in self.jugador_partida:
                    partida = self.jugador_partida[writer]
            
            if partida:
                await partida.jugador_desconectado(writer, es_abandono=True)
        
        finally:
            partida = None
            async with self._lock_partida:
                if writer in self.jugador_partida:
                    partida = self.jugador_partida[writer]
            
            if partida:
                await partida.jugador_desconectado(writer)

            async with self._lock_cola:
                if writer in self.cola_espera:
                    self.cola_espera.remove(writer)
                if writer in self.cola_tiempos:
                    del self.cola_tiempos[writer]

            async with self._lock_contador:
                if writer in self._ids:
                    del self._ids[writer]

            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            
        
    async def _matchmaker(self) -> None:
        """
        Tarea asíncrona que empareja jugadores de la cola
        y crea partidas cuando hay suficientes.
        También revisa timeouts para jugadores que han esperado demasiado.
        """
        while True:
            # Revisar timeouts
            await self._revisar_timeouts_cola()
            
            sesion = None
            async with self._lock_cola:
                if len(self.cola_espera) >= 2:
                    j1 = self.cola_espera.popleft()
                    j2 = self.cola_espera.popleft()                  
                    # Limpiar tiempos
                    if j1 in self.cola_tiempos:
                        del self.cola_tiempos[j1]
                    if j2 in self.cola_tiempos:
                        del self.cola_tiempos[j2]
                else:
                    j1 = j2 = None

            if j1 is not None and j2 is not None:
                async with self._lock_contador:
                    id1 = self._ids.get(j1, -1)
                    id2 = self._ids.get(j2, -1)
                    
                    # Si alguno fue limpiado, no crear sesión
                    if id1 < 0 or id2 < 0:
                        j1 = j2 = None
                    else:
                        addr1 = j1.get_extra_info("peername")
                        addr2 = j2.get_extra_info("peername")

                        partida_id = self._contador_partidas
                        self._contador_partidas += 1

            if j1 is not None and j2 is not None:
                sesion = SesionPVP(
                    j1,
                    j2,
                    id1,
                    id2,
                    addr1,
                    addr2,
                    partida_id,
                    self.logger,
                    self.jugador_partida,
                    self._lock_partida,
                    self.partidas_activas
                )

                async with self._lock_partida:
                    self.partidas_activas.append(sesion)
            
            if sesion:    
                await sesion.iniciar()
                self.logger.info(f"{MATCH_CREATED} match={partida_id} player1={id1} player2={id2}")
                
            await asyncio.sleep(0.1)

    
    async def _revisar_timeouts_cola(self) -> None:
        """
        Revisa si hay jugadores en la cola que han excedido el tiempo de espera.
        Si es así, los saca de la cola y les envía un mensaje de timeout.

        Returns:
            None
        """
        tiempo_actual = time.time()
        
        async with self._lock_cola:
            jugadores_timeout = []
            
            # Identificar jugadores con timeout
            for writer in list(self.cola_espera):
                if writer in self.cola_tiempos:
                    tiempo_espera = tiempo_actual - self.cola_tiempos[writer]
                    if tiempo_espera >= self.TIMEOUT_COLA:
                        jugadores_timeout.append(writer)
            
            # Remover de cola
            for writer in jugadores_timeout:
                try:
                    self.cola_espera.remove(writer)
                    del self.cola_tiempos[writer]
                except (ValueError, KeyError):
                    pass
        
        # Enviar mensajes (fuera del lock para no bloquear)
        for writer in jugadores_timeout:
            try:
                await enviar(writer, {
                    "tipo": "timeout_cola",
                    "razon": "rivales_no_disponibles"
                })
                
                # Obtener ID para loguear
                async with self._lock_contador:
                    jugador_id = self._ids.get(writer, -1)
                
                if jugador_id >= 0:
                    self.logger.info(f"PLAYER_TIMEOUT player={jugador_id} razón=sin_rival_disponible")
                
            except Exception as e:
                self.logger.warning(f"Error enviando timeout: {e}")


if __name__ == "__main__":
    servidor = Servidor()
    try:
        asyncio.run(servidor.iniciar())
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido manualmente. Cerrando partidas...")
        for sesion in servidor.partidas_activas:
            for w in sesion._writers.values():
                try:
                    w.close()
                    asyncio.run(w.wait_closed())
                except:
                    pass
        print("[INFO] Todas las partidas cerradas.")
