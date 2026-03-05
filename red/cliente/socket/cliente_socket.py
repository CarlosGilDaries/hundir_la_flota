import asyncio
import json


class ClienteSocket:

    def __init__(self, host: str, puerto: int) -> None:
        self._host = host
        self._puerto = puerto
        self._reader = None
        self._writer = None


    async def conectar(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._puerto
        )


    async def enviar(self, datos: dict) -> None:
        mensaje = json.dumps(datos)
        self._writer.write(mensaje.encode())
        await self._writer.drain()


    async def recibir(self) -> dict:
        data = await self._reader.read(4096)
        return json.loads(data.decode())
