import asyncio
import json


async def send(writer: asyncio.StreamWriter, data: dict) -> None:
    """
    Sends a JSON message to a client via its writer.

    Serializes the data to JSON format, adds a newline as a message delimiter,
    encodes to bytes, and writes to the stream. The added newline serves as
    an end-of-message marker, allowing the client to read line by line with
    reader.readline(). Finally, it ensures the data is fully sent (drain).

    Args:
        writer (asyncio.StreamWriter): Writer of the target client.
        data (dict): Data to send (JSON).
    """
    message = json.dumps(data) + "\n"
    # print("SERVER -> CLIENT:", message.strip())
    writer.write(message.encode())
    await writer.drain()