from utils.exceptions import ExitProgram
from view.console.console_view import ConsoleView
from config.constants import CONSTANTS


class Menu:
    """
    Menu class that presents options for the user to interact with the game.
    """

    def __init__(self, interface: ConsoleView, instructions: str) -> None:
        """
        Initializes a menu with options for user interaction.

        Args:
            interface (ConsoleView): ConsoleView object.
            instructions (str): Game instructions.
        """
        self._interface = interface
        self._instructions = instructions


    def execute_main_menu(self, difficulties: list[int]) -> int:
        """
        Executes the main menu of the game.
        The menu is displayed repeatedly until the user
        chooses to start a game or exit the program.

        Args:
            difficulties (list[int]): List of difficulty indices available for PvE mode.

        Returns:
            int:
                - integer within difficulty range → selected difficulty for PvE mode
                - integer outside difficulty range → start PvP mode

        Raises:
            ExitProgram: If the user chooses to exit.
        """
        self._interface.clear_console()
        while True:
            option = self._main_menu()

            match option:
                case "1":
                    return self.execute_difficulty_menu(difficulties)
                case "2":
                    return len(difficulties) + 1
                case "3":
                    self._interface.display_instructions(self._instructions)
                case "4":
                    raise ExitProgram()
                case _:
                    self._interface.clear_console()
                    print(self._interface.get_text("ERROR_MENU"))


    def execute_difficulty_menu(self, difficulties: list[int]) -> int:
        """
        Executes the difficulty menu.

        Args:
            difficulties (list[int]): List of difficulty indices available for PvE mode.

        Returns:
            int: The number corresponding to the selected option.
        """
        self._interface.clear_console()
        while True:
            option = self._difficulty_menu()

            if option.isdigit() and int(option) in difficulties:
                return int(option)

            self._interface.clear_console()
            print(self._interface.get_text("ERROR_MENU"))


    def _main_menu(self) -> str:
        """
        Displays the main menu options and asks the user for an option.

        Returns:
            str: Number entered by the user via keyboard.
        """
        print("")
        print("HUNDIR LA FLOTA")
        print("")
        print("1. Jugar contra la Máquina (PVE)")
        print("2. Jugar contra otro/a Jugador/a (PVP)")
        print("3. Instrucciones")
        print("4. Salir")
        print("")
        return input("Introduzca el número correspondiente a la opción deseada: ")


    def _difficulty_menu(self) -> str:
        """
        Displays the difficulty options.

        Returns:
            str: Option entered by the user.
        """
        print("")
        print("Dificultad")
        print("")

        for num, difficulty in CONSTANTS["DIFFICULTY"]["PVE"].items():
            print(f"{num}. {difficulty['name']}")

        print("")
        return input("Introduzca el número correspondiente a la opción deseada: ")