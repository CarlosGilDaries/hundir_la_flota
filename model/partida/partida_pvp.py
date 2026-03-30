from model.partida.game import Partida
from model.board import Tablero
from model.ship import Barco
from model.result import ResultadoDisparo
from enum import Enum
import random


class EstadoPartida(Enum):
    """
    Estados posibles de una partida PVP.
    """
    COLOCACION = "colocacion"
    JUGANDO = "jugando"
    FINALIZADA = "finalizada"


class PartidaPVP(Partida):
    """
    Implementación de una partida entre dos jugadores (PVP).
    """
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
        Realiza un disparo sobre el tablero rival.

        Args:
            jugador (int): Jugador que dispara.
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Raises:
            ValueError: Si no es el turno del jugador.

        Returns:
            ResultadoDisparo: Resultado del disparo.
        """
        if jugador != self._turno or self.estado() != EstadoPartida.JUGANDO:
            raise ValueError("No es tu turno de disparar")

        defensor = self._oponente(jugador)

        resultado, _ = self._tableros[defensor].recibir_disparo(x, y)

        if self._tableros[defensor].todos_hundidos():
            self._estado = EstadoPartida.FINALIZADA
        else:
            self._turno = defensor

        return resultado
    
    
    def obtener_tablero_propio(self, jugador: int) -> list[list[str]]:
        """
        Devuelve el tablero propio del jugador.

        Args:
            jugador (int): Identificador del jugador.

        Returns:
            list[list[str]]: Tablero completo del jugador.
        """
        return self._tableros[jugador].ver_tablero()


    def obtener_tablero_rival(self, jugador: int) -> list[list[str]]:
        """
        Devuelve el tablero visible del rival.

        Args:
            jugador (int): Identificador del jugador.

        Returns:
            list[list[str]]: Tablero del rival con barcos ocultos.
        """
        rival = self._oponente(jugador)
        return self._tableros[rival].ver_tablero_rival()
    
    
    def colocar_barco(self, barco: Barco, x: int, y: int, horizontal: bool, jugador: int) -> bool:
        """
        Coloca un barco en el tablero del jugador.

        Args:
            barco (Barco): Barco a colocar.
            x (int): Coordenada X inicial.
            y (int): Coordenada Y inicial.
            horizontal (bool): Orientación del barco.
            jugador (int): Identificador del jugador.

        Returns:
            bool: True si se colocó correctamente, False si no.
        """
        tablero = self._tableros[jugador]
        barco.set_horizontal(horizontal)
        colocado = tablero.colocar_barco_manual(barco, x, y)

        if colocado:
            if tablero.todos_colocados():
                self._jugadores_listos.add(jugador)

                if len(self._jugadores_listos) == 2:
                    self._estado = EstadoPartida.JUGANDO
                    self._turno = self._randomizar_turnos()

        return colocado
    
    
    def hay_victoria(self) -> bool:
        """
        Indica si la partida ha terminado.

        Returns:
            bool: True si la partida ha finalizado.
        """
        return self._estado == EstadoPartida.FINALIZADA


    def estado(self) -> EstadoPartida:
        """
        Devuelve el estado actual de la partida.

        Returns:
            EstadoPartida: Estado actual.
        """
        return self._estado


    def turno_actual(self) -> int:
        """
        Devuelve el jugador al que le toca atacar.

        Returns:
            int: Jugador actual.
        """
        return self._turno
    
    
    def jugador_ganador(self) -> int | None:
        """
        Determina el jugador ganador.

        Returns:
            int | None: Jugador ganador o None si aún no hay.
        """
        if self._estado != EstadoPartida.FINALIZADA:
            return None

        for jugador in (1, 2):
            if self._tableros[self._oponente(jugador)].todos_hundidos():
                return jugador

        return None


    def _oponente(self, jugador: int) -> int:
        """
        Devuelve el identificador del jugador rival.

        Args:
            jugador (int): Jugador actual.

        Returns:
            int: Jugador rival.
        """
        return 2 if jugador == 1 else 1


    def _randomizar_turnos(self) -> int:
        """
        Randomiza el primer turno para que sea aleatorio quién empieza.

        Returns:
            int: 1 para que empiece el jugador 1 y 2 para que empiece el jugador 2.
        """
        return random.randint(1, 2)