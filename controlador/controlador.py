from abc import ABC, abstractmethod

class Controlador(ABC):

    @abstractmethod
    def crear_partida(self):
        pass


    @abstractmethod
    def ejecutar_partida(self):
        pass
    
    