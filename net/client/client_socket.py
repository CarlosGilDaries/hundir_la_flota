import asyncio
import json
from typing import Any
from asyncio import StreamReader, StreamWriter
from net.protocol.messages import ProtocolMessage


class ClientSocket:
    """
    Asynchronous TCP client responsible for communicating with the server.
    Implements a simple protocol based on JSON messages delimited by newline (`\\n`).
    Each sent or received message represents a game event.
    """

    def __init__(self, host: str, port: int) -> None:
        """
        Initializes the network client.

        Args:
            host (str): Server address.
            port (int): Server port.
        """
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None


    async def connect(self) -> None:
        """
        Establishes the TCP connection with the server.
        """
        self._reader, self._writer = await asyncio.open_connection(
            self._host,
            self._port
        )


    async def send(self, data: ProtocolMessage) -> None:
        """
        Sends a JSON message to the server.
        The message is serialized as JSON and delimited with a newline
        to allow reading via `readline()` on the server side.

        Args:
            data (dict[str, Any]): Dictionary representing the message to send.
        """
        message = json.dumps(data) + "\n"
        self._writer.write(message.encode())
        await self._writer.drain()


    async def receive(self) -> ProtocolMessage | None:
        """
        Receives a JSON message from the server.
        Reads a complete line from the socket and converts it into a dictionary.

        Returns:
            dict[str, Any] | None:
                - Dictionary with the received message if valid.
                - None if the server closed the connection or the JSON is invalid.
        """
        data = await self._reader.readline()
        # print("RAW RECIBIDO:", repr(data))
        if not data:
            print("SERVIDOR CERRÓ LA CONEXIÓN")
            return None

        text = data.decode().strip()
        # print("SERVIDOR -> CLIENTE:", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print("ERROR JSON:", text)
            return None


    async def disconnect(self) -> None:
        """
        Closes the connection with the server safely.
        """
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._writer = None
            except Exception:
                pass