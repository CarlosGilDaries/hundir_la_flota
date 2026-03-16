import pytest
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from tests.unit.test_partida_pve import barcos, barcos_horizontales, contar_celdas_barco, total_caracteres_barcos

@pytest.fixture
def partida_pvp(barcos):
    tablero1 = Tablero(6, 6, barcos, "~", "X", "O")
    tablero2 = Tablero(6, 6, barcos, "~", "X", "O")
    
    return PartidaPVP(tablero1, tablero2)


@pytest.fixture
def tableros_barcos_colocados_manualmente(barcos_horizontales):
    """Crea dos tableros con barcos colocados manualmente en posiciones conocidas."""
    tablero1 = Tablero(6, 6, barcos_horizontales, "~", "X", "O")
    tablero2 = Tablero(6, 6, barcos_horizontales, "~", "X", "O")
    y = 0
    for barco in tablero1.barcos:
        tablero1.colocar_barco_manual(barco, 0, y)
        y += 1
    
    y = 0
    for barco in tablero2.barcos:
        tablero2.colocar_barco_manual(barco, 0, y)
        y += 1

    return [tablero1, tablero2]


@pytest.fixture
def partida_con_barcos_colocados_turno_jugador_1(tableros_barcos_colocados_manualmente):
    tablero1, tablero2 = tableros_barcos_colocados_manualmente
    partida = PartidaPVP(tablero1, tablero2)
    partida._estado = EstadoPartida.JUGANDO
    
    return partida


class TestPartidaPVP:
    
    def test_constructor(self, partida_pvp):
        assert isinstance(partida_pvp._tableros, dict)
        assert len(partida_pvp._tableros) == 2
        assert partida_pvp._turno == 1
        assert partida_pvp._estado == EstadoPartida.COLOCACION
        assert isinstance(partida_pvp._jugadores_listos, set)
        assert len(partida_pvp._jugadores_listos) == 0
        
        
    @pytest.mark.parametrize("jugador1, x, y, esperado", [
        (1, 0, 1, ResultadoDisparo.TOCADO),
        (1, 0, 2, ResultadoDisparo.TOCADO),
    ])
    def test_disparo_tocado(self, partida_con_barcos_colocados_turno_jugador_1, jugador1, x, y, esperado):
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(jugador1, x, y) == esperado
        
    
    def test_disparo_hundido(self, partida_con_barcos_colocados_turno_jugador_1):
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0) == ResultadoDisparo.HUNDIDO
        
    
    def test_disparo_repetido(self, partida_con_barcos_colocados_turno_jugador_1):
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0) == ResultadoDisparo.REPETIDO
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0) == ResultadoDisparo.REPETIDO
        
    
    def test_disparo_invalido(self, partida_con_barcos_colocados_turno_jugador_1):
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, -10, 0) == ResultadoDisparo.INVALIDO
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 12) == ResultadoDisparo.INVALIDO
    
    
    def test_disparar_cambia_el_turno(self, partida_con_barcos_colocados_turno_jugador_1):
        assert partida_con_barcos_colocados_turno_jugador_1._turno == 1
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1._turno == 2
        partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1._turno == 1
    
    
    def test_disparar_fuera_de_turno(self, partida_con_barcos_colocados_turno_jugador_1):
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)  # Jugador 2 intenta disparar en turno de jugador 1
            
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)      # Jugador 1 dispara y cambia turno
        
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)  # Jugador 1 intenta disparar en turno de jugador 2