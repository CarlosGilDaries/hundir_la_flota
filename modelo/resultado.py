from enum import Enum, auto

class ResultadoDisparo(Enum):
    """
    Enum que representa el resultado de un disparo en el tablero.
    """
    AGUA = auto()
    TOCADO = auto()
    HUNDIDO = auto()
    REPETIDO = auto()
    INVALIDO = auto()