from dominio.partida_base import PartidaBase
from dominio.resultado import ResultadoDisparo

class PartidaPVP(PartidaBase):

    def disparar(self, jugador, x, y):
        tablero_objetivo = self.obtener_tablero_rival(jugador)
        resultado = tablero_objetivo.recibir_disparo(x, y)

        if resultado != ResultadoDisparo.INVALIDO:
            self._cambiar_turno()

        return resultado
