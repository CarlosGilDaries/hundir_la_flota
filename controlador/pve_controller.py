from model.board import Board
from model.game.pve_game import PvEGame
from model.ship import Ship
from vista.consola.vista_consola import ConsoleView
from utils.excepciones import ReturnToMenu
from controlador.controller import Controller


class PvEController(Controller):
    def __init__(self, view: ConsoleView, config: dict) -> None:
        self._view = view
        self._config = config
        self._game: PvEGame | None = None
        self.difficulty_config = self._config["DIFFICULTY"]["PVE"]


    def start(self, difficulty: int) -> None:
        """
        Starts a new PvE game.

        Args:
            difficulty (int): Selected difficulty index.

        Returns:
            None
        """
        self._game = self.create_game(difficulty)
        self.run_main_loop()


    def create_ships(self, ships_config: list[tuple[str, int, str]]) -> list[Ship]:
        """
        Creates Ship objects from configuration.

        Args:
            ships_config (list[tuple[str, int, str]]): Ship configuration.

        Returns:
            list[Ship]: List of created Ship objects.
        """
        return [
            Ship(name, size, character)
            for name, size, character in ships_config
        ]


    def create_game(self, difficulty: int) -> PvEGame:
        """
        Creates the PvE game.

        Args:
            difficulty (int): Difficulty index.

        Returns:
            PvEGame: PvEGame object.
        """
        difficulty_config = self._config["DIFFICULTY"]["PVE"][difficulty]
        characters = self._config["CHARACTERS"]

        ships = self.create_ships(difficulty_config["ships"])

        board = Board(
            difficulty_config["width"],
            difficulty_config["height"],
            ships,
            characters["EMPTY_CHARACTER"],
            characters["HIT_CHARACTER"],
            characters["WATER_CHARACTER"]
        )

        return PvEGame(
            board,
            difficulty_config["shots"]
        )


    def run_main_loop(self) -> None:
        """
        Executes the main loop of the PvE game.

        Returns:
            None
        """
        try:
            self._view.clear_console()

            while self._game.has_shots_left() and not self._game.check_victory():
                self.display_state()
                self.turn_phase()

            self.display_state()
            self._view.display_final_message(
                self._game.check_victory(),
                False
            )

        except ReturnToMenu:
            self._view.clear_console()


    def display_state(self) -> None:
        """
        Displays the board and remaining shots.

        Returns:
            None
        """
        self._view.display_board(
            self._game.get_opponent_board()
        )
        self._view.display_remaining_shots(
            self._game.remaining_shots()
        )


    def turn_phase(self) -> None:
        """
        Executes the logic of a player turn.

        Returns:
            None
        """
        width, height = self._game.get_board_dimensions()
        self._view.show_return_to_menu_option()
        x, y = self._view.request_shot(width, height)
        result = self._game.shoot(x, y)
        self._view.clear_console()
        self._view.display_shot_result(result)