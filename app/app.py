from vista.consola.vista_pve import InterfazConsola
from vista.consola.menu_pve import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma
from config.mensajes import TEXTOS, INSTRUCCIONES
import asyncio
from red.cliente import ClientePVP
from controlador.controlador_pve import ControladorPVE


class App:

    def __init__(self) -> None:
        """
        Inicializa la aplicación.
        """
        validador = Util()
        self._interfaz = InterfazConsola(TEXTOS, validador)
        self._menu = Menu(self._interfaz, INSTRUCCIONES)
        self.controlador_pve = ControladorPVE(self._interfaz, self._menu)


    def ejecutar(self) -> None:
        """
        Inicia la ejecución de la aplicación.
        """
        try:
            while True:
                opcion = self._menu.ejecutar_menu_principal()
                if opcion in [1, 2, 3]:
                    dificultad = opcion
                    partida_pve = self.controlador_pve.crear_partida(dificultad)
                    self.controlador_pve.ejecutar_partida(partida_pve)
                elif opcion == 4:
                    self._iniciar_cliente_pvp()
                    # próximamente partida_pvp = self.controlador_pvp.crear_partida()
                    # próximamente self.controlador_pvp(ejecutar_partida(partida_pvp))
        except SalirDelPrograma:
            self._interfaz.fin_programa()
            
            
    def _iniciar_cliente_pvp(self) -> None:
        """
        Inicia el cliente para partida PvP.
        """
        try:          
            cliente = ClientePVP()           
            # Ejecutar el cliente de forma asíncrona
            asyncio.run(cliente.ejecutar())
            
        except KeyboardInterrupt:
            self._interfaz.mostrar_mensaje("\nConexión cancelada por el usuario")
        except Exception as e:
            self._interfaz.mostrar_mensaje(f"Error en la conexión: {e}")
        finally:
            input("\nPresiona Enter para volver al menú principal...")
            self._interfaz.borrar_consola()