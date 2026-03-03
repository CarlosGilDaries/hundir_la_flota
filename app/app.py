from vista.consola.interfaz_consola import InterfazConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma
from config.mensajes import TEXTOS, INSTRUCCIONES
import asyncio
from red.cliente import ClientePVP
from controladores.controlador_pve import ControladorPVE


class App:

    def __init__(self):
        """
        Inicializa la aplicación.
        """
        validador = Util()
        self._interfaz = InterfazConsola(TEXTOS, validador)
        self._menu = Menu(self._interfaz, INSTRUCCIONES)
        self.controlador_pve = ControladorPVE()


    def ejecutar(self):
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
        except SalirDelPrograma:
            self._interfaz.fin_programa()
            
            
    def _iniciar_cliente_pvp(self):
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