import json

jugador_partida = {}

async def enviar(writer, data):
    writer.write((json.dumps(data) + "\n").encode())
    await writer.drain()