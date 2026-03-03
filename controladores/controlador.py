from dominio.resultado import ResultadoDisparo
from config.mensajes import TRADUCCION
from abc import ABC, abstractmethod

class Controlador(ABC):

    @abstractmethod
    def crear_partida(self):
        pass


    @abstractmethod
    def ejecutar_partida(self):
        pass
    
    
    def adaptar_resultado_a_string(self, resultado: ResultadoDisparo) -> str:
        return TRADUCCION[resultado]