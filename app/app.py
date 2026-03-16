from vista.consola.vista_consola import VistaConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma
from config.textos import TEXTOS, INSTRUCCIONES
from config.constantes import CONSTANTES
import asyncio
from controlador.controlador_pve import ControladorPVE
from controlador.controlador_pvp_cliente import ControladorPVPCliente
from red.cliente.cliente_socket import ClienteSocket
import time


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
            pve_dificultades = []
            for clave in self.controlador_pve.config_dificultad.keys():
                pve_dificultades.append(int(clave))
                
            while True:
                opcion = self._menu.ejecutar_menu_principal(pve_dificultades)
                
                if opcion in pve_dificultades:
                    dificultad = opcion
                    self.controlador_pve.iniciar(dificultad)
                    
                elif opcion == len(pve_dificultades) + 1:
                    self._iniciar_cliente_pvp()
                    
        except SalirDelPrograma:
            pass
        
        except KeyboardInterrupt:
            pass
        
        finally:
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