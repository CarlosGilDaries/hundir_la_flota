from functools import wraps
from utils.log import configurar_logger

logger = configurar_logger()

def log_async(func):
    """
    Decorador para registrar la ejecución de funciones asíncronas.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        #logger.info(f"Entrando en {func.__name__}")

        try:
            resultado = await func(*args, **kwargs)
            #logger.info(f"Saliendo de {func.__name__}")
            
            return resultado

        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}")
            
            raise

    return wrapper
