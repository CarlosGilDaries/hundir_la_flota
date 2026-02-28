from abc import ABC, abstractmethod

class Juego(ABC):

    def __init__(self, caracter_vacio, caracter_tocado, caracter_agua):
        """
        Clase abstracta Juego de la que heredan JuegoPVE y JuegoPVP.

        Args:
            caracter_vacio (str): Carácter para casillas vacías.
            caracter_tocado (str): Carácter para disparos acertados.
            caracter_agua (str): Carácter para disparos fallidos.
        """
        self._caracter_vacio = caracter_vacio
        self._caracter_tocado = caracter_tocado
        self._caracter_agua = caracter_agua


    @abstractmethod
    def disparar(self, x, y):
        """
        Realiza un disparo sobre el tablero.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
        """
        pass


    @abstractmethod
    def hay_victoria(self):
        """
        Comprueba si quedan barcos en el tablero rival.
        """
        pass