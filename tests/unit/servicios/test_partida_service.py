import pytest
from modelo.resultado import ResultadoDisparo
from modelo.board import Tablero
from modelo.ship import Barco
from modelo.partida.partida_pvp import PartidaPVP, EstadoPartida
from servicios.partida_service import PartidaService

# =============================================================================
# FIXTURES
# =============================================================================

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


@pytest.fixture
def partida_service_con_un_barco_tamanyo_1_colocado():
    """Devuelve una instancia de PartidaService con un barco tamaño 1 en posición conocida por jugador"""
    config = {
        "ancho": 10,
        "alto": 10,
        "barcos": [
            ("Test", 1, "T"),
        ]
    }
    caracteres = {
        "CARACTER_VACIO": "~",
        "CARACTER_TOCADO": "X",
        "CARACTER_AGUA": "O"
    }
    partida = PartidaService(config, caracteres)

    for jugador in [1, 2]:
        for barco in partida.barcos_pendientes(jugador):
            partida.colocar_barco(jugador, 1, 0, 0, True)
            
    return partida


class TestPartidaService:
    """Tests de PartidaService."""

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
        assert partida_service.barcos_j1 is not partida_service.barcos_pendientes(1)
        assert partida_service.barcos_j2 is not partida_service.barcos_pendientes(2)
        assert partida_service.barcos_pendientes(1) is not partida_service.barcos_pendientes(2)

        # Modificar pendientes no afecta a barcos originales
        original_len = len(partida_service.barcos_j1)
        partida_service.barcos_pendientes(1).pop()
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
    # BARCOS PENDIENTES
    # ============================================================================
    
    def test_barcos_pendientes_longitud(self, partida_service):
        """Comprueba que devuelve el número correcto de barcos pendientes."""
        assert len(partida_service.barcos_pendientes(1)) == len(partida_service.config["barcos"])


    def test_barcos_pendientes_formato(self, partida_service):
        """Comprueba que el formato de salida de barcos_pendientes es correcto."""
        barco = partida_service.barcos_pendientes(1)[0]

        assert isinstance(barco, dict)
        assert set(barco.keys()) == {"indice", "nombre", "tamanyo"}
    
    
    # ============================================================================
    # COLOCACIÓN BARCOS
    # ============================================================================
    
    def test_colocar_barco_valido_elimina_de_pendientes(self, partida_service):
        """Comprueba que colocar un barco válido lo elimina de pendientes."""
        inicial = len(partida_service.barcos_pendientes(1))

        resultado = partida_service.colocar_barco(1, 1, 0, 0, True)

        assert resultado is True
        assert len(partida_service.barcos_pendientes(1)) == inicial - 1


    def test_colocacion_invalida_no_elimina_de_pendientes(self, partida_service):
        """Comprueba que una colocación inválida no elimina el barco."""
        inicial = len(partida_service.barcos_pendientes(1))

        partida_service.colocar_barco(1, 1, 999, 999, True)

        assert len(partida_service.barcos_pendientes(1)) == inicial


    def test_colocar_barco_indice_invalido_lanza_error(self, partida_service):
        """Comprueba que un índice inválido lanza ValueError."""
        with pytest.raises(ValueError):
            partida_service.colocar_barco(1, 0, 0, 0, True)


    def test_indice_corresponde_a_barco_correcto(self, partida_service):
        """Comprueba que el índice corresponde al barco correcto."""
        barcos = partida_service.barcos_pendientes(1)
        nombre_primero = barcos[0]["nombre"]

        partida_service.colocar_barco(1, 1, 0, 0, True)

        restantes = partida_service.barcos_pendientes(1)
        assert all(b["nombre"] != nombre_primero for b in restantes)
            
    
    # =============================================================================
    # DISPARO (DELEGACIÓN)
    # =============================================================================

    def test_disparar_devuelve_resultado_valido(self, partida_service_con_un_barco_tamanyo_1_colocado):
        """Comprueba que disparar devuelve un ResultadoDisparo válido."""
        turno = partida_service_con_un_barco_tamanyo_1_colocado.turno()
        resultado = partida_service_con_un_barco_tamanyo_1_colocado.disparar(turno, 0, 0)

        assert resultado in ResultadoDisparo
        
        
    # =============================================================================
    # ESTADO Y TABLEROS (DELEGACIÓN)
    # =============================================================================
    
    def test_estado(self, partida_service):
        """Comprueba que estado devuelve un EstadoPartida válido"""
        assert partida_service.estado() in EstadoPartida

    def test_estado_tableros_formato(self, partida_service):
        """Comprueba que estado_tableros devuelve la estructura correcta."""
        estado = partida_service.estado_tableros(1)

        assert "propio" in estado
        assert "rival" in estado
        assert isinstance(estado["propio"], list)
        assert isinstance(estado["rival"], list)


    # =============================================================================
    # FINALIZACIÓN
    # =============================================================================

    def test_hay_victoria_y_ganador(self, partida_service_con_un_barco_tamanyo_1_colocado):
        """Comprueba que hay_victoria y ganador funcionan sin errores."""
        assert partida_service_con_un_barco_tamanyo_1_colocado.hay_victoria() is False
        assert partida_service_con_un_barco_tamanyo_1_colocado.ganador() is None
        
        turno = partida_service_con_un_barco_tamanyo_1_colocado.turno()
        partida_service_con_un_barco_tamanyo_1_colocado.disparar(turno, 0, 0)
        
        assert partida_service_con_un_barco_tamanyo_1_colocado.hay_victoria() is True
        assert partida_service_con_un_barco_tamanyo_1_colocado.ganador() is turno