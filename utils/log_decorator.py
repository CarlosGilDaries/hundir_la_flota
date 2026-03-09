from functools import wraps
from typing import Callable, Awaitable, TypeVar, Any
from utils.log import configurar_logger

logger = configurar_logger()
T = TypeVar("T")

def log_async(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorador para registrar la ejecución de funciones asíncronas.
    Este decorador envuelve funciones `async` y captura cualquier excepción
    producida durante su ejecución, registrándola en el logger configurado.

    Args:
        func (Callable[..., Awaitable[T]]): Función asíncrona a decorar.

    Returns:
        Callable[..., Awaitable[T]]: Función decorada que mantiene la misma
        firma y comportamiento que la función original.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        """
        Función envolvente que ejecuta la función original y registra errores.

        Args:
            *args (Any): Argumentos posicionales de la función decorada.
            **kwargs (Any): Argumentos nombrados de la función decorada.

        Returns:
            T: Resultado devuelto por la función decorada.

        Raises:
            Exception: Relanza cualquier excepción capturada tras registrarla.
        """
        #logger.info(f"Entrando en {func.__name__}")
        try:
            resultado = await func(*args, **kwargs)
            #logger.info(f"Saliendo de {func.__name__}")
            
            return resultado

        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}")
            
            raise

    return wrapper
