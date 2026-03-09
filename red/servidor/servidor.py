from red.servidor.sesion_pvp import SesionPVP
from utils.log import configurar_logger
from red.helpers.enviar import enviar
from red.protocolo.mensajes import obtener_tipo
import asyncio
import json


class Servidor:

    def __init__(self, host: str = "0.0.0.0", port: int = 8888) -> None:
        """
        Inicializa el servidor con la configuración de red y estado inicial.

        Args:
            host (str, optional): IP del servidor. Defaults to "127.0.0.1".
            port (int, optional): Puerto de conexión. Defaults to 8888.
        """
        self.host = host
        self.port = port
        self.cola_espera = []
        self.partidas_activas = []
        self._contador_jugadores = 1
        self._contador_partidas = 1
        self._ids = {}
        self.logger = configurar_logger()
        self.jugador_partida = {}
        

    async def iniciar(self) -> None:
        """
        Inicia el servidor asíncrono y comienza a aceptar conexiones de clientes.
    
        Configura y ejecuta el servidor en la dirección y puerto especificados,
        manteniéndolo en ejecución hasta que sea detenido manualmente.
        
        La corrutina se ejecuta indefinidamente (serve_forever).
        """
        server = await asyncio.start_server(
            self._manejar_cliente,
            self.host,
            self.port
        )

        self.logger.info(f"SERVER_START host={self.host} port={self.port}")

        async with server:
            await server.serve_forever()


    async def _manejar_cliente(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Gestiona el ciclo de vida completo de un cliente conectado.
    
        Maneja la conexión del cliente, lo coloca en cola de espera,
        lo asigna a partidas cuando hay rival disponible y procesa
        los mensajes entrantes durante la partida.
        
        Asigna ids a los clientes y a las partidas entre ellos.        
        Limpia automáticamente los recursos cuando el cliente se desconecta.
        Elimina al cliente de colas y partidas activas al finalizar.
        Maneja errores de conexión como ConnectionResetError.

        Args:
            reader (asyncio.StreamReader): Flujo de lectura para recibir
                datos del cliente.
            writer (asyncio.StreamWriter): Flujo de escritura para enviar
                datos al cliente.
        """
        addr = writer.get_extra_info("peername")
        jugador_id = self._contador_jugadores
        self._contador_jugadores += 1
        self._ids[writer] = jugador_id
        
        self.logger.info(f"PLAYER_CONNECTED player={jugador_id} addr={addr}")

        self.cola_espera.append(writer)
        
        self.logger.info(f"QUEUE_ADD player={jugador_id} waiting={len(self.cola_espera)}")


        await enviar(writer, {
            "tipo": "espera",
            "mensaje": "Esperando rival..."
        })

        if len(self.cola_espera) >= 2:
            j1 = self.cola_espera.pop(0)
            j2 = self.cola_espera.pop(0)
            id1 = self._ids[j1]
            id2 = self._ids[j2]
            addr1 = j1.get_extra_info("peername")
            addr2 = j2.get_extra_info("peername")
            partida_id = self._contador_partidas
            self._contador_partidas += 1

            sesion = SesionPVP(
                j1,
                j2,
                id1,
                id2,
                addr1,
                addr2,
                partida_id,
                self.logger,
                self.jugador_partida
            )
            self.partidas_activas.append(sesion)

            await sesion.iniciar()
            
            self.logger.info(f"MATCH_CREATED match={partida_id} player1={id1} player2={id2}")

        try:
            while True:
                data = await reader.readline()

                if not data:
                    self.logger.info(f"PLAYER_DISCONNECTED player={jugador_id} addr={addr}")
                    
                    if writer in self.jugador_partida:
                        partida = self.jugador_partida[writer]
                        await partida.jugador_desconectado(writer)

                    break

                mensaje = json.loads(data.decode().strip())
                if mensaje.get("tipo") == "salir":
                    self.logger.info(f"PLAYER_EXIT player={jugador_id} addr={addr}")

                    if writer in self.jugador_partida:
                        partida = self.jugador_partida[writer]
                        await partida.jugador_desconectado(writer)

                    break

                if writer in self.jugador_partida:
                    partida = self.jugador_partida[writer]
                    await partida.recibir_mensaje(writer, mensaje)
            
            writer.close()
            await writer.wait_closed()

        except ConnectionResetError:
            self.logger.warning(f"PLAYER_CONNECTION_LOST player={jugador_id} addr={addr}")

            if writer in self.jugador_partida:
                partida = self.jugador_partida[writer]
                await partida.jugador_desconectado(writer)
        
        finally:
            if writer in self.jugador_partida:
                partida = self.jugador_partida[writer]
                await partida.jugador_desconectado(writer)

            if writer in self.cola_espera:
                self.cola_espera.remove(writer)

            if writer in self._ids:
                del self._ids[writer]

            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass


if __name__ == "__main__":
    servidor = Servidor()
    asyncio.run(servidor.iniciar())
