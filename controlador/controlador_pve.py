from modelo.tablero import Tablero
from modelo.partida.partida_pve import PartidaPVE
from modelo.barco import Barco
from vista.consola.vista_consola_pve import VistaConsolaPVE
from vista.consola.menu_consola_pve import Menu
from utils.excepciones import VolverAlMenu
from controlador.controlador import Controlador
from modelo.resultado import ResultadoDisparo

class ControladorPVE(Controlador):
    def __init__(self, vista: VistaConsolaPVE, config: dict) -> None:
        self._vista = vista
        self._config = config
        self._partida: PartidaPVE | None = None
        
    
    def iniciar_partida(self, dificultad: int) -> None:
        """
        Crea una nueva partida pve.

        :param dificultad: Índice para la dificultad.
        :type dificultad: int
        :return: Objeto PartidaPVE inicializado.
        :rtype: PartidaPVE
        """
        self._partida = self._crear_partida(dificultad)
        self._ejecutar_bucle_principal()

    def _crear_partida(self, dificultad: int) -> PartidaPVE:
        config_dificultad = self._config["DIFICULTAD"]["PVE"][dificultad]
        caracteres = self._config["CARACTERES"]

        barcos = self._crear_barcos(config_dificultad["barcos"])

        tablero = Tablero(
            config_dificultad["ancho"],
            config_dificultad["alto"],
            barcos,
            caracteres["CARACTER_VACIO"],
            caracteres["CARACTER_TOCADO"],
            caracteres["CARACTER_AGUA"]
        )

        return PartidaPVE(
            tablero,
            config_dificultad["disparos"]
        )


    def _ejecutar_bucle_principal(self) -> None:
        if self._partida is None:
            raise RuntimeError("No hay partida iniciada")

        try:
            self._vista.borrar_consola()

            while self._partida.quedan_disparos() and not self._partida.hay_victoria():
                self._mostrar_estado()
                self._fase_turno()

            self._mostrar_estado()
            self._vista.mostrar_mensaje_final(
                self._partida.hay_victoria()
            )

        except VolverAlMenu:
            self._vista.borrar_consola()
            
            
    def _crear_barcos(self, config_barcos: list) -> list:
        return [
            Barco(nombre, tamanyo, caracter)
            for nombre, tamanyo, caracter in config_barcos
        ]
        
    
    def _mostrar_estado(self) -> None:
        self._vista.mostrar_tablero(
            self._partida.obtener_tablero_rival()
        )
        self._vista.mostrar_balas(
            self._partida.disparos_restantes()
        )
        
    
    def _fase_turno(self) -> None:
        ancho, alto = self._partida.obtener_dimensiones_tablero()
        self._vista.opcion_volver_menu()
        x, y = self._vista.pedir_disparo(ancho, alto)
        resultado = self._partida.disparar(x, y)
        self._vista.borrar_consola()
        self._vista.mostrar_resultado(resultado)