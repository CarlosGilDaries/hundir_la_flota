from abc import ABC, abstractmethod


class Controlador(ABC):
    """
    Interfaz base para todos los controladores del juego.
    """

    @abstractmethod
    def iniciar(self, *args, **kwargs) -> None:
        """
        Inicia el controlador.

        Cada modo de juego implementa su propia lógica.

        Returns:
            None
        """
        pass
