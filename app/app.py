from dominio.tablero import Tablero
from dominio.juego_pve import JuegoPVE
from dominio.barco import Barco
from vista.consola.interfaz_consola import InterfazConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma, VolverAlMenu
from config.mensajes import TEXTOS, INSTRUCCIONES
import config.constantes as constante
import asyncio
from red.cliente import ClientePVP

class App:

    def __init__(self):
        """
        Inicializa la aplicación.
        """
        validador = Util()
        self._interfaz = InterfazConsola(TEXTOS, validador)
        self._menu = Menu(self._interfaz, INSTRUCCIONES)


    def ejecutar(self):
        """
        Inicia la ejecución de la aplicación.
        """
        try:
            while True:
                opcion = self._menu.ejecutar_menu_principal()
                if opcion in [1, 2, 3]:
                    dificultad = opcion
                    juego_pve = self._crear_juego_pve(dificultad)
                    self._ejecutar_partida_pve(juego_pve)
                elif opcion == 4:
                    self._iniciar_cliente_pvp()
        except SalirDelPrograma:
            self._interfaz.fin_programa()


    def _crear_juego_pve(self, dificultad):
        """
        Crea e inicializa una nueva partida pve del juego.

        :param dificultad: Índice para la dificultad
        :type dificultad: int
        :return: Objeto JuegoPVE inicializado.
        :rtype: JuegoPVE
        """
        config = constante.DIFICULTAD[dificultad]

        barcos = [
            Barco(nombre, longitud, identificador)
            for nombre, longitud, identificador in config["barcos"]
        ]

        tablero_usuario = Tablero(
            config["ancho"],
            config["alto"],
            barcos,
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )

        tablero_interno = Tablero(
            config["ancho"],
            config["alto"],
            barcos,
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )

        return JuegoPVE(
            tablero_usuario,
            tablero_interno,
            config["disparos"],
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )


    def _ejecutar_partida_pve(self, juego):
        """
        Ejecuta el bucle principal de una partida pve.

        :param juego: Instancia del juego pve en curso.
        :type juego: JuegoPVE
        """
        try:
            self._interfaz.borrar_consola()
            self._interfaz.mostrar_tablero(juego.tablero_usuario.ver_tablero_rival())
            while juego.quedan_disparos() and not juego.hay_victoria():

                self._interfaz.opcion_volver_menu()
                x, y = self._interfaz.pedir_disparo(
                    juego.tablero_barco.ancho,
                    juego.tablero_barco.alto
                )

                resultado = juego.disparar(x, y)

                self._interfaz.borrar_consola()
                self._interfaz.mostrar_tablero(juego.tablero_usuario.ver_tablero_rival())
                self._interfaz.mostrar_resultado(resultado)
                self._interfaz.mostrar_balas(juego.disparos_restantes())

            self._interfaz.mostrar_mensaje_final(juego.hay_victoria())

        except VolverAlMenu:
            self._interfaz.borrar_consola()
            
            
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