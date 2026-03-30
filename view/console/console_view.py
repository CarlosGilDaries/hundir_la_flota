# view/console/console_view.py

from utils.utils import Util
from utils.exceptions import ReturnToMenu
from model.result import ShotResult
from view.view import View
import os


class ConsoleView(View):
    """
    Console-based implementation of the view.
    """

    def __init__(self, texts: dict, validator: Util) -> None:
        """
        Initializes the console view.

        Args:
            texts (dict): Texts stored as key-value pairs in config/texts.
            validator (Util): Validator from the Util class.
        """
        self._texts = texts
        self._validator = validator


    def request_shot(self, width: int, height: int) -> tuple[int, int]:
        """
        Asks the user for the shot coordinates.
        Allows typing 'salir' to exit the game.

        Args:
            width (int): Board width.
            height (int): Board height.

        Returns:
            tuple[int, int]: X and Y coordinates entered by the user.
        """
        x = self.request_coordinate("x", width - 1)
        y = self.request_coordinate("y", height - 1)
        return x, y


    def request_coordinate(self, axis: str, limit: int) -> int:
        """
        Asks the user for a valid coordinate.
        'Salir' is the value set to exit the program.

        Args:
            axis (str): Axis ('x' or 'y').
            limit (int): Maximum allowed value.

        Raises:
            ReturnToMenu: If the user selects the exit option.

        Returns:
            int: Valid coordinate.
        """
        valid = False
        while not valid:
            value = input(self._texts[f"POSITION_{axis.upper()}"])
            print("")

            if value.lower() == "salir":
                raise ReturnToMenu()

            if not self._validator.is_integer(value):
                print(self._texts["ERROR_INTEGER"])
                print("")
                continue

            if not self._validator.is_valid_option(value, limit):
                print(self._texts["ERROR_BOARD_LIMIT"])
                print("")
                continue

            valid = True
            return int(value)


    def show_return_to_menu_option(self) -> None:
        """
        Displays the text with the option to return to the menu.
        """
        print("")
        print(self._texts["EXIT_PROMPT"])
        print("")


    def display_shot_result(self, result_enum: ShotResult) -> None:
        """
        Displays the result of a shot.

        Args:
            result_enum (ShotResult): Result of the shot.
        """
        print("")
        result = self.adapt_result_to_string(result_enum)
        print(self._texts[f"{result}"])
        print("")


    def display_board(self, board: list) -> None:
        """
        Displays the game board with row and column indices.

        The board is printed in matrix format:
        - The first line shows the column indices.
        - Each row is printed preceded by its corresponding index.

        Args:
            board (list): List of lists with the board characters.
        """
        height = len(board)
        width = len(board[0])

        # Show header with X coordinates
        header = "   " + " ".join(str(i) for i in range(width))
        print(header)

        # Show each row with its Y coordinate
        for i in range(height):
            row = board[i]
            row_str = f"{i:<2} " + " ".join(row)
            print(row_str)


    def display_final_message(self, victory: bool, pvp: bool) -> None:
        """
        Displays the final message of the game.

        Args:
            victory (bool): Indicates whether the player has won.
            pvp (bool): Indicates whether the game is PvE (False) or PvP (True).
        """
        if victory:
            print("")
            print(self._texts["VICTORY"])
        else:
            print("")
            print(self._texts["DEFEAT"])

        if not pvp:
            input(self._texts["PRESS_ENTER"])


    def display_abandon_message(self, abandon: bool) -> None:
        """
        Displays the final message if the opponent has abandoned.

        Args:
            abandon (bool): Indicates whether the opponent has abandoned.
        """
        if abandon:
            print("")
            print(self._texts["PVP_ABANDON"])


    def exit_program(self) -> None:
        """
        Displays the program end text.
        """
        print("")
        print(self._texts["END_OF_PROGRAM"])
        print("")


    def display_remaining_shots(self, remaining: int) -> None:
        """
        Displays the remaining shots.

        Args:
            remaining (int): Number of remaining shots.
        """
        print("")
        print(self._texts["REMAINING_SHOTS"], remaining)


    def get_text(self, key: str) -> str:
        """
        Returns the text corresponding to the key.

        Args:
            key (str): Text key.

        Returns:
            str: Associated text.
        """
        return self._texts.get(key, f"[Text not found: {key}]")


    def display_message(self, message: str) -> None:
        """
        Displays the message passed as a parameter.

        Args:
            message (str): Message to display.
        """
        print(message)


    def display_instructions(self, instructions: str) -> None:
        """
        Displays the game instructions.

        Args:
            instructions (str): Game instructions.
        """
        self.clear_console()
        print(instructions)
        input()
        self.clear_console()


    def clear_console(self) -> None:
        """
        Clears the console screen.

        Uses ANSI sequences and the corresponding operating system command
        to ensure cross-platform compatibility.
        """
        # \033[2J → clears the whole screen
        # \033[H → moves cursor to (0,0)
        print("\033[2J\033[H", end="")
        os.system('cls' if os.name == 'nt' else 'clear')


    def display_boards(self, own: list[list[str]], opponent: list[list[str]]) -> None:
        """
        Displays simultaneously the player's board and the opponent's board,
        including X and Y coordinates as headers.

        Args:
            own (list[list[str]]): Player's board.
            opponent (list[list[str]]): Visible opponent's board.
        """
        height = len(own)
        width = len(own[0])

        # Calculate the width of each printed board
        # Format: "Y " (3 characters) + numbers with spaces
        printed_board_width = 3 + (width * 2 - 1)
        spacer = 5

        print()

        # Show titles centered above the boards
        own_title = "Tu tablero"
        opponent_title = "Tablero rival"
        title_line = own_title.ljust(printed_board_width) + (" " * spacer) + opponent_title
        print(f"{title_line}\n")

        # Show X headers
        header = "   " + " ".join(str(i) for i in range(width))
        header_line = header.ljust(printed_board_width) + (" " * spacer) + header
        print(header_line)

        # Show rows with Y indices
        for i in range(height):
            row_own = own[i]
            row_opponent = opponent[i]

            row_str_own = f"{i:<2} " + " ".join(row_own)
            row_str_opponent = f"{i:<2} " + " ".join(row_opponent)

            line = row_str_own.ljust(printed_board_width) + (" " * spacer) + row_str_opponent
            print(line)