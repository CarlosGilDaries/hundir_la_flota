from abc import ABC, abstractmethod


class Controller(ABC):
    """
    Base interface for all game controllers.
    """

    @abstractmethod
    def start(self, *args, **kwargs) -> None:
        """
        Starts the controller.

        Each game mode implements its own logic.

        Returns:
            None
        """
        pass