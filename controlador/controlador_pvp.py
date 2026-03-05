from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP
from modelo.partida.partida_pvp import EstadoPartida
from modelo.resultado import ResultadoDisparo
from config.constantes import CONSTANTES
from controlador.controlador import Controlador


class ControladorPVP(Controlador):

    def __init__(self, constantes: dict) -> None:
        self.config = constantes["DIFICULTAD"]["PVP"]
        self.caracteres = constantes["CARACTERES"]

        self.barcos_j1 = self.crear_barcos(self.config["barcos"])
        self.barcos_j2 = self.crear_barcos(self.config["barcos"])
        
        self._barcos_pendientes = {
            1: self.barcos_j1.copy(),
            2: self.barcos_j2.copy()
        }
        
        self.iniciar()
        
    
    def iniciar(self) -> None:
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


    def obtener_estado_tableros(self, jugador: int) -> dict:
        return {
            "propio": self._partida.obtener_tablero_propio(jugador),
            "rival": self._partida.obtener_tablero_rival(jugador)
        }


    def hay_victoria(self) -> bool:
        return self._partida.hay_victoria()


    def jugador_ganador(self) -> int | None:
        return self._partida.jugador_ganador()