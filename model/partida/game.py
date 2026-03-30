from abc import ABC, abstractmethod
from typing import Optional
from model.ship import Ship
from model.result import ShotResult


class Game(ABC):
    """
    Abstract class that defines the common contract for any type of game.

    Concrete implementations (PVE or PVP) must provide logic for shots,
    ship placement, and obtaining boards.
    """


    @abstractmethod
    def shoot(self, x: int, y: int) -> ShotResult:
        """
        Performs a shot at the indicated position.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            ShotResult: Result of the shot.
        """
        pass


    @abstractmethod
    def get_own_board(self, player: Optional[int] = None) -> list[list[str]]:
        """
        Gets the player's own board.

        Args:
            player (Optional[int], optional): Player identifier in PVP games.

        Returns:
            list[list[str]]: Representation of the own board.
        """
        pass


    @abstractmethod
    def get_opponent_board(self, player: Optional[int] = None) -> list[list[str]]:
        """
        Gets the opponent's board visible to the player.

        Args:
            player (Optional[int], optional): Player identifier in PVP games.

        Returns:
            list[list[str]]: Representation of the opponent's board.
        """
        pass


    @abstractmethod
    def place_ship(self, ship: Ship, x: Optional[int] = None, y: Optional[int] = None,
                   horizontal: Optional[bool] = None, player: Optional[int] = None) -> bool:
        """
        Places a ship on the board.

        Args:
            ship (Ship): Ship to be placed.
            x (Optional[int]): Starting X coordinate.
            y (Optional[int]): Starting Y coordinate.
            horizontal (Optional[bool]): Orientation of the ship.
            player (Optional[int]): Player identifier in PVP.

        Returns:
            bool: True if placement was successful, False otherwise.
        """
        pass


    @abstractmethod
    def check_victory(self) -> bool:
        """
        Checks if the game has ended with a victory.

        Returns:
            bool: True if there is a winner, False otherwise.
        """
        pass