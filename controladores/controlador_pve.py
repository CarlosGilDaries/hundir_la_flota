from dominio.tablero import Tablero
from dominio.partida_pve import PartidaPVE
from dominio.barco import Barco
from vista.consola.interfaz_consola import InterfazConsola
from vista.consola.menu_consola import Menu
from utils.utils import Util
from utils.excepciones import VolverAlMenu
from config.mensajes import TEXTOS, INSTRUCCIONES
import config.constantes as constante
from controladores.controlador import Controlador

class ControladorPVE(Controlador):
    def __init__(self):
        """
        Inicializa el controlador PVE.
        """
        validador = Util()
        self._interfaz = InterfazConsola(TEXTOS, validador)
        self._menu = Menu(self._interfaz, INSTRUCCIONES)
        
        
    def crear_partida(self, dificultad):
        """
        Crea e inicializa una nueva partida pve.

        :param dificultad: Índice para la dificultad
        :type dificultad: int
        :return: Objeto PartidaPVE inicializado.
        :rtype: PartidaPVE
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

        tablero_maquina = Tablero(
            config["ancho"],
            config["alto"],
            barcos,
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )

        return PartidaPVE(
            tablero_usuario,
            tablero_maquina,
            config["disparos"],
            constante.CARACTER_VACIO,
            constante.CARACTER_TOCADO,
            constante.CARACTER_AGUA
        )


    def ejecutar_partida(self, PartidaPVE):
        """
        Ejecuta el bucle principal de una partida pve.

        :param PartidaPVE: Instancia de la partida pve en curso.
        :type PartidaPVE: PartidaPVE
        """
        try:
            ancho, alto = PartidaPVE.obtener_dimensiones_tablero()
            self._interfaz.borrar_consola()
            self._interfaz.mostrar_tablero(PartidaPVE.tablero_usuario.ver_tablero_rival())
            while PartidaPVE.quedan_disparos() and not PartidaPVE.hay_victoria():

                self._interfaz.opcion_volver_menu()
                x, y = self._interfaz.pedir_disparo(
                    ancho,
                    alto
                )

                resultado_enum = PartidaPVE.disparar(x, y)
                resultado = self.adaptar_resultado_a_string(resultado_enum)

                self._interfaz.borrar_consola()
                self._interfaz.mostrar_tablero(PartidaPVE.tablero_usuario.ver_tablero_rival())
                self._interfaz.mostrar_resultado(resultado)
                self._interfaz.mostrar_balas(PartidaPVE.disparos_restantes())

            self._interfaz.mostrar_mensaje_final(PartidaPVE.hay_victoria())

        except VolverAlMenu:
            self._interfaz.borrar_consola()