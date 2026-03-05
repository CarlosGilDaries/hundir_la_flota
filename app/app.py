from vista.consola.vista_consola import VistaConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma
from config.mensajes import TEXTOS, INSTRUCCIONES
from config.constantes import CONSTANTES
import asyncio
#from red.cliente1 import ClientePVP
from controlador.controlador_pve import ControladorPVE
from controlador.controlador_pvp_cliente import ControladorPVPCliente
from cliente.cliente_socket import ClienteSocket


class App:

    def __init__(self) -> None:
        """
        Inicializa la aplicación.
        """
        validador = Util()
        self._interfaz = VistaConsola(TEXTOS, validador)
        self._menu = Menu(self._interfaz, INSTRUCCIONES)
        self.controlador_pve = ControladorPVE(self._interfaz, CONSTANTES)


    def ejecutar(self) -> None:
        """
        Inicia la ejecución de la aplicación.
        """
        try:
            while True:
                opcion = self._menu.ejecutar_menu_principal()
                if opcion in [1, 2, 3]:
                    dificultad = opcion
                    self.controlador_pve.iniciar(dificultad)
                elif opcion == 4:
                    self._iniciar_cliente_pvp()
        except SalirDelPrograma:
            self._interfaz.fin_programa()
            
            
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
            if cliente:
                asyncio.run(cliente.desconectar())

        finally:
            input("\nPresiona Enter para volver al menú principal...")
            self._interfaz.borrar_consola()
            
            
    async def _ejecutar_pvp(self):
        cliente = ClienteSocket("localhost", 8888)

        controlador = ControladorPVPCliente(
            cliente,
            self._interfaz
        )

        try:
            await controlador.iniciar()
        except asyncio.CancelledError:
            # Tarea cancelada, cerrar socket
            await cliente.desconectar()
        finally:
            # Asegurarse de cerrar la conexión aunque se salga de la partida
            await cliente.desconectar()