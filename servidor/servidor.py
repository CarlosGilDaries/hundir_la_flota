from servidor.sesion_pvp import SesionPVP
from servidor.globales import enviar, jugador_partida
from config.protocolo import obtener_tipo
from servidor.log import logger
import asyncio
import json

class Servidor:

    def __init__(self, host: str = "127.0.0.1", port: int = 8888) -> None:
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

        logger.info(f"\nServidor escuchando en {self.host}:{self.port}")

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
        
        logger.info("\n=======================================================")
        logger.info(f"Jugador {jugador_id} conectado desde {addr}")
        logger.info("=======================================================")

        self.cola_espera.append(writer)

        await enviar(writer, {
            "tipo": "espera",
            "mensaje": "Esperando rival..."
        })

        logger.info("\n========================================================")
        logger.info(f"Jugadores en espera: {len(self.cola_espera)}")
        logger.info("========================================================")

        if len(self.cola_espera) >= 2:
            j1 = self.cola_espera.pop(0)
            j2 = self.cola_espera.pop(0)
            id1 = self._ids[j1]
            id2 = self._ids[j2]
            addr1 = j1.get_extra_info("peername")
            addr2 = j2.get_extra_info("peername")
            partida_id = self._contador_partidas
            self._contador_partidas += 1

            sesion = SesionPVP(j1, j2, partida_id)
            self.partidas_activas.append(sesion)

            await sesion.iniciar()
            
            logger.info("\n----------- PARTIDA INICIADA -----------")
            logger.info(f"Partida #{partida_id}")
            logger.info(f"Jugador {id1} {addr1}")
            logger.info(f"Jugador {id2} {addr2}")
            logger.info("----------------------------------------\n")
            logger.info("========================================================")
            logger.info(f"Partidas activas: {len(self.partidas_activas)}")
            logger.info("\n========================================================")
            logger.info(f"Jugadores en espera: {len(self.cola_espera)}")
            logger.info("========================================================")

        try:
            while True:

                data = await reader.readline()

                if not data:
                    logger.info("\n=======================================================")
                    logger.info(f"Cliente desconectado: J{jugador_id} {addr}")
                    logger.info("========================================================")
                    break

                mensaje = json.loads(data.decode().strip())

                if writer in jugador_partida:
                    partida = jugador_partida[writer]
                    await partida.recibir_mensaje(writer, mensaje)
            
            writer.close()
            await writer.wait_closed()

        except ConnectionResetError:
            logger.info("\n=======================================================")
            logger.info(f"Conexión perdida con J{jugador_id} {addr}")
            logger.info("========================================================")
        
        finally:
            if writer in self._ids:
                del self._ids[writer]



if __name__ == "__main__":
    servidor = Servidor()
    asyncio.run(servidor.iniciar())
