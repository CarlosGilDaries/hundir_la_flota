import asyncio
import json
from typing import Any
from asyncio import StreamReader, StreamWriter

class ClienteSocket:
    """
        Cliente TCP asíncrono encargado de la comunicación con el servidor.
        Implementa un protocolo simple basado en mensajes JSON delimitados
        por salto de línea (`\\n`). Cada mensaje enviado o recibido representa
        un evento del juego.
        """
    def __init__(self, host: str, puerto: int) -> None:
        """
        Inicializa el cliente de red.

        Args:
            host (str): Dirección del servidor.
            puerto (int): Puerto del servidor.
        """
        self._host = host
        self._puerto = puerto
        self._reader = None
        self._writer = None


    async def conectar(self) -> None:
        """
        Establece la conexión TCP con el servidor.

        Returns:
            None
        """
        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._puerto
        )


    async def enviar(self, data: dict[str, Any]) -> None:
        """
        Envía un mensaje JSON al servidor.
        El mensaje se serializa como JSON y se delimita con un salto de línea
        para permitir su lectura mediante `readline()` en el servidor.

        Args:
            data (dict[str, Any]): Diccionario que representa el mensaje a enviar.

        Returns:
            None
        """
        mensaje = json.dumps(data) + "\n"
        self._writer.write(mensaje.encode())
        await self._writer.drain()


    async def recibir(self) -> dict[str, Any] | None:
        """
        Recibe un mensaje JSON desde el servidor.
        Lee una línea completa del socket y la convierte en un diccionario.

        Returns:
            dict[str, Any] | None:
                - Diccionario con el mensaje recibido si es válido.
                - None si el servidor cerró la conexión o el JSON es inválido.
        """
        data = await self._reader.readline()
        # print("RAW RECIBIDO:", repr(data))
        if not data:
            print("SERVIDOR CERRÓ LA CONEXIÓN")
            return None

        texto = data.decode().strip()
        # print("SERVIDOR -> CLIENTE:", texto)

        try:
            return json.loads(texto)
        except json.JSONDecodeError:
            print("ERROR JSON:", texto)
            return None
    
    
    async def desconectar(self):
        """
        Cierra la conexión con el servidor de forma segura.

        Returns:
            None
        """
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._writer = None
            except Exception:
                pass
