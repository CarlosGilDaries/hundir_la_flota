import pytest
from model.result import ResultadoDisparo
from model.board import Tablero
from model.ship import Barco
from model.partida.partida_pve import PartidaPVE
from tests.helpers import contar_celdas_barco, total_caracteres_barcos

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def barcos():
    """Proporciona una lista de barcos de prueba con distintos tamaños."""
    return [
        Barco("Prueba", 1, "P"),
        Barco("Lancha", 2, "L"),
        Barco("Submarino", 3, "S")
    ]


@pytest.fixture
def barcos_horizontales():
    """Proporciona una lista de barcos configurados con orientación horizontal."""
    return [
        Barco("Prueba", 1, "P", True),
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True)
    ]


@pytest.fixture
def tablero(barcos):
    """Crea un tablero vacío de pruebas con los barcos disponibles."""
    return Tablero(6, 6, barcos, "~", "X", "O")


@pytest.fixture
def tablero_barcos_colocados_manualmente(barcos_horizontales):
    """Crea un tablero con barcos colocados manualmente en posiciones conocidas."""
    tablero = Tablero(6, 6, barcos_horizontales, "~", "X", "O")
    y = 0
    for barco in tablero.barcos:
        tablero.colocar_barco_manual(barco, 0, y)
        y += 1

    return tablero


@pytest.fixture
def partida_pve(tablero):
    """Crea una partida PVE estándar con barcos colocados automáticamente."""
    return PartidaPVE(tablero, 10)


@pytest.fixture
def partida_con_pocos_disparos(tablero):
    """Crea una partida PVE con un número muy limitado de disparos."""
    return PartidaPVE(tablero, 2)


@pytest.fixture
def partida_con_barcos_colocados(tablero_barcos_colocados_manualmente):
    """Crea una partida PVE con barcos ya colocados manualmente para pruebas deterministas."""
    return PartidaPVE(tablero_barcos_colocados_manualmente, 10, True)


@pytest.fixture
def partida_sin_barcos_colocados(tablero):
    """Crea una partida PVE con un tablero vacío sin colocar barcos automáticamente."""
    return PartidaPVE(tablero, 10, True)


