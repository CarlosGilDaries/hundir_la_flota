import pytest
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from tests.unit.test_partida_pve import barcos, barcos_horizontales, tablero_barcos_colocados_manualmente, contar_celdas_barco, total_caracteres_barcos

@pytest.fixture
def partida_pvp(barcos):
    tablero1 = Tablero(6, 6, barcos, "~", "X", "O")
    tablero2 = Tablero(6, 6, barcos, "~", "X", "O")
    return PartidaPVP(tablero1, tablero2)


class TestPartidaPVP:
    
    def test_constructor(self, partida_pvp):
        assert isinstance(partida_pvp._tableros, dict)
        assert len(partida_pvp._tableros) == 2
        assert partida_pvp._turno == 1
        assert partida_pvp._estado == EstadoPartida.COLOCACION
        assert isinstance(partida_pvp._jugadores_listos, set)
        assert len(partida_pvp._jugadores_listos) == 0