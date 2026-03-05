import json
import asyncio

jugador_partida = {}

async def enviar(writer: asyncio.StreamWriter, data: dict) -> None:
    """
    Envía un mensaje JSON a un cliente a través de su writer.
    
    Serializa los datos a formato JSON, añade un salto de línea como
    delimitador de mensaje, codifica a bytes y escribe en el stream.
    El salto de línea añadido sirve como marcador de fin de mensaje,
    permitiendo al cliente leer línea por línea con reader.readline().
    Finaliza asegurando que los datos se envían completamente (drain).

    Args:
        writer (asyncio.StreamWriter): Writer del cliente destinatario.
        data (dict): Datos a enviar (JSON).
    """
    writer.write((json.dumps(data) + "\n").encode())
    await writer.drain()