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
        mensaje = json.dumps(datos) + "\n"
        self._writer.write(mensaje.encode())
        await self._writer.drain()


    async def recibir(self) -> dict | None:
        data = await self._reader.readline()
        if not data:
            # El servidor cerró la conexión
            return None
        try:
            return json.loads(data.decode().strip())
        except json.JSONDecodeError:
            # Mensaje corrupto o vacío
            return None
    
    
    async def desconectar(self):
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._writer = None
            except Exception:
                pass
