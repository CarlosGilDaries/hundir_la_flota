from servidor.sesion_pvp import SesionPVP
from servidor.globales import enviar, jugador_partida
from config.protocolo import obtener_tipo
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

        print(f"Servidor escuchando en {self.host}:{self.port}")

        async with server:
            await server.serve_forever()


    async def _manejar_cliente(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Gestiona el ciclo de vida completo de un cliente conectado.
    
        Maneja la conexión del cliente, lo coloca en cola de espera,
        lo asigna a partidas cuando hay rival disponible y procesa
        los mensajes entrantes durante la partida.
        
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
        print(f"Cliente conectado desde {addr}")

        self.cola_espera.append(writer)

        await enviar(writer, {
            "tipo": "espera",
            "mensaje": "Esperando rival..."
        })

        sesion = None
        if len(self.cola_espera) >= 2:
            # Sacamos dos jugadores de la cola y creamos la partida
            j1 = self.cola_espera.pop(0)
            j2 = self.cola_espera.pop(0)

            sesion = SesionPVP(j1, j2)
            self.partidas_activas.append(sesion)
            await sesion.iniciar()

        try:
            while True:
                data = await reader.readline()
                if not data:
                    print(f"Cliente desconectado: {addr}")
                    break

                try:
                    mensaje = json.loads(data.decode().strip())
                except json.JSONDecodeError:
                    continue  # ignorar mensajes corruptos

                if writer in jugador_partida:
                    partida = jugador_partida[writer]
                    await partida.recibir_mensaje(writer, mensaje)

        except ConnectionResetError:
            print(f"Conexión perdida con {addr}")

        finally:
            # Si estaba en cola, quitarlo
            if writer in self.cola_espera:
                self.cola_espera.remove(writer)

            # Si estaba en partida, notificar desconexión
            partida = jugador_partida.get(writer)
            if partida:
                await partida.jugador_desconectado(writer)
                for w in list(partida._writers.values()):
                    if w in jugador_partida:
                        del jugador_partida[w]
                if partida in self.partidas_activas:
                    self.partidas_activas.remove(partida)

            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass


if __name__ == "__main__":
    servidor = Servidor()
    asyncio.run(servidor.iniciar())
