import pytest
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from servicios.partida_service import PartidaService
from tests.helpers import contar_celdas_barco, total_caracteres_barcos

@pytest.fixture
def partida_service():
    """Devuelve una instancia de PartidaService""" 
    config = {
        "ancho": 10,
        "alto": 10,
        "barcos": [
            ("Portaaviones", 5, "P"),
            ("Acorazado", 4, "A"),
            ("Destructor", 3, "D"),
            ("Submarino", 3, "S"),
            ("Lancha", 2, "L"),
        ]
    }
    caracteres = {
        "CARACTER_VACIO": "~",
        "CARACTER_TOCADO": "X",
        "CARACTER_AGUA": "O"
    }
    
    return PartidaService(config, caracteres)


class TestPartidaService:
    """Tests del constructor de PartidaService."""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    
    def test_constructor_crea_barcos_correctamente(self, partida_service):
        """Comprueba que los barcos se crean con los datos correctos de configuración."""
        for barco, config_barco in zip(partida_service.barcos_j1, partida_service.config["barcos"]):
            nombre, tam, char = config_barco
            assert barco.nombre == nombre
            assert barco.tamanyo == tam
            assert barco.caracter == char

        for barco, config_barco in zip(partida_service.barcos_j2, partida_service.config["barcos"]):
            nombre, tam, char = config_barco
            assert barco.nombre == nombre
            assert barco.tamanyo == tam
            assert barco.caracter == char

        # Los barcos de J1 y J2 deben ser objetos distintos
        for b1, b2 in zip(partida_service.barcos_j1, partida_service.barcos_j2):
            assert b1 is not b2


    def test_constructor_copias_independientes(self, partida_service):
        """Comprueba que las listas de pendientes son copias independientes."""
        assert partida_service.barcos_j1 is not partida_service._pendientes[1]
        assert partida_service.barcos_j2 is not partida_service._pendientes[2]
        assert partida_service._pendientes[1] is not partida_service._pendientes[2]

        # Modificar pendientes no afecta a barcos originales
        original_len = len(partida_service.barcos_j1)
        partida_service._pendientes[1].pop()
        assert len(partida_service.barcos_j1) == original_len


    def test_constructor_crea_partida_correctamente(self, partida_service):
        """Comprueba que se crea la partida con tableros y estado inicial correctos."""
        partida = partida_service._partida

        assert isinstance(partida, PartidaPVP)
        assert partida.estado() == EstadoPartida.COLOCACION
        assert partida.turno_actual() == 1

        tablero_j1 = partida._tableros[1]
        tablero_j2 = partida._tableros[2]

        assert tablero_j1.ancho == partida_service.config["ancho"]
        assert tablero_j1.alto == partida_service.config["alto"]
        assert tablero_j2.ancho == partida_service.config["ancho"]
        assert tablero_j2.alto == partida_service.config["alto"]
        
        
    # ============================================================================
    # ESTADOS / TURNOS
    # ============================================================================
    
    
    
    # ============================================================================
    # COLOCACIÓN BARCOS
    # ============================================================================
    
    @pytest.mark.parametrize("jugador, indice, x, y, horizontal, resultado_esperado", [
        (1, 1, 0, 0, True, True),
        (2, 1, 0, 0, True, True),
        (1, 2, 5, 5, False, True),
        (2, 2, 5, 5, False, True),
        (1, 4, 8, 8, True, False),
        (2, 4, 8, 8, True, False)
    ])
    def test_colocar_barco(self, partida_service, jugador, indice, x, y, horizontal, resultado_esperado):
        """Comprueba que se pueden colocar barcos sólo si entran dentro de los límites del tablero"""
        assert partida_service.colocar_barco(jugador, indice, x, y, horizontal) == resultado_esperado
        
        
    @pytest.mark.parametrize("jugador, indice, x, y, horizontal, resultado_esperado", [
        (1, -2, 5, 5, False, ValueError),
        (1, 0, 5, 5, False, ValueError),
        (2, 6, 5, 5, False, ValueError),
    ])
    def test_colocar_barco_genera_excepcion_por_indice(self, partida_service, jugador, indice, x, y, horizontal, resultado_esperado):
        """Comprueba que se genera una excepción si el índice está fuera del rango válido"""
        with pytest.raises(resultado_esperado):
            partida_service.colocar_barco(jugador, indice, x, y, horizontal)
            
    
    def test_colocar_barco_lo_elimina_de_pendientes(self, partida_service):
        cantidad_inicial_barcos_j1 = len(partida_service._pendientes[1])
        cantidad_inicial_barcos_j2 = len(partida_service._pendientes[2])
        
        partida_service.colocar_barco(1, 1, 0, 0, True)
        partida_service.colocar_barco(2, 1, 0, 0, True)
        assert cantidad_inicial_barcos_j1 > len(partida_service._pendientes[1])
        assert cantidad_inicial_barcos_j2 > len(partida_service._pendientes[2])