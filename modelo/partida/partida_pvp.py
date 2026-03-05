from modelo.partida.partida import Partida
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo
from enum import Enum


class EstadoPartida(Enum):
    COLOCACION = "colocacion"
    JUGANDO = "jugando"
    FINALIZADA = "finalizada"


class PartidaPVP(Partida):

    def __init__(self, tablero_j1: Tablero, tablero_j2: Tablero) -> None:
        """
        Inicializa una partida PVP.

        Args:
            tablero_j1 (Tablero): Tablero del jugador 1.
            tablero_j2 (Tablero): Tablero del jugador 2.
        """
        self._tableros = {
            1: tablero_j1,
            2: tablero_j2
        }

        self._turno = 1
        self._estado = EstadoPartida.COLOCACION

        self._jugadores_listos = set()


    def disparar(self, jugador: int, x: int, y: int) -> ResultadoDisparo:
        """
        Dispara sobre el tablero del defensor.

        Args:
            jugador (int): Entero que representa al jugador.
            x (int): Coordenada X del disparo.
            y (int): Coordenada Y del disparo.

        Raises:
            ValueError: Se ejecuta si el jugador intenta disparar en el turno rival.

        Returns:
            ResultadoDisparo: Enum que representa el resultado del disparo.
        """
        # if self._estado != EstadoPartida.JUGANDO:
        #     raise ValueError("La partida no está en fase de juego")

        if jugador != self._turno:
            raise ValueError("No es tu turno")

        defensor = self._oponente(jugador)

        resultado, _ = self._tableros[defensor].recibir_disparo(x, y)

        if self._tableros[defensor].todos_hundidos():
            self._estado = EstadoPartida.FINALIZADA
        else:
            self._turno = defensor

        return resultado
    
    
    def obtener_tablero_propio(self, jugador: int) -> list:
        """
        Obtiene el tablero del jugador.

        Args:
            jugador (int): Entero que representa al jugador.

        Returns:
            list: Lista que representa el tablero del jugador.
        """
        return self._tableros[jugador].ver_tablero()


    def obtener_tablero_rival(self, jugador: int) -> list:
        """
        Obtiene el tablero del rival.

        Args:
            jugador (int): Entero que representa al jugador rival.

        Returns:
            list: Lista que representa el tablero del jugador rival.
        """
        rival = self._oponente(jugador)
        return self._tableros[rival].ver_tablero_rival()
    
    
    def colocar_barco(self, barco: Barco, x: int, y: int, horizontal: bool, jugador: int) -> bool:
        """
        Coloca un barco en el tablero del jugador.

        Args:
            barco (Barco): Objeto barco a colocar.
            x (int): Coordenada X de la posición inicial.
            y (int): Coordenada Y de la posición inicial.
            horizontal (bool): Orientación del barco.
            jugador (int): Entero que representa al jugador.

        Returns:
            bool: True si se pudo colocar y False si no.
        """
        # if self._estado != EstadoPartida.COLOCACION:
        #     raise ValueError("La fase de colocación ha terminado")

        tablero = self._tableros[jugador]
        barco.set_horizontal(horizontal)
        colocado = tablero.colocar_barco_manual(barco, x, y)

        if colocado:
            if tablero.todos_colocados():
                self._jugadores_listos.add(jugador)

                if len(self._jugadores_listos) == 2:
                    self._estado = EstadoPartida.JUGANDO
                    self._turno = 1

        return colocado
    
    
    def hay_victoria(self) -> bool:
        """
        Comprueba si ha habido victoria.

        Returns:
            bool: True si la ha habido y False si no.
        """
        return self._estado == EstadoPartida.FINALIZADA


    def estado(self) -> EstadoPartida:
        """
        Estado actual de la partida.

        Returns:
            EstadoPartida: Estado de la partida.
        """
        return self._estado


    def turno_actual(self) -> int:
        """
        Turno actual para comprobar quién ataca.

        Returns:
            int: Turno actual.
        """
        return self._turno
    
    
    def jugador_ganador(self) -> int | None:
        """
        Comprueba si hay un ganador.

        Returns:
            int | None: Entero que representa al ganador, None si no ha ganado nadie aún.
        """
        if self._estado != EstadoPartida.FINALIZADA:
            return None

        for jugador in (1, 2):
            if self._tableros[self._oponente(jugador)].todos_hundidos():
                return jugador

        return None


    def _oponente(self, jugador: int) -> int:
        """
        Devuelve el entero que representa al oponente.

        Args:
            jugador (int): Entero que representa al oponente.

        Returns:
            int: entero que representa al oponente.
        """
        return 2 if jugador == 1 else 1

