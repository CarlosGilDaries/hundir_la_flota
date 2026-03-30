from view.console.console_view import ConsoleView
from view.console.console_menu import Menu
from utils.utils import Util
from utils.exceptions import ExitProgram
from config.texts import TEXTS, INSTRUCTIONS
from config.constants import CONSTANTS
import asyncio
from controller.pve_controller import PvEController
from controller.controlador_pvp_cliente import ControladorPVPCliente
from red.cliente.cliente_socket import ClienteSocket


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
            
            
    def _iniciar_cliente_pvp(self) -> None:
        """
        Inicia una partida PvP.
        """
        cliente = None
        try:

            asyncio.run(self._ejecutar_pvp())

        except KeyboardInterrupt:
            self._interfaz.mostrar_mensaje("\nConexión cancelada por el usuario")
            if cliente:
                asyncio.run(cliente.desconectar())
                
        except Exception as e:
            self._interfaz.mostrar_mensaje(f"Error en la conexión: {e}")
            asyncio.run(asyncio.sleep(5))
            if cliente:
                asyncio.run(cliente.desconectar())
            
            
    async def _ejecutar_pvp(self):
        cliente = ClienteSocket("127.0.0.1", 8888)

        controlador = ControladorPVPCliente(
            cliente,
            self._interfaz
        )

        await controlador.iniciar()