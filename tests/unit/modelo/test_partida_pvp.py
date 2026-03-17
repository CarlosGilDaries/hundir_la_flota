import pytest
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from tests.helpers import contar_celdas_barco, total_caracteres_barcos
from unittest.mock import patch

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def barco_pruebas_tamanyo_3():
    """Devuelve un barco de tamaño 3 para pruebas de colocación."""
    return Barco("Test", 3, "T")


@pytest.fixture
def partida_pvp():
    """Crea una partida PVP con dos tableros de 6x6 y tres barcos por jugador."""
    barcos_j1 = [
        Barco("Prueba", 1, "P"),
        Barco("Lancha", 2, "L"),
        Barco("Submarino", 3, "S")
    ]
    
    barcos_j2 = [
        Barco("Prueba", 1, "P"),
        Barco("Lancha", 2, "L"),
        Barco("Submarino", 3, "S")
    ]
    
    tablero1 = Tablero(6, 6, barcos_j1, "~", "X", "O")
    tablero2 = Tablero(6, 6, barcos_j2, "~", "X", "O")
    
    return PartidaPVP(tablero1, tablero2)


@pytest.fixture
def partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar():
    """Crea una partida PVP donde cada jugador tiene un único barco de tamaño 1 sin colocar."""
    barcos_j1 = [
        Barco("Prueba", 1, "P"),
    ]
    
    barcos_j2 = [
        Barco("Prueba", 1, "P"),
    ]
    
    tablero1 = Tablero(6, 6, barcos_j1, "~", "X", "O")
    tablero2 = Tablero(6, 6, barcos_j2, "~", "X", "O")
    
    return PartidaPVP(tablero1, tablero2)


