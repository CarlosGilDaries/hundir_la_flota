from red.partida import Partida
from red.globales import enviar, jugador_partida
import asyncio
import json

class Servidor:

    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.cola_espera = []
        self.partidas_activas = []
        

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

        except ConnectionResetError:
            print(f"Conexión perdida con {addr}")

        finally:
            print(f"Cliente desconectado: {addr}")

            # Si estaba en cola
            if writer in self.cola_espera:
                self.cola_espera.remove(writer)

            # Si estaba en partida
            if writer in jugador_partida:
                partida = jugador_partida[writer]
                await partida.jugador_desconectado(writer)

                # limpiar asociaciones con seguridad
                for jugador in [partida.jugador1, partida.jugador2]:
                    if jugador in jugador_partida:
                        del jugador_partida[jugador]

                if partida in self.partidas_activas:
                    self.partidas_activas.remove(partida)

            writer.close()
            await writer.wait_closed()


if __name__ == "__main__":
    servidor = Servidor()
    asyncio.run(servidor.iniciar())
