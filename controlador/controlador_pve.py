from modelo.tablero import Tablero
from modelo.partida.partida_pve import PartidaPVE
from modelo.ship import Barco
from vista.consola.vista_consola import VistaConsola
from utils.excepciones import VolverAlMenu
from controlador.controlador import Controlador


class ControladorPVE(Controlador):
    def __init__(self, vista: VistaConsola, config: dict) -> None:
        self._vista = vista
        self._config = config
        self._partida: PartidaPVE | None = None
        self.config_dificultad = self._config["DIFICULTAD"]["PVE"]
        
    
    def iniciar(self, dificultad: int) -> None:
        """
            Inicia una nueva partida PVE.

            Args:
                dificultad (int): Índice de dificultad seleccionado.

            Returns:
                None
            """
        self._partida = self.crear_partida(dificultad)
        self.ejecutar_bucle_principal()
        
    
    def crear_barcos(self, config_barcos: list[tuple[str, int, str]]) -> list[Barco]:
        """
        Crea los objetos Barco a partir de la configuración.

        Args:
            config_barcos (list[tuple[str, int, str]]): Configuración de barcos.

        Returns:
            list[Barco]: Lista de objetos Barco creados.
        """
        return [
            Barco(nombre, tamanyo, caracter)
            for nombre, tamanyo, caracter in config_barcos
        ]


    def crear_partida(self, dificultad: int) -> PartidaPVE:
        """
        Crea la partida pve.

        Args:
            dificultad (int): Índice de la dificultad.

        Returns:
            PartidaPVE: Objeto PartidaPVE.
        """
        config_dificultad = self._config["DIFICULTAD"]["PVE"][dificultad]
        caracteres = self._config["CARACTERES"]

        barcos = self.crear_barcos(config_dificultad["barcos"])

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


    def ejecutar_bucle_principal(self) -> None:
        """
        Ejecuta el bucle principal de la partida PVE.

        Returns:
            None
        """
        try:
            self._vista.borrar_consola()

            while self._partida.quedan_disparos() and not self._partida.hay_victoria():
                self.mostrar_estado()
                self.fase_turno()

            self.mostrar_estado()
            self._vista.mostrar_mensaje_final(
                self._partida.hay_victoria(),
                False
            )

        except VolverAlMenu:
            self._vista.borrar_consola()
        
    
    def mostrar_estado(self) -> None:
        """
        Muestra el tablero y los disparos restantes.

        Returns:
            None
        """
        self._vista.mostrar_tablero(
            self._partida.obtener_tablero_rival()
        )
        self._vista.mostrar_balas(
            self._partida.disparos_restantes()
        )
        
    
    def fase_turno(self) -> None:
        """
        Ejecuta la lógica de un turno del jugador.

        Returns:
            None
        """
        ancho, alto = self._partida.obtener_dimensiones_tablero()
        self._vista.opcion_volver_menu()
        x, y = self._vista.pedir_disparo(ancho, alto)
        resultado = self._partida.disparar(x, y)
        self._vista.borrar_consola()
        self._vista.mostrar_resultado(resultado)
