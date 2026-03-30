from abc import ABC, abstractmethod
from model.result import ShotResult
from config.texts import TRANSLATION


class View(ABC):
    """
    Abstract class that defines the interface for system views.
    The view is exclusively responsible for user interaction,
    displaying information and requesting input when necessary.
    Concrete implementations (e.g., console or web) must
    implement all abstract methods defined here.
    """

    def adapt_result_to_string(self, result: ShotResult) -> str:
        """
        Converts a shot result (enum) to its textual representation.

        Args:
            result (ShotResult): Result of the shot.

        Returns:
            str: String associated with the result.
        """
        return TRANSLATION[result]


    @abstractmethod
    def request_shot(self, width: int, height: int) -> tuple[int, int]:
        """
        Asks the user for the coordinates of a shot.

        Args:
            width (int): Width of the board.
            height (int): Height of the board.

        Returns:
            tuple[int, int]: Shot coordinates (x, y).
        """
        pass


    @abstractmethod
    def request_coordinate(self, axis: str, limit: int) -> int:
        """
        Asks the user for a valid coordinate.

        Args:
            axis (str): Name of the axis ("x" or "y").
            limit (int): Maximum allowed value.

        Returns:
            int: Entered coordinate.
        """
        pass


    @abstractmethod
    def show_return_to_menu_option(self) -> None:
        """
        Displays the option to return to the main menu.
        """
        pass


    @abstractmethod
    def display_shot_result(self, result_enum: ShotResult) -> None:
        """
        Displays the result of a shot.

        Args:
            result_enum (ShotResult): Result of the shot.
        """
        pass


    @abstractmethod
    def display_board(self, board: list[list[str]]) -> None:
        """
        Displays a game board.

        Args:
            board (list[list[str]]): Board representation.
        """
        pass


    @abstractmethod
    def display_final_message(self, victory: bool, pvp: bool) -> None:
        """
        Displays the final message of the game.

        Args:
            victory (bool): Indicates whether the player has won.
            pvp (bool): Indicates whether it is a player versus player game.
        """
        pass


    @abstractmethod
    def get_text(self, key: str) -> str:
        """
        Returns a text associated with a key.

        Args:
            key (str): Key of the text.

        Returns:
            str: Corresponding text.
        """
        pass


    @abstractmethod
    def display_message(self, message: str) -> None:
        """
        Displays a message to the user.

        Args:
            message (str): Message to display.
        """
        pass