from functools import wraps
from typing import Callable, Awaitable, TypeVar, Any
from utils.log import configure_logger

logger = configure_logger()
T = TypeVar("T")


def log_async(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorator to log the execution of asynchronous functions.
    This decorator wraps `async` functions and catches any exception
    raised during their execution, logging it with the configured logger.

    Args:
        func (Callable[..., Awaitable[T]]): Asynchronous function to decorate.

    Returns:
        Callable[..., Awaitable[T]]: Decorated function that maintains the same
        signature and behavior as the original function.
    """


    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        """
        Wrapper function that executes the original function and logs errors.

        Args:
            *args (Any): Positional arguments of the decorated function.
            **kwargs (Any): Keyword arguments of the decorated function.

        Returns:
            T: Result returned by the decorated function.

        Raises:
            Exception: Re-raises any caught exception after logging it.
        """
        # logger.info(f"Entering {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            # logger.info(f"Exiting {func.__name__}")
            return result

        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper
