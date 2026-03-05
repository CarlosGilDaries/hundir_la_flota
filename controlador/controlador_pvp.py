from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP
from modelo.partida.partida_pvp import EstadoPartida
from modelo.resultado import ResultadoDisparo
from config.constantes import CONSTANTES


class ControladorPVP():

    def __init__(self, dificultad: str = "PVP") -> None:
        config = CONSTANTES["DIFICULTAD"][dificultad]
        caracteres = CONSTANTES["CARACTERES"]

        barcos_j1 = self.crear_barcos(config["barcos"])
        barcos_j2 = self.crear_barcos(config["barcos"])

        tablero_j1 = Tablero(
            config["ancho"],
            config["alto"],
            barcos_j1,
            caracteres["CARACTER_VACIO"],
            caracteres["CARACTER_TOCADO"],
            caracteres["CARACTER_AGUA"]
        )

        tablero_j2 = Tablero(
            config["ancho"],
            config["alto"],
            barcos_j2,
            caracteres["CARACTER_VACIO"],
            caracteres["CARACTER_TOCADO"],
            caracteres["CARACTER_AGUA"]
        )

        self._barcos_pendientes = {
            1: barcos_j1.copy(),
            2: barcos_j2.copy()
        }

        self._partida = PartidaPVP(tablero_j1, tablero_j2)
        
    
    def crear_barcos(self, config_barcos: list) -> list:
        return [
            Barco(nombre, tamanyo, caracter)
            for nombre, tamanyo, caracter in config_barcos
        ]
        
    
    def estado(self) -> EstadoPartida:
        return self._partida.estado()


    def turno_actual(self) -> int:
        return self._partida.turno_actual()


    def obtener_barcos_pendientes(self, jugador: int) -> list:
        lista = []

        for i, barco in enumerate(self._barcos_pendientes[jugador], start=1):
            lista.append({
                "indice": i,
                "nombre": barco.nombre,
                "tamanyo": barco.tamanyo
            })

        return lista


    def colocar_barco(self, jugador: int, indice: int, x: int, y: int, horizontal: bool) -> bool:

        pendientes = self._barcos_pendientes[jugador]

        if indice < 1 or indice > len(pendientes):
            raise ValueError("Selección inválida")

        barco = pendientes[indice - 1]

        colocado = self._partida.colocar_barco(
            jugador,
            barco,
            x,
            y,
            horizontal
        )

        if colocado:
            pendientes.remove(barco)

        return colocado


    def disparar(self, jugador: int, x: int, y: int) -> ResultadoDisparo:
        return self._partida.disparar(jugador, x, y)


    def obtener_estado_tableros(self, jugador: int) -> dict:
        return {
            "propio": self._partida.obtener_tablero_propio(jugador),
            "rival": self._partida.obtener_tablero_rival(jugador)
        }


    def hay_victoria(self) -> bool:
        return self._partida.hay_victoria()


    def jugador_ganador(self) -> int | None:
        return self._partida.jugador_ganador()