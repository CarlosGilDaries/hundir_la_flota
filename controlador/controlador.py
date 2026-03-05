from abc import ABC, abstractmethod
from typing import Optional
from modelo.barco import Barco
from modelo.partida.partida import Partida

class Controlador(ABC):

    @abstractmethod
    def iniciar_partida(self) -> None:
        pass


    @abstractmethod
    def crear_barcos(self) -> list[Barco]:
        pass
    
    
    @abstractmethod
    def crear_partida(self, dificultad: Optional[int] = None) -> Partida:
        pass
    
    
    @abstractmethod
    def ejecutar_bucle_principal(self) -> None:
        pass
    
    
    @abstractmethod
    def mostrar_estado(self) -> None:
        pass
    
    
    @abstractmethod
    def fase_turno(self) -> None:
        pass