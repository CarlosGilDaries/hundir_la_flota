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
def tableros_barcos_colocados_manualmente():
    """Crea dos tableros con barcos colocados manualmente en posiciones conocidas."""
    tablero1 = Tablero(6, 6, [
        Barco("Prueba", 1, "P", True),
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True)
    ], "~", "X", "O")

    tablero2 = Tablero(6, 6, [
        Barco("Prueba", 1, "P", True),
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True)
    ], "~", "X", "O")
    
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
def tableros_con_un_barco_pequeño():
    """Crea dos tableros con un barco de tamaño 1 colocado manualmente en posición conocida."""
    tablero1 = Tablero(6, 6, [Barco("Test", 1, "T", True)], "~", "X", "O")

    tablero2 = Tablero(6, 6, [Barco("Test", 1, "T", True)], "~", "X", "O")

    tablero1.colocar_barco_manual(tablero1.barcos[0], 0, 0)
    tablero2.colocar_barco_manual(tablero2.barcos[0], 0, 0)

    return [tablero1, tablero2]


@pytest.fixture
def partida_con_barcos_colocados_turno_jugador_1(tableros_barcos_colocados_manualmente):
    tablero1, tablero2 = tableros_barcos_colocados_manualmente
    partida = PartidaPVP(tablero1, tablero2)
    partida._estado = EstadoPartida.JUGANDO
    
    return partida


@pytest.fixture
def partida_con_un_barco_turno_jugador_1(tableros_con_un_barco_pequeño):
    tablero1, tablero2 = tableros_con_un_barco_pequeño
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
        
        
    @pytest.mark.parametrize("jugador, x, y, esperado", [
        (1, 0, 1, ResultadoDisparo.TOCADO),
        (1, 0, 2, ResultadoDisparo.TOCADO),
    ])
    def test_disparo_tocado(self, partida_con_barcos_colocados_turno_jugador_1, jugador, x, y, esperado):
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(jugador, x, y) == esperado
        
    
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
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 2
        partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
    
    
    def test_disparar_fuera_de_turno(self, partida_con_barcos_colocados_turno_jugador_1):
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)  # Jugador 2 intenta disparar en turno de jugador 1
            
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)      # Jugador 1 dispara y cambia turno
        
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)  # Jugador 1 intenta disparar en turno de jugador 2
            
    
    def test_disparar_cuando_estado_no_es_jugando(self, partida_pvp):
        with pytest.raises(ValueError):
            partida_pvp.disparar(1, 0, 0)       # Turno jugador 1 pero estado == EstadoPartida.COLOCACION
            
        
    def test_estado(self, partida_pvp, partida_con_barcos_colocados_turno_jugador_1):
        assert partida_pvp.estado() == EstadoPartida.COLOCACION
        assert partida_con_barcos_colocados_turno_jugador_1.estado() == EstadoPartida.JUGANDO
        
    
    def test_turno_actual(self, partida_con_barcos_colocados_turno_jugador_1):
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 2
        
    
    def test_todos_hundidos_finaliza_partida(self, partida_con_un_barco_turno_jugador_1):
        assert partida_con_un_barco_turno_jugador_1.estado() != EstadoPartida.FINALIZADA
        partida_con_un_barco_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_turno_jugador_1.estado() == EstadoPartida.FINALIZADA
        
    
    def test_hay_victoria_jugador_1(self, partida_con_un_barco_turno_jugador_1):
        assert partida_con_un_barco_turno_jugador_1.hay_victoria() is False
        partida_con_un_barco_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_turno_jugador_1.hay_victoria() is True
        
    
    def test_hay_victoria_jugador_2(self, partida_con_un_barco_turno_jugador_1):
        assert partida_con_un_barco_turno_jugador_1.hay_victoria() is False
        partida_con_un_barco_turno_jugador_1.disparar(1, 1, 0)
        assert partida_con_un_barco_turno_jugador_1.hay_victoria() is False
        partida_con_un_barco_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_un_barco_turno_jugador_1.hay_victoria() is True
        
        
    def test_jugador_1_ganador(self, partida_con_un_barco_turno_jugador_1):
        assert partida_con_un_barco_turno_jugador_1.jugador_ganador() is None
        partida_con_un_barco_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_turno_jugador_1.jugador_ganador() == 1
        
    
    def test_jugador_2_ganador(self, partida_con_un_barco_turno_jugador_1):
        assert partida_con_un_barco_turno_jugador_1.jugador_ganador() is None
        partida_con_un_barco_turno_jugador_1.disparar(1, 1, 0)
        assert partida_con_un_barco_turno_jugador_1.jugador_ganador() is None
        partida_con_un_barco_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_un_barco_turno_jugador_1.jugador_ganador() == 2
    
# TODO Comprobar que el tablero defensor se marca con el disparo del atacante
# TODO obtener_tablero_rival
# TODO obtener_tablero_propio
# TODO colocar_barco