from abc import ABC, abstractmethod

class Controlador(ABC):

    @abstractmethod
    def iniciar_partida(self):
        pass


    @abstractmethod
    def crear_barcos(self):
        pass