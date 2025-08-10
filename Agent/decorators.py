import time
import logging
from functools import wraps
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

def log_exceptions(default: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to log exceptions raised by the decorated function and return a default value.

    Args:
        default (Any): The value to return if an exception occurs.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Exception in {func.__name__}: {e}")
                return default
        return wrapper
    return decorator

def rate_limiter(calls_per_second: float) -> Callable[[F], F]:
    """
    Decorator to limit the rate at which a function can be called.

    Args:
        calls_per_second (float): Maximum number of allowed calls per second.

    Returns:
        Callable: The decorated function.
    """
    interval = 1.0 / calls_per_second
    last_called = [0.0]  # Mutable container to store last call time

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.time() - last_called[0]
            wait_time = interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return cast(F, wrapper)
    return decorator

def timing(func: F) -> F:
    """
    Decorator to measure and print the execution time of a function.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = (end - start) * 1000  # milliseconds
        print(f"[TIMER] {func.__name__} took {duration:.2f} ms")
        return result
    return cast(F, wrapper)

def log_io(func: F) -> F:
    """
    Decorator to log the input arguments and output of a function.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        arg_str = ", ".join(repr(a) for a in args)
        kwarg_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        print(f"[INPUT] {func.__name__}({arg_str}{', ' if kwarg_str else ''}{kwarg_str})")
        result = func(*args, **kwargs)
        print(f"[OUTPUT] {func.__name__} -> {result!r}")
        return result
    return cast(F, wrapper)

def retry(max_retries: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """
    Decorator to retry a function if it raises an exception.

    Args:
        max_retries (int): Maximum number of retries.
        delay (float): Delay in seconds between retries.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Retry {i+1}/{max_retries} for {func.__name__} failed: {e}")
                    time.sleep(delay)
            logger.error(f"{func.__name__} failed after {max_retries} attempts")
            raise Exception(f"{func.__name__} failed after {max_retries} attempts")
        return cast(F, wrapper)
    return decorator