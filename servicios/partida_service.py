from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from modelo.resultado import ResultadoDisparo


class PartidaService:
    """
    Capa de aplicación que gestiona la lógica de una partida PvP.
    Desacopla el servidor del modelo.
    """

    def __init__(self, config: dict, caracteres: dict):

        self.config = config
        self.caracteres = caracteres

        self.barcos_j1 = self._crear_barcos(config["barcos"])
        self.barcos_j2 = self._crear_barcos(config["barcos"])

        self._pendientes = {
            1: self.barcos_j1.copy(),
            2: self.barcos_j2.copy()
        }

        self._crear_partida()


    def _crear_partida(self):

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


    def _crear_barcos(self, config_barcos: list):

        return [
            Barco(nombre, tamanyo, caracter)
            for nombre, tamanyo, caracter in config_barcos
        ]


    def estado(self) -> EstadoPartida:
        return self._partida.estado()


    def turno(self) -> int:
        return self._partida.turno_actual()


    def barcos_pendientes(self, jugador: int):

        barcos = []

        for i, barco in enumerate(self._pendientes[jugador], start=1):

            barcos.append({
                "indice": i,
                "nombre": barco.nombre,
                "tamanyo": barco.tamanyo
            })

        return barcos


    def colocar_barco(self, jugador: int, indice: int, x: int, y: int, horizontal: bool):

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

        return self._partida.disparar(jugador, x, y)


    def estado_tableros(self, jugador: int):

        return {
            "propio": self._partida.obtener_tablero_propio(jugador),
            "rival": self._partida.obtener_tablero_rival(jugador)
        }


    def hay_victoria(self) -> bool:
        return self._partida.hay_victoria()


    def ganador(self) -> int | None:
        return self._partida.jugador_ganador()
