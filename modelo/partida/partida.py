from abc import ABC, abstractmethod
from typing import Optional
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo

class Partida(ABC):
    """
    Clase abstracta que define el contrato común de cualquier tipo de partida.

    Las implementaciones concretas (PVE o PVP) deben proporcionar la lógica
    para disparos, colocación de barcos y obtención de tableros.
    """

    @abstractmethod
    def disparar(self, x: int, y: int) -> ResultadoDisparo:
        """
        Realiza un disparo en la posición indicada.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            ResultadoDisparo: Resultado del disparo.
        """
        pass
    
    
    @abstractmethod
    def obtener_tablero_propio(self, jugador: Optional[int] = None) -> list[list[str]]:
        """
        Obtiene el tablero propio del jugador.

        Args:
            jugador (Optional[int], optional): Identificador del jugador en partidas PVP.

        Returns:
            list[list[str]]: Representación del tablero propio.
        """
        pass
    
    
    @abstractmethod
    def obtener_tablero_rival(self, jugador: Optional[int] = None) -> list[list[str]]:
        """
        Obtiene el tablero rival visible para el jugador.

        Args:
            jugador (Optional[int], optional): Identificador del jugador en partidas PVP.

        Returns:
            list[list[str]]: Representación del tablero rival.
        """
        pass
    
    
    @abstractmethod
    def colocar_barco(self, barco: Barco, x: Optional[int] = None, y: Optional[int] = None, horizontal: Optional[int] = None, jugador: Optional[int] = None) -> bool:
        """
        Coloca un barco en el tablero.

        Args:
            barco (Barco): Barco que se va a colocar.
            x (Optional[int]): Coordenada X inicial.
            y (Optional[int]): Coordenada Y inicial.
            horizontal (Optional[bool]): Orientación del barco.
            jugador (Optional[int]): Identificador del jugador en PVP.

        Returns:
            bool: True si se pudo colocar correctamente, False si no.
        """
        pass
    

    @abstractmethod
    def hay_victoria(self) -> bool:
        """
        Comprueba si la partida ha terminado con victoria.

        Returns:
            bool: True si hay un ganador, False en caso contrario.
        """
        pass