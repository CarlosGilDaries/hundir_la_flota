from view.console.console_view import ConsoleView
from view.console.console_menu import Menu
from utils.utils import Util
from utils.exceptions import ExitProgram
from config.texts import TEXTS, INSTRUCTIONS
from config.constants import CONSTANTS
import asyncio
from controller.pve_controller import PvEController
from controller.pvp_client_controller import PvPClientController
from net.client.client_socket import ClientSocket


class App:
    """
    Main application class.
    """

    def __init__(self) -> None:
        """
        Initializes the application.
        """
        validator = Util()
        self._interface = ConsoleView(TEXTS, validator)
        self._menu = Menu(self._interface, INSTRUCTIONS)
        self._pve_controller = PvEController(self._interface, CONSTANTS)


    def run(self) -> None:
        """
        Starts the application execution.
        """
        try:
            pve_difficulties = []
            for key in self._pve_controller.difficulty_config.keys():
                pve_difficulties.append(int(key))

            while True:
                option = self._menu.execute_main_menu(pve_difficulties)

                if option in pve_difficulties:
                    difficulty = option
                    self._pve_controller.start(difficulty)

                elif option == len(pve_difficulties) + 1:
                    self._start_pvp_client()

        except ExitProgram:
            pass

        except KeyboardInterrupt:
            pass

        finally:
            self._interface.exit_program()


    def _start_pvp_client(self) -> None:
        """
        Starts a PvP game.
        """
        client = None
        try:
            asyncio.run(self._run_pvp())

        except KeyboardInterrupt:
            self._interface.display_message("\nConexión cancelada por el usuario")
            if client:
                asyncio.run(client.disconnect())

        except Exception as e:
            self._interface.display_message(f"Error en la conexión: {e}")
            asyncio.run(asyncio.sleep(5))
            if client:
                asyncio.run(client.disconnect())


    async def _run_pvp(self):
        client = ClientSocket("127.0.0.1", 8888)

        controller = PvPClientController(
            client,
            self._interface
        )

        await controller.start()