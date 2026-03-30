from abc import ABC, abstractmethod
from model.result import ResultadoDisparo
from config.texts import TRADUCCION

class Vista(ABC):
    """
    Clase abstracta que define la interfaz de las vistas del sistema.
    La vista es responsable exclusivamente de la interacción con el usuario,
    mostrando información y solicitando entradas cuando sea necesario.
    Las implementaciones concretas (por ejemplo, consola o web) deben
    implementar todos los métodos abstractos definidos aquí.
    """
    def adaptar_resultado_a_string(self, resultado: ResultadoDisparo) -> str:
        """
        Convierte un resultado de disparo (enum) a su representación textual.

        Args:
            resultado (ResultadoDisparo): Resultado del disparo.

        Returns:
            str: Cadena asociada al resultado.
        """
        return TRADUCCION[resultado]
    
    
    @abstractmethod
    def pedir_disparo(self, ancho: int, alto: int) -> tuple[int, int]:
        """
        Solicita al usuario las coordenadas de un disparo.

        Args:
            ancho (int): Ancho del tablero.
            alto (int): Alto del tablero.

        Returns:
            tuple[int, int]: Coordenadas (x, y) del disparo.
        """
        pass
    

    @abstractmethod
    def pedir_coordenada(self, eje: str, limite: int) -> int:
        """
        Solicita una coordenada válida al usuario.

        Args:
            eje (str): Nombre del eje ("x" o "y").
            limite (int): Valor máximo permitido.

        Returns:
            int: Coordenada introducida.
        """
        pass


    @abstractmethod
    def opcion_volver_menu(self) -> None:
        """
        Muestra la opción de volver al menú principal.
        """
        pass
    
    
    @abstractmethod
    def mostrar_resultado(self, resultado_enum: ResultadoDisparo) -> None:
        """
        Muestra el resultado de un disparo.

        Args:
            resultado_enum (ResultadoDisparo): Resultado del disparo.
        """
        pass
    
    
    @abstractmethod
    def mostrar_tablero(self, tablero: list[list[str]]) -> None:
        """
        Muestra un tablero de juego.

        Args:
            tablero (list[list[str]]): Representación del tablero.
        """
        pass
    
    
    @abstractmethod
    def mostrar_mensaje_final(self, victoria: bool, pvp: bool) -> None:
        """
        Muestra el mensaje final de la partida.

        Args:
            victoria (bool): Indica si el jugador ha ganado.
            pvp (bool): Indica si es una partida entre jugadores.
        """
        pass
    
    
    @abstractmethod
    def obtener_texto(self, clave: str) -> str:
        """
        Devuelve un texto asociado a una clave.

        Args:
            clave (str): Clave del texto.

        Returns:
            str: Texto correspondiente.
        """
        pass
    
    
    @abstractmethod
    def mostrar_mensaje(self, mensaje: str) -> None:
        """
        Muestra un mensaje al usuario.

        Args:
            mensaje (str): Mensaje a mostrar.
        """
        pass