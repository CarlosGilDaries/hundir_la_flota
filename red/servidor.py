from partida import Partida
from globales import jugador_partida, enviar
import asyncio
import json

# cola_espera = []
# partidas_activas = []
# jugador_partida = {}

# async def enviar(writer, data):
#     writer.write((json.dumps(data) + "\n").encode())
#     await writer.drain()

class Servidor:

    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.cola_espera = []
        self.partidas_activas = {}
        

    async def iniciar(self):
        server = await asyncio.start_server(
            self._manejar_cliente,
            self.host,
            self.port
        )

        print(f"Servidor escuchando en {self.host}:{self.port}")

        async with server:
            await server.serve_forever()

    async def _manejar_cliente(self, reader, writer):
        addr = writer.get_extra_info("peername")
        print(f"Cliente conectado desde {addr}")
        
        self.cola_espera.append(writer)
        
        await enviar(writer, {
            "tipo": "espera",
            "mensaje": "Esperando rival..."
        })
        
        if len(self.cola_espera) >= 2:
            j1 = self.cola_espera.pop(0)
            j2 = self.cola_espera.pop(0)

            partida = Partida(j1, j2)
            self.partidas_activas.append(partida)


        try:
            while True:
                data = await reader.readline()
                if not data:
                    break

                mensaje = json.loads(data.decode().strip())

                if writer in jugador_partida:
                    partida = jugador_partida[writer]
                    await partida.recibir_mensaje(writer, mensaje)
                else:
                    print("Mensaje recibido sin partida asociada")

        except ConnectionResetError:
            print(f"Conexión perdida con {addr}")

        finally:
            print(f"Cliente desconectado: {addr}")
            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    servidor = Servidor()
    asyncio.run(servidor.iniciar())
