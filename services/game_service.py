from model.board import Board
from model.ship import Ship
from model.game.pvp_game import PvPGame, GameState
from model.result import ShotResult
from typing import Any


class GameService:
    """
    Application layer that manages the logic of a PvP game.
    This class acts as an intermediary between the network server
    and the domain model of the game. It is responsible for setting up
    the game, managing ship placement, processing shots, and exposing
    the game state to the server.
    """

    def __init__(self, config: dict[str, Any], characters: dict[str, str]) -> None:
        """
        Initializes the game service.
        Creates the ships for each player and sets up the game with
        the corresponding boards.

        Args:
            config (dict[str, Any]): General game configuration.
                Must contain:
                    - width (int)
                    - height (int)
                    - ships (list)
            characters (dict[str, str]): Dictionary with the characters
                used to represent the board.
        """
        self.config = config
        self.characters = characters

        self.player1_ships = self._create_ships(config["ships"])
        self.player2_ships = self._create_ships(config["ships"])

        self._remaining_ships = {
            1: self.player1_ships.copy(),
            2: self.player2_ships.copy()
        }

        self._create_game()


    def _create_game(self) -> None:
        """
        Initializes the boards and creates the PvP game instance.

        Returns:
            None
        """
        board1 = Board(
            self.config["width"],
            self.config["height"],
            self.player1_ships,
            self.characters["EMPTY_CHARACTER"],
            self.characters["HIT_CHARACTER"],
            self.characters["WATER_CHARACTER"]
        )

        board2 = Board(
            self.config["width"],
            self.config["height"],
            self.player2_ships,
            self.characters["EMPTY_CHARACTER"],
            self.characters["HIT_CHARACTER"],
            self.characters["WATER_CHARACTER"]
        )

        self._game = PvPGame(board1, board2)


    def _create_ships(self, ships_config: list[tuple[str, int, str]]) -> list[Ship]:
        """
        Creates the list of ships from the configuration.

        Args:
            ships_config (list[tuple[str, int, str]]):
                List of ship definitions where each element contains:
                    - name (str)
                    - size (int)
                    - character (str)

        Returns:
            list[Ship]: List of ship instances.
        """
        return [
            Ship(name, size, character)
            for name, size, character in ships_config
        ]


    def state(self) -> GameState:
        """
        Returns the current state of the game.

        Returns:
            GameState: Current game state.
        """
        return self._game.state()


    def current_turn(self) -> int:
        """
        Returns the player who has the current turn.

        Returns:
            int: Player identifier (1 or 2).
        """
        return self._game.current_turn()


    def remaining_ships(self, player: int) -> list[dict[str, Any]]:
        """
        Gets the list of ships that the player still needs to place.

        Args:
            player (int): Player identifier (1 or 2).

        Returns:
            list[dict[str, Any]]: List of pending ships with their information:
                - index (int)
                - name (str)
                - size (int)
        """
        ships = []

        for i, ship in enumerate(self._remaining_ships[player], start=1):
            ships.append({
                "index": i,
                "name": ship.name,
                "size": ship.size
            })

        return ships


    def place_ship(self, player: int, index: int, x: int, y: int, horizontal: bool) -> bool:
        """
        Attempts to place a ship on the player's board.
        If placement is valid, the ship is removed from the pending list.

        Args:
            player (int): Player identifier.
            index (int): Index of the selected ship.
            x (int): Horizontal coordinate.
            y (int): Vertical coordinate.
            horizontal (bool): Ship orientation.

        Returns:
            bool: True if the ship was placed correctly, False otherwise.

        Raises:
            ValueError: If the ship index is invalid.
        """
        pending = self._remaining_ships[player]

        if index < 1 or index > len(pending):
            raise ValueError("Invalid selection")

        ship = pending[index - 1]

        placed = self._game.place_ship(
            ship,
            x,
            y,
            horizontal,
            player
        )

        if placed:
            pending.remove(ship)

        return placed


    def shoot(self, player: int, x: int, y: int) -> ShotResult:
        """
        Executes a shot on the opponent's board.

        Args:
            player (int): Player making the shot.
            x (int): Horizontal coordinate.
            y (int): Vertical coordinate.

        Returns:
            ShotResult: Result of the shot (water, hit, or sunk).
        """
        return self._game.shoot(player, x, y)


    def get_boards_state(self, player: int) -> dict[str, Any]:
        """
        Gets the state of the boards from the player's perspective.
        Includes the player's own full board and the visible information
        of the opponent's board.

        Args:
            player (int): Player identifier.

        Returns:
            dict[str, Any]: Dictionary with:
                - own: state of the player's board
                - opponent: visible state of the opponent's board
        """
        return {
            "own": self._game.get_own_board(player),
            "opponent": self._game.get_opponent_board(player)
        }


    def check_victory(self) -> bool:
        """
        Indicates whether the game has ended with a winner.

        Returns:
            bool: True if there is a winner, False otherwise.
        """
        return self._game.check_victory()


    def winning_player(self) -> int | None:
        """
        Returns the winning player of the game.

        Returns:
            int | None:
                - 1 or 2 if there is a winner
                - None if the game has not yet ended
        """
        return self._game.winning_player()