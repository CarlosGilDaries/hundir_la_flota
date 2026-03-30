import random
from model.ship import Ship
from model.result import ShotResult
import copy


class Board:

    def __init__(self, width: int, height: int, ships: list[Ship], empty_character: str, hit_character: str, water_character: str) -> None:
        """
        Initializes a two-dimensional board.

        Args:
            width (int): Number of columns.
            height (int): Number of rows.
            ships (list[Ship]): List of Ship objects.
            empty_character (str): Character representing an empty space.
            hit_character (str): Character representing a successful shot.
            water_character (str): Character representing a missed shot.

        Returns:
            None
        """
        self.width = width
        self.height = height
        self.ships = ships
        self._empty_character = empty_character
        self._hit_character = hit_character
        self._water_character = water_character
        self._placed_ships_count = 0

        self.__cells = [
            [None for _ in range(width)]
            for _ in range(height)
        ]


    def get_all_cells(self) -> list[list[Ship | str | None]]:
        """
        Returns a copy of the private cells attribute.

        Returns:
            list[list[Ship|str|None]]: Board cells.
        """
        return copy.deepcopy(self.__cells)


    def get_cell(self, x: int, y: int) -> Ship | str | None:
        """
        Returns a copy of a specific cell.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            Ship|str|None: Content of the cell.
        """
        return copy.deepcopy(self.__cells[y][x])


    def view_board(self) -> list[list[str]]:
        """
        Returns a view of the board with ships visible.

        Returns:
            list[list[str]]: Matrix representing the board.
        """
        view = []

        for row in self.__cells:
            new_row = []
            for cell in row:
                if cell is None:
                    new_row.append(self._empty_character)
                elif isinstance(cell, Ship):
                    new_row.append(cell.character)
                else:
                    new_row.append(cell)

            view.append(new_row)

        return view


    def view_opponent_board(self) -> list[list[str]]:
        """
        Returns the board hiding ships, only showing shots.

        Returns:
            list[list[str]]: Matrix representing the opponent's board.
        """
        view = []

        for row in self.__cells:
            new_row = []
            for cell in row:
                if cell == self._hit_character or cell == self._water_character:
                    new_row.append(cell)
                else:
                    new_row.append(self._empty_character)

            view.append(new_row)

        return view


    def mark_shot(self, x: int, y: int, character: str) -> None:
        """
        Marks a shot at the indicated position on the board.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            character (str): Character representing the result of the shot.

        Returns:
            None
        """
        self.__cells[y][x] = character


    def place_ship_randomly(self, ship: Ship) -> bool:
        """
        Places a ship randomly on the board without overlaps.

        Args:
            ship (Ship): Ship to place.

        Returns:
            bool: True if placed successfully, False if placement failed.
        """
        max_attempts = 1000
        attempts = 0
        placed = False

        while not placed and attempts < max_attempts:
            attempts += 1
            ship.set_horizontal()

            max_x = ship.calculate_max_position(self.width)
            max_y = ship.calculate_max_position(self.height)

            pos_x = random.randint(0, max_x)
            pos_y = random.randint(0, max_y)

            if self._can_be_placed(ship, pos_x, pos_y):
                self._insert_ship_into_board(ship, pos_x, pos_y)
                placed = True
                self._placed_ships_count += 1

        return placed


    def place_ship_manually(self, ship: Ship, x: int, y: int) -> bool:
        """
        Places a ship at the manually indicated position.

        Args:
            ship (Ship): Ship to place.
            x (int): Starting X coordinate.
            y (int): Starting Y coordinate.

        Returns:
            bool: True if placed successfully, False if conflict.
        """
        if not self._can_be_placed(ship, x, y):
            return False

        self._insert_ship_into_board(ship, x, y)
        self._placed_ships_count += 1
        return True


    def _insert_ship_into_board(self, ship: Ship, x: int, y: int) -> None:
        """
        Inserts a ship into the board according to its orientation.

        Args:
            ship (Ship): Ship to place.
            x (int): Starting X coordinate.
            y (int): Starting Y coordinate.

        Returns:
            None
        """
        if ship.get_horizontal():
            for i in range(ship.size):
                self.__cells[y][x] = ship
                x += 1
        else:
            for i in range(ship.size):
                self.__cells[y][x] = ship
                y += 1


    def receive_shot(self, x: int, y: int) -> tuple[ShotResult, str]:
        """
        Processes a shot at the indicated position.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            tuple[ShotResult, str]: Result of the shot and content of the cell.
        """
        if not self._coordinates_valid(x, y):
            return [ShotResult.INVALID, ""]

        cell = self.__cells[y][x]

        # Already shot
        if cell == self._hit_character or cell == self._water_character:
            return [ShotResult.REPEATED, cell]

        # Hit on a ship
        if isinstance(cell, Ship):
            ship = cell
            ship.take_hit()
            self.__cells[y][x] = self._hit_character

            if ship.is_sunk():
                return [ShotResult.SUNK, self._hit_character]
            else:
                return [ShotResult.HIT, self._hit_character]

        # Water
        self.__cells[y][x] = self._water_character
        return [ShotResult.WATER, self._water_character]


    def all_sunk(self) -> bool:
        """
        Checks if all ships on the board have been sunk.

        Returns:
            bool: True if all ships are sunk, False otherwise.
        """
        return all(ship.is_sunk() for ship in self.ships)


    def _coordinates_valid(self, x: int, y: int) -> bool:
        """
        Validates if the coordinates are within the board and are integers.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            bool: True if coordinates are valid, False otherwise.
        """
        return (
            isinstance(x, int) and
            isinstance(y, int) and
            0 <= x < self.width and
            0 <= y < self.height
        )


    def _can_be_placed(self, ship: Ship, x: int, y: int) -> bool:
        """
        Checks if a ship can be placed at the indicated position.

        Args:
            ship (Ship): Ship to place.
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            bool: True if it can be placed, False if conflict or out of bounds.
        """
        # Starting coordinate valid
        if not self._coordinates_valid(x, y):
            return False

        for i in range(ship.size):
            if ship.get_horizontal():
                nx = x + i
                ny = y
            else:
                nx = x
                ny = y + i

            # Validate bounds
            if not self._coordinates_valid(nx, ny):
                return False

            # Validate overlap
            if self.__cells[ny][nx] is not None:
                return False

        return True


    def all_placed(self) -> bool:
        """
        Checks if all ships have been placed.

        Returns:
            bool: True if all are placed, False otherwise.
        """
        return self._placed_ships_count == len(self.ships)