@pytest.fixture
def tableros_barcos_colocados_manualmente():
    """Crea dos tableros con varios barcos colocados manualmente en posiciones conocidas."""
    tablero1 = Tablero(6, 6, [
        Barco("Prueba", 1, "P", True),
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True)
    ], "~", "X", "O")

    tablero2 = Tablero(6, 6, [
        Barco("Prueba", 1, "P", True),
        Barco("Destructor", 3, "L", True),
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
    """Crea una partida en estado JUGANDO con barcos ya colocados y turno inicial del jugador 1."""
    tablero1, tablero2 = tableros_barcos_colocados_manualmente
    partida = PartidaPVP(tablero1, tablero2)
    partida._estado = EstadoPartida.JUGANDO
    
    return partida


@pytest.fixture
def partida_con_un_barco_colocado_turno_jugador_1(tableros_con_un_barco_pequeño):
    """Crea una partida en estado JUGANDO donde cada jugador tiene un solo barco colocado."""
    tablero1, tablero2 = tableros_con_un_barco_pequeño
    partida = PartidaPVP(tablero1, tablero2)
    partida._estado = EstadoPartida.JUGANDO
    
    return partida


class TestPartidaPVP:
    """Clase encargada de testear la lógica de una PartidaPVP"""
    
    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, partida_pvp):
        """Comprueba que el constructor inicializa correctamente los atributos de la partida."""
        assert isinstance(partida_pvp._tableros, dict)
        assert len(partida_pvp._tableros) == 2
        assert partida_pvp.turno_actual() == 1
        assert partida_pvp.estado() == EstadoPartida.COLOCACION
        assert isinstance(partida_pvp._jugadores_listos, set)
        assert len(partida_pvp._jugadores_listos) == 0
        
    
    # ============================================================================
    # DISPAROS
    # ============================================================================
    
    @pytest.mark.parametrize("jugador, x, y, esperado", [
        (1, 0, 1, ResultadoDisparo.TOCADO),
        (1, 0, 2, ResultadoDisparo.TOCADO),
    ])
    def test_disparo_tocado(self, partida_con_barcos_colocados_turno_jugador_1, jugador, x, y, esperado):
        """Verifica que un disparo sobre una celda de barco devuelve resultado TOCADO."""
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(jugador, x, y) == esperado
        
    
    def test_disparo_hundido(self, partida_con_barcos_colocados_turno_jugador_1):
        """Comprueba que disparar al último segmento de un barco devuelve HUNDIDO."""
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0) == ResultadoDisparo.HUNDIDO
        
    
    def test_disparo_repetido(self, partida_con_barcos_colocados_turno_jugador_1):
        """Verifica que disparar dos veces a la misma celda devuelve REPEtIDO."""
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0) == ResultadoDisparo.REPETIDO
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0) == ResultadoDisparo.REPETIDO
        
    
    def test_disparo_invalido(self, partida_con_barcos_colocados_turno_jugador_1):
        """Comprueba que disparar fuera de los límites del tablero devuelve INVALIDO."""
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(1, -10, 0) == ResultadoDisparo.INVALIDO
        assert partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 12) == ResultadoDisparo.INVALIDO
    
    
    # ============================================================================
    # DISPARO / TURNO / ESTADO
    # ============================================================================
    
    def test_disparar_cambia_el_turno(self, partida_con_barcos_colocados_turno_jugador_1):
        """Verifica que después de un disparo válido el turno cambia al jugador rival."""
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 2
        partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
    
    
    def test_disparar_fuera_de_turno(self, partida_con_barcos_colocados_turno_jugador_1):
        """Comprueba que disparar cuando no es el turno del jugador lanza ValueError."""
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(2, 0, 0)  # Jugador 2 intenta disparar en turno de jugador 1
            
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)      # Jugador 1 dispara y cambia turno
        
        with pytest.raises(ValueError):
            partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)  # Jugador 1 intenta disparar en turno de jugador 2
            
    
    def test_disparar_cuando_estado_no_es_jugando(self, partida_pvp):
        """Verifica que no se puede disparar si la partida no está en estado JUGANDO."""
        with pytest.raises(ValueError):
            partida_pvp.disparar(1, 0, 0)       # Turno jugador 1 pero estado == EstadoPartida.COLOCACION
            
    
    # ============================================================================
    # ESTADOS / TURNOS
    # ============================================================================
    
    def test_estado(self, partida_pvp, partida_con_un_barco_colocado_turno_jugador_1):
        """Comprueba que el método estado devuelve correctamente el estado actual de la partida."""
        assert partida_pvp.estado() == EstadoPartida.COLOCACION
        assert partida_con_un_barco_colocado_turno_jugador_1.estado() == EstadoPartida.JUGANDO
        
    
    def test_turno_actual(self, partida_con_barcos_colocados_turno_jugador_1):
        """Verifica que turno_actual refleja correctamente el cambio de turno tras disparar."""
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 1
        partida_con_barcos_colocados_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_barcos_colocados_turno_jugador_1.turno_actual() == 2
        
    
    def test_todos_hundidos_finaliza_partida(self, partida_con_un_barco_colocado_turno_jugador_1):
        """Comprueba que la partida pasa a FINALIZADA cuando todos los barcos son hundidos."""
        assert partida_con_un_barco_colocado_turno_jugador_1.estado() != EstadoPartida.FINALIZADA
        partida_con_un_barco_colocado_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_colocado_turno_jugador_1.estado() == EstadoPartida.FINALIZADA
        
    
    def test_hay_victoria_jugador(self, partida_con_un_barco_colocado_turno_jugador_1):
        """Verifica que hay_victoria devuelve True cuando se hunden todos los barcos del rival."""
        assert partida_con_un_barco_colocado_turno_jugador_1.hay_victoria() is False
        partida_con_un_barco_colocado_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_colocado_turno_jugador_1.hay_victoria() is True
        
        
    def test_jugador_ganador(self, partida_con_un_barco_colocado_turno_jugador_1):
        """Comprueba que jugador_ganador devuelve el jugador que hunde el último barco rival."""
        assert partida_con_un_barco_colocado_turno_jugador_1.jugador_ganador() is None
        partida_con_un_barco_colocado_turno_jugador_1.disparar(1, 0, 0)
        assert partida_con_un_barco_colocado_turno_jugador_1.jugador_ganador() == 1
        
    
    # ============================================================================
    # MOSTRAR TABLEROS
    # ============================================================================
    
    def test_obtener_tablero_propio_devuelve_barcos(self, partida_con_barcos_colocados_turno_jugador_1):
        """Verifica que obtener_tablero_propio muestra los barcos del jugador."""
        tablero_j1 = partida_con_barcos_colocados_turno_jugador_1.obtener_tablero_propio(1)
        tablero_j2 = partida_con_barcos_colocados_turno_jugador_1.obtener_tablero_propio(2)
        
        assert total_caracteres_barcos(partida_con_barcos_colocados_turno_jugador_1._tableros[1].barcos) == contar_celdas_barco(tablero_j1) == 6 
        assert total_caracteres_barcos(partida_con_barcos_colocados_turno_jugador_1._tableros[2].barcos) == contar_celdas_barco(tablero_j2) == 7
        
    
    def test_obtener_tablero_rival_no_devuelve_barcos(self, partida_con_barcos_colocados_turno_jugador_1):
        """Comprueba que obtener_tablero_rival oculta los barcos del oponente."""
        tablero_rival_jugador_1 = partida_con_barcos_colocados_turno_jugador_1.obtener_tablero_rival(1)     # Obtiene el tablero rival del jugador 1 (tablero j2)
        tablero_rival_jugador_2 = partida_con_barcos_colocados_turno_jugador_1.obtener_tablero_rival(2)     # Obtiene el tablero rival del jugador 2 (tablero j1)
        
        assert contar_celdas_barco(tablero_rival_jugador_1) == 0
        assert contar_celdas_barco(tablero_rival_jugador_2) == 0


    # ============================================================================
    # COLOCACIÓN BARCOS
    # ============================================================================
    
    def test_colocar_barco(self, partida_pvp):
        """Verifica que colocar_barco coloca correctamente un barco en el tablero."""
        barcos_j1 = partida_pvp._tableros[1].barcos      
        assert partida_pvp.colocar_barco(barcos_j1[1], 0, 0, True, 1) is True


    def test_colocar_barco_donde_ya_hay_barco(self, partida_pvp):
        """Comprueba que no se puede colocar un barco encima de otro."""
        barcos_j1 = partida_pvp._tableros[1].barcos       
        assert partida_pvp.colocar_barco(barcos_j1[1], 0, 0, True, 1) is True
        assert partida_pvp.colocar_barco(barcos_j1[2], 0, 0, True, 1) is False
        
    
    def test_colocar_barco_fuera_del_tablero(self, partida_pvp):
        """Verifica que no se puede colocar un barco fuera de los límites del tablero."""
        barcos_j1 = partida_pvp._tableros[1].barcos
        assert partida_pvp.colocar_barco(barcos_j1[2], 10, 10, True, 1) is False
        assert partida_pvp.colocar_barco(barcos_j1[2], 6, 6, True, 1) is False


    @pytest.mark.parametrize("x, y, esperado", [
        (0, 0, "T"),
        (1, 0, "T"),
        (2, 0, "T"),
        (3, 0, "~")
    ])
    def test_colocar_barco_horizontal(self, partida_pvp, barco_pruebas_tamanyo_3, x, y, esperado):
        """Comprueba que un barco horizontal ocupa las celdas correctas del tablero."""
        partida_pvp.colocar_barco(barco_pruebas_tamanyo_3, 0, 0, True, 1)
        tablero_j1 = partida_pvp.obtener_tablero_propio(1)
        assert tablero_j1[y][x] == esperado
        
    
    @pytest.mark.parametrize("x, y, esperado", [
        (0, 0, "T"),
        (0, 1, "T"),
        (0, 2, "T"),
        (0, 3, "~")
    ])
    def test_colocar_barco_vertical(self, partida_pvp, barco_pruebas_tamanyo_3, x, y, esperado):
        """Comprueba que un barco vertical ocupa las celdas correctas del tablero."""
        partida_pvp.colocar_barco(barco_pruebas_tamanyo_3, 0, 0, False, 1)
        tablero_j1 = partida_pvp.obtener_tablero_propio(1)
        assert tablero_j1[y][x] == esperado
        
    
    # ============================================================================
    # COLOCACIÓN / ESTADOS / TURNOS
    # ============================================================================
    
    def test_todos_colocados_introduce_jugador_en_jugadores_listos(self, partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar):
        """Verifica que un jugador se añade a jugadores_listos cuando coloca todos sus barcos."""
        assert len(partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._jugadores_listos) == 0

        barcos_j2 = partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._tableros[2].barcos
        partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.colocar_barco(barcos_j2[0], 0, 0, False, 2)
        assert len(partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._jugadores_listos) == 1
        assert 2 in partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._jugadores_listos
    
    
    def test_jugadores_listos_cambia_estado_a_jugando(self, partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar):
        """Comprueba que el estado pasa a JUGANDO cuando ambos jugadores colocan sus barcos."""
        assert partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.estado() != EstadoPartida.JUGANDO
        
        barcos_j2 = partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._tableros[2].barcos
        barcos_j1 = partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._tableros[1].barcos
        partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.colocar_barco(barcos_j2[0], 0, 0, False, 2)
        partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.colocar_barco(barcos_j1[0], 0, 0, False, 1)
        assert len(partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._jugadores_listos) == 2
        assert partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.estado() == EstadoPartida.JUGANDO
        
    
    def test_jugadores_listos_randomiza_turnos(self, partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar):
        """Verifica que el primer turno se decide aleatoriamente cuando ambos jugadores están listos."""
        barcos_j2 = partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._tableros[2].barcos
        barcos_j1 = partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar._tableros[1].barcos

        partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.colocar_barco(barcos_j2[0], 0, 0, False, 2)
        with patch("modelo.partida.partida_pvp.random.randint", return_value=2):
            partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.colocar_barco(barcos_j1[0], 0, 0, False, 1)
        assert partida_pvp_con_un_barco_tamanyo_1_por_tablero_sin_colocar.turno_actual() == 2