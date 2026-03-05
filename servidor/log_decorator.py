from servidor.log import logger
import functools
import json

def log_mensajes(func):
    @functools.wraps(func)
    async def wrapper(self, writer, mensaje, *args, **kwargs):
        jugador = self._jugadores.get(writer, "desconocido")
        partida = getattr(self, "partida_id", "desconocida")
        logger.info(f"[PARTIDA {partida}] J{jugador} envía: {json.dumps(mensaje)}")
        resultado = await func(self, writer, mensaje, *args, **kwargs)
        logger.info(f"[PARTIDA {partida}] J{jugador} procesado")
        return resultado
    return wrapper