class TestPartidaPVE:
    """Clase encargada de testear la lógica de una PartidaPVE"""
    
    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, partida_pve, tablero):
        """Verifica que el constructor inicializa atributos y coloca automáticamente los barcos."""
        cantidad_caracteres_barcos = total_caracteres_barcos(tablero.barcos)
        
        assert partida_pve.tablero_maquina == tablero
        assert partida_pve._disparos_maximos == 10
        assert partida_pve._disparos_realizados == 0             
        assert contar_celdas_barco(partida_pve.obtener_tablero_propio()) == cantidad_caracteres_barcos
        
    
    # ============================================================================
    # DISPAROS
    # ============================================================================
    
    @pytest.mark.parametrize("x, y, esperado", [
        (0, 1, ResultadoDisparo.TOCADO),
        (0, 2, ResultadoDisparo.TOCADO),
    ]) 
    def test_disparo_tocado(self, partida_con_barcos_colocados, x, y, esperado):
        """Comprueba que disparar a una celda con barco devuelve resultado TOCADO."""
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
        
    def test_disparo_hundido(self, partida_con_barcos_colocados):
        """Comprueba que disparar a un barco de tamaño 1 devuelve resultado HUNDIDO."""
        assert partida_con_barcos_colocados.disparar(0, 0) == ResultadoDisparo.HUNDIDO
        
        
    @pytest.mark.parametrize("x, y, esperado", [
        (5, 5, ResultadoDisparo.AGUA),
        (4, 4, ResultadoDisparo.AGUA),
    ])
    def test_disparo_agua(self, partida_con_barcos_colocados, x, y, esperado):
        """Verifica que disparar a una celda vacía devuelve resultado AGUA."""
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
    
    @pytest.mark.parametrize("x, y, esperado", [
        (-2, 5, ResultadoDisparo.INVALIDO),
        (8, 4, ResultadoDisparo.INVALIDO),
    ])
    def test_disparo_invalido(self, partida_con_barcos_colocados, x, y, esperado):
        """Comprueba que disparar fuera de los límites del tablero devuelve INVALIDO."""
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
        
    def test_disparo_repetido(self, partida_con_barcos_colocados):
        """Verifica que disparar dos veces a la misma celda devuelve REPETIDO."""
        partida_con_barcos_colocados.disparar(0, 1)
        assert partida_con_barcos_colocados.disparar(0, 1) == ResultadoDisparo.REPETIDO
        
    
    # ============================================================================
    # CANTIDAD DE DISPAROS / DISPAROS RESTANTES
    # ============================================================================
    
    def test_quedan_disparos(self, partida_con_pocos_disparos):
        """Verifica que el sistema detecta correctamente cuándo se agotan los disparos."""
        assert partida_con_pocos_disparos.quedan_disparos() is True
        partida_con_pocos_disparos.disparar(0, 0)
        assert partida_con_pocos_disparos.quedan_disparos() is True
        partida_con_pocos_disparos.disparar(0, 1)
        assert partida_con_pocos_disparos.quedan_disparos() is False
        
    
    def test_disparos_restantes(self, partida_pve):
        """Comprueba que el número de disparos restantes se actualiza tras cada disparo válido."""
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos
        partida_pve.disparar(0, 0)
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos - partida_pve._disparos_realizados
        partida_pve.disparar(0, 1)
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos - partida_pve._disparos_realizados
    
    def test_disparar_aumenta_disparos_realizados(self, partida_pve):
        """Comprueba que los disparos válidos incrementan el contador de disparos realizados."""
        partida_pve.disparar(0, 0)
        assert partida_pve._disparos_realizados == 1
        partida_pve.disparar(0, 2)
        assert partida_pve._disparos_realizados == 2
        
    
    def test_disparo_repetido_no_aumenta_disparos_realizados(self, partida_pve):
        """Verifica que repetir un disparo no incrementa el contador de disparos."""
        partida_pve.disparar(0, 0)
        partida_pve.disparar(0, 0)
        partida_pve.disparar(0, 0)
        assert partida_pve._disparos_realizados == 1
        
    
    def test_disparo_invalido_no_aumenta_disparos_realizados(self, partida_pve):
        """Comprueba que los disparos inválidos no incrementan el contador de disparos."""
        partida_pve.disparar(-2, 0)
        partida_pve.disparar(5, 12)
        assert partida_pve._disparos_realizados == 0
       
        
    # ============================================================================
    # MOSTRAR TABLEROS
    # ============================================================================
    
    def test_obtener_tablero_propio_devuelve_barcos(self, partida_pve, barcos):
        """Verifica que el tablero propio muestra las posiciones de los barcos."""
        cantidad_caracteres_barco_en_tablero = total_caracteres_barcos(barcos)
        tablero = partida_pve.obtener_tablero_propio()           
        assert contar_celdas_barco(tablero) == cantidad_caracteres_barco_en_tablero
        
    
    def test_obtener_tablero_rival_no_devuelve_barcos(self, partida_pve):
        """Comprueba que el tablero visible al jugador no revela barcos enemigos."""
        tablero = partida_pve.obtener_tablero_rival()      
        assert contar_celdas_barco(tablero) == 0
        
    
    def test_obtener_dimensiones_tablero(self, barcos):
        """Verifica que la partida devuelve correctamente las dimensiones del tablero."""
        ancho = 10
        alto = 10
        tablero = Tablero(ancho, alto, barcos, "~", "X", "O")
        partida = PartidaPVE(tablero, 10)
        
        assert partida.obtener_dimensiones_tablero() == (ancho, alto)
        
        
    # ============================================================================
    # COLOCAR BARCOS
    # ============================================================================
    
    def test_colocar_barco(self, partida_sin_barcos_colocados, barcos):
        """Verifica que los barcos pueden colocarse automáticamente en el tablero."""
        assert partida_sin_barcos_colocados.colocar_barco(barcos[0]) is True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[1]) is True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[2]) is True
        
    
    # ============================================================================
    # VICTORIA
    # ============================================================================
    
    def test_hay_victoria(self, partida_con_barcos_colocados):
        """Comprueba que la victoria se detecta únicamente cuando todos los barcos han sido hundidos."""
        disparos = [(0,0),(0,1),(1,1),(0,2),(1,2)]

        for x,y in disparos:
            partida_con_barcos_colocados.disparar(x,y)
            assert partida_con_barcos_colocados.hay_victoria() is False

        partida_con_barcos_colocados.disparar(2,2)
        assert partida_con_barcos_colocados.hay_victoria() is True