from dominio.tablero import Tablero
from dominio.juego import Juego
from dominio.barco import Barco
from vista.consola.interfaz_consola import InterfazConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import SalirDelPrograma, VolverAlMenu
from config.mensajes import TEXTOS, INSTRUCCIONES
import config.constantes as constante


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
                dificultad = self._menu.ejecutar_menu_principal()
                juego = self._crear_juego(dificultad)
                self._ejecutar_partida(juego)
        except VolverAlMenu:
            self.ejecutar()
        except SalirDelPrograma:
            self._interfaz.fin_programa()


    def _crear_juego(self, dificultad):
        """
        Crea e inicializa una nueva partida del juego.

        :param dificultad: Índice para la dificultad
        :type dificultad: int
        :return: Objeto Juego inicializado.
        :rtype: Juego
        """
        config = constante.DIFICULTAD[dificultad]

        barcos = [
            Barco(longitud, cantidad, identificador)
            for longitud, cantidad, identificador in config["barcos"]
        ]

        tablero_usuario = Tablero(
            config["ancho"],
            config["alto"],
            barcos,
            constante.CARACTER_VACIO
        )

        tablero_interno = Tablero(
            config["ancho"],
            config["alto"],
            barcos,
            constante.CARACTER_VACIO
        )

        return Juego(
            tablero_usuario,
            tablero_interno,
            config["disparos"],
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )


    def _ejecutar_partida(self, juego):
        """
        Ejecuta el bucle principal de una partida.

        :param juego: Instancia del juego en curso.
        :type juego: Juego
        """
        try:
            self._interfaz.borrar_consola()
            self._interfaz.mostrar_tablero(juego.tablero_usuario)
            while juego.quedan_disparos() and not juego.hay_victoria():

                self._interfaz.opcion_volver_menu()
                x, y = self._interfaz.pedir_disparo(
                    juego.tablero_barco.ancho,
                    juego.tablero_barco.alto
                )

                resultado = juego.disparar(x, y)

                self._interfaz.borrar_consola()
                self._interfaz.mostrar_tablero(juego.tablero_usuario)
                self._interfaz.mostrar_resultado(resultado)
                self._interfaz.mostrar_balas(juego.disparos_restantes())

            self._interfaz.mostrar_mensaje_final(juego.hay_victoria())

        except VolverAlMenu:
            self._interfaz.borrar_consola()
