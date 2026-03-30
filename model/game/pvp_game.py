from model.game.game import Game
from model.board import Board
from model.ship import Ship
from model.result import ShotResult
from enum import Enum
import random


class GameState(Enum):
    """
    Possible states of a PVP game.
    """
    PLACEMENT = "placement"
    PLAYING = "playing"
    FINISHED = "finished"


class PvPGame(Game):
    """
    Implementation of a game between two players (PVP).
    """

    def __init__(self, player1_board: Board, player2_board: Board) -> None:
        """
        Initializes a PVP game.

        Args:
            player1_board (Board): Board of player 1.
            player2_board (Board): Board of player 2.
        """
        self._boards = {
            1: player1_board,
            2: player2_board
        }

        self._turn = 1
        self._state = GameState.PLACEMENT

        self._ready_players = set()


    def shoot(self, player: int, x: int, y: int) -> ShotResult:
        """
        Performs a shot on the opponent's board.

        Args:
            player (int): Player who shoots.
            x (int): X coordinate.
            y (int): Y coordinate.

        Raises:
            ValueError: If it is not the player's turn.

        Returns:
            ShotResult: Result of the shot.
        """
        if player != self._turn or self.state() != GameState.PLAYING:
            raise ValueError("It's not your turn to shoot")

        defender = self._opponent(player)

        result, _ = self._boards[defender].receive_shot(x, y)

        if self._boards[defender].all_sunk():
            self._state = GameState.FINISHED
        else:
            self._turn = defender

        return result


    def get_own_board(self, player: int) -> list[list[str]]:
        """
        Returns the player's own board.

        Args:
            player (int): Player identifier.

        Returns:
            list[list[str]]: Player's full board.
        """
        return self._boards[player].view_board()


    def get_opponent_board(self, player: int) -> list[list[str]]:
        """
        Returns the opponent's visible board.

        Args:
            player (int): Player identifier.

        Returns:
            list[list[str]]: Opponent's board with ships hidden.
        """
        opponent = self._opponent(player)
        return self._boards[opponent].view_opponent_board()


    def place_ship(self, ship: Ship, x: int, y: int, horizontal: bool, player: int) -> bool:
        """
        Places a ship on the player's board.

        Args:
            ship (Ship): Ship to place.
            x (int): Starting X coordinate.
            y (int): Starting Y coordinate.
            horizontal (bool): Orientation of the ship.
            player (int): Player identifier.

        Returns:
            bool: True if placement was successful, False otherwise.
        """
        board = self._boards[player]
        ship.set_horizontal(horizontal)
        placed = board.place_ship_manually(ship, x, y)

        if placed:
            if board.all_placed():
                self._ready_players.add(player)

                if len(self._ready_players) == 2:
                    self._state = GameState.PLAYING
                    self._turn = self._randomize_turn()

        return placed


    def check_victory(self) -> bool:
        """
        Indicates whether the game has ended.

        Returns:
            bool: True if the game is finished.
        """
        return self._state == GameState.FINISHED


    def state(self) -> GameState:
        """
        Returns the current state of the game.

        Returns:
            GameState: Current state.
        """
        return self._state


    def current_turn(self) -> int:
        """
        Returns the player whose turn it is to attack.

        Returns:
            int: Current player.
        """
        return self._turn


    def winning_player(self) -> int | None:
        """
        Determines the winning player.

        Returns:
            int | None: Winning player or None if there is no winner yet.
        """
        if self._state != GameState.FINISHED:
            return None

        for player in (1, 2):
            if self._boards[self._opponent(player)].all_sunk():
                return player

        return None


    def _opponent(self, player: int) -> int:
        """
        Returns the identifier of the opponent player.

        Args:
            player (int): Current player.

        Returns:
            int: Opponent player.
        """
        return 2 if player == 1 else 1


    def _randomize_turn(self) -> int:
        """
        Randomizes the first turn so that it is random who starts.

        Returns:
            int: 1 if player 1 starts, 2 if player 2 starts.
        """
        return random.randint(1, 2)