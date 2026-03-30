from model.game.game import Game
from model.result import ShotResult
from model.board import Board
from model.ship import Ship
from typing import Optional


class PvEGame(Game):
    """
    Implementation of a game against the machine (PvE).
    """

    def __init__(self, machine_board: Board, max_shots: int, ships_placed: Optional[bool] = None) -> None:
        """
        Initializes a new PvE game.

        Args:
            machine_board (Board): Board where the machine's ships are placed.
            max_shots (int): Maximum number of shots allowed.
            ships_placed (bool): Optional flag to skip automatic ship placement, only for testing.
        """
        self.machine_board = machine_board
        self._max_shots = max_shots
        self._shots_fired = 0

        if not ships_placed:
            self._place_ships_automatically()


    def shoot(self, x: int, y: int) -> ShotResult:
        """
        Performs a shot on the machine's board.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            ShotResult: Result of the shot.
        """
        [result, _] = self.machine_board.receive_shot(x, y)
        if result != ShotResult.REPEATED and result != ShotResult.INVALID:
            self._shots_fired += 1

        return result


    def get_own_board(self, player: Optional[int] = None) -> list[list[str]]:
        """
        Returns the full board of the machine.

        Used mainly for debugging.

        Returns:
            list[list[str]]: Board with ships visible.
        """
        return self.machine_board.view_board()


    def get_opponent_board(self, player: Optional[int] = None) -> list[list[str]]:
        """
        Returns the board visible to the player.

        Returns:
            list[list[str]]: Board with ships hidden.
        """
        return self.machine_board.view_opponent_board()


    def place_ship(self, ship: Ship, x: Optional[int] = None, y: Optional[int] = None,
                   horizontal: Optional[bool] = None, player: Optional[int] = None) -> bool:
        """
        Places a ship automatically on the board.

        Args:
            ship (Ship): Ship to place.
            x (Optional[int]): Ignored in this implementation.
            y (Optional[int]): Ignored in this implementation.
            horizontal (Optional[bool]): Ignored in this implementation.
            player (Optional[int]): Ignored in this implementation.

        Returns:
            bool: True if placement was successful, False otherwise.
        """
        return self.machine_board.place_ship_randomly(ship)


    def check_victory(self) -> bool:
        """
        Checks if all ships have been sunk.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        return self.machine_board.all_sunk()


    def has_shots_left(self) -> bool:
        """
        Checks if there are remaining shots.

        Returns:
            bool: True if shots are still available.
        """
        return self._shots_fired < self._max_shots


    def remaining_shots(self) -> int:
        """
        Calculates the number of shots left.

        Returns:
            int: Number of remaining shots.
        """
        return self._max_shots - self._shots_fired


    def get_board_dimensions(self) -> tuple[int, int]:
        """
        Returns the dimensions of the board.

        Returns:
            tuple[int, int]: Width and height of the board.
        """
        return self.machine_board.width, self.machine_board.height


    def _place_ships_automatically(self) -> None:
        """
        Automatically places all ships on the board.

        Raises:
            RuntimeError: If any ship cannot be placed.
        """
        for ship in self.machine_board.ships:
            placed = self.place_ship(ship)
            if not placed:
                raise RuntimeError(f"Could not place ship {ship.name}.")