import random
from typing import Optional


class Ship:
    """
    Represents a ship in the game.
    """

    def __init__(self, name: str, size: int, character: str, horizontal: Optional[bool] = None) -> None:
        """
        Initializes a ship with a given size and random orientation.
        Remaining life equals the size and decreases by 1 with each hit received.

        Args:
            name (str): Name of the ship.
            size (int): Size of the ship.
            character (str): Character representing the ship.
            horizontal (Optional[bool], optional): Indicates if the ship is horizontal (True) or vertical (False).
                If not provided, it is generated randomly. Defaults to None.

        Returns:
            None
        """
        self.name = name
        self.size = size
        self.character = character
        self._remaining_health = size
        if horizontal is not None:
            self._horizontal = horizontal
        else:
            self.set_horizontal()


    def set_horizontal(self, horizontal: Optional[bool] = None) -> None:
        """
        Determines whether the ship's orientation is horizontal or vertical.
        For PvE it is random; for PvP it can be specified manually.

        Args:
            horizontal (Optional[bool], optional): Orientation chosen by the user. Defaults to None.

        Returns:
            None
        """
        if horizontal is not None:
            self._horizontal = horizontal
        else:
            self._horizontal = random.choice([True, False])


    def get_horizontal(self) -> bool:
        """
        Returns the orientation of the ship.

        Returns:
            bool: True if the ship is horizontal, False if vertical.
        """
        return self._horizontal


    def calculate_max_position(self, dimension: int) -> int:
        """
        Calculates the maximum position where the ship can be placed on a given axis.

        Args:
            dimension (int): Total dimension of the axis.

        Returns:
            int: Maximum allowed position for the ship.
        """
        return dimension - self.size


    def take_hit(self) -> None:
        """
        Reduces the ship's remaining health by one.
        """
        self._remaining_health -= 1


    def is_sunk(self) -> bool:
        """
        Checks whether the ship has been sunk.

        Returns:
            bool: True if the ship has no remaining health, False otherwise.
        """
        return self._remaining_health == 0