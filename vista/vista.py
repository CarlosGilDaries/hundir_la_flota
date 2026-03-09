from abc import ABC, abstractmethod
from modelo.resultado import ResultadoDisparo
from config.textos import TRADUCCION

class Vista(ABC):
    
    def adaptar_resultado_a_string(self, resultado: ResultadoDisparo) -> str:
        """
        Convierte el enum a str.

        Args:
            resultado (ResultadoDisparo): Objeto de la clase ResultadoDisparo que representa un resultado.

        Returns:
            str: Cadena resultado.
        """
        return TRADUCCION[resultado]
    
    
    @abstractmethod
    def pedir_disparo(self, ancho: int, alto: int) -> tuple[int, int]:
        pass
    

    @abstractmethod
    def pedir_coordenada(self, eje: str, limite: int) -> int:
        pass


    @abstractmethod
    def opcion_volver_menu(self) -> None:
        pass
    
    
    @abstractmethod
    def mostrar_resultado(self, resultado_enum: ResultadoDisparo) -> None:
        pass
    
    
    @abstractmethod
    def mostrar_tablero(self, tablero: list) -> None:
        pass
    
    
    @abstractmethod
    def mostrar_mensaje_final(self, victoria: bool) -> None:
        pass
    
    
    @abstractmethod
    def obtener_texto(self, clave: str) -> str:
        pass
    
    
    @abstractmethod
    def mostrar_mensaje(self, mensaje: str) -> None:
        pass