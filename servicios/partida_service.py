from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from modelo.resultado import ResultadoDisparo
from typing import Any

class PartidaService:
    """
    Capa de aplicación que gestiona la lógica de una partida PvP.
    Esta clase actúa como intermediaria entre el servidor de red
    y el modelo de dominio del juego. Se encarga de preparar la
    partida, gestionar la colocación de barcos, procesar disparos
    y exponer el estado del juego al servidor.
    """
    
    def __init__(self, config: dict[str, Any], caracteres: dict[str, str]) -> None:
        """
        Inicializa el servicio de partida.
        Crea los barcos de cada jugador y prepara la partida con
        los tableros correspondientes.

        Args:
            config (dict[str, Any]): Configuración general del juego.
                Debe contener:
                    - ancho (int)
                    - alto (int)
                    - barcos (list)
            caracteres (dict[str, str]): Diccionario con los caracteres
                utilizados para representar el tablero.
        """
        self.config = config
        self.caracteres = caracteres

        self.barcos_j1 = self._crear_barcos(config["barcos"])
        self.barcos_j2 = self._crear_barcos(config["barcos"])

        self._pendientes = {
            1: self.barcos_j1.copy(),
            2: self.barcos_j2.copy()
        }

        self._crear_partida()


    def _crear_partida(self) -> None:
        """
        Inicializa los tableros y crea la instancia de la partida PvP.

        Returns:
            None
        """
        tablero_j1 = Tablero(
            self.config["ancho"],
            self.config["alto"],
            self.barcos_j1,
            self.caracteres["CARACTER_VACIO"],
            self.caracteres["CARACTER_TOCADO"],
            self.caracteres["CARACTER_AGUA"]
        )

        tablero_j2 = Tablero(
            self.config["ancho"],
            self.config["alto"],
            self.barcos_j2,
            self.caracteres["CARACTER_VACIO"],
            self.caracteres["CARACTER_TOCADO"],
            self.caracteres["CARACTER_AGUA"]
        )

        self._partida = PartidaPVP(tablero_j1, tablero_j2)


    def _crear_barcos(self, config_barcos: list[tuple[str, int, str]]) -> list[Barco]:
        """
        Crea la lista de barcos a partir de la configuración.

        Args:
            config_barcos (list[tuple[str, int, str]]):
                Lista de definiciones de barcos donde cada elemento contiene:
                    - nombre (str)
                    - tamaño (int)
                    - caracter (str)

        Returns:
            list[Barco]: Lista de instancias de barcos.
        """
        return [
            Barco(nombre, tamanyo, caracter)
            for nombre, tamanyo, caracter in config_barcos
        ]


    def estado(self) -> EstadoPartida:
        """
        Devuelve el estado actual de la partida.

        Returns:
            EstadoPartida: Estado actual de la partida.
        """
        return self._partida.estado()


    def turno(self) -> int:
        """
        Devuelve el jugador que tiene el turno actual.

        Returns:
            int: Identificador del jugador (1 o 2).
        """
        return self._partida.turno_actual()


    def barcos_pendientes(self, jugador: int) -> list[dict[str, Any]]:
        """
        Obtiene la lista de barcos que el jugador aún debe colocar.

        Args:
            jugador (int): Identificador del jugador (1 o 2).

        Returns:
            list[dict[str, Any]]: Lista de barcos pendientes con su información:
                - indice (int)
                - nombre (str)
                - tamanyo (int)
        """
        barcos = []
        
        for i, barco in enumerate(self._pendientes[jugador], start=1):
            barcos.append({
                "indice": i,
                "nombre": barco.nombre,
                "tamanyo": barco.tamanyo
            })

        return barcos


    def colocar_barco(self, jugador: int, indice: int, x: int, y: int, horizontal: bool) -> bool:
        """
        Intenta colocar un barco en el tablero del jugador.
        Si la colocación es válida, el barco se elimina de la lista
        de barcos pendientes.

        Args:
            jugador (int): Identificador del jugador.
            indice (int): Índice del barco seleccionado.
            x (int): Coordenada horizontal.
            y (int): Coordenada vertical.
            horizontal (bool): Orientación del barco.

        Returns:
            bool: True si el barco se colocó correctamente, False en caso contrario.

        Raises:
            ValueError: Si el índice de barco es inválido.
        """
        pendientes = self._pendientes[jugador]

        if indice < 1 or indice > len(pendientes):
            raise ValueError("Selección inválida")

        barco = pendientes[indice - 1]

        colocado = self._partida.colocar_barco(
            barco,
            x,
            y,
            horizontal,
            jugador
        )

        if colocado:
            pendientes.remove(barco)

        return colocado


    def disparar(self, jugador: int, x: int, y: int) -> ResultadoDisparo:
        """
        Ejecuta un disparo en el tablero del rival.

        Args:
            jugador (int): Jugador que realiza el disparo.
            x (int): Coordenada horizontal.
            y (int): Coordenada vertical.

        Returns:
            ResultadoDisparo: Resultado del disparo
            (agua, tocado o hundido).
        """
        return self._partida.disparar(jugador, x, y)


    def estado_tableros(self, jugador: int) -> dict[str, Any]:
        """
        Obtiene el estado de los tableros desde la perspectiva del jugador.
        Incluye el tablero propio completo y la información visible
        del tablero del rival.

        Args:
            jugador (int): Identificador del jugador.

        Returns:
            dict[str, Any]: Diccionario con:
                - propio: estado del tablero del jugador
                - rival: estado visible del tablero del rival
        """
        return {
            "propio": self._partida.obtener_tablero_propio(jugador),
            "rival": self._partida.obtener_tablero_rival(jugador)
        }


    def hay_victoria(self) -> bool:
        """
        Indica si la partida ha terminado con un ganador.

        Returns:
            bool: True si existe un ganador, False en caso contrario.
        """
        return self._partida.hay_victoria()


    def ganador(self) -> int | None:
        """
        Devuelve el jugador ganador de la partida.

        Returns:
            int | None:
                - 1 o 2 si existe ganador
                - None si la partida aún no ha terminado
        """
        return self._partida.jugador_ganador()