import pytest
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.partida.partida_pve import PartidaPVE

@pytest.fixture
def barcos():
    return [
        Barco("Prueba", 1, "P"),
        Barco("Lancha", 2, "L"),
        Barco("Submarino", 3, "S")
    ]


@pytest.fixture
def barcos_horizontales():
    return [
        Barco("Prueba", 1, "P", True),
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True)
    ]


@pytest.fixture
def tablero(barcos):
    return Tablero(6, 6, barcos, "~", "X", "O")


@pytest.fixture
def tablero_barcos_colocados_manualmente(barcos_horizontales):
    tablero = Tablero(6, 6, barcos_horizontales, "~", "X", "O")
    y = 0
    for barco in tablero.barcos:
        tablero.colocar_barco_manual(barco, 0, y)
        y += 1

    return tablero


@pytest.fixture
def partida_pve(tablero):
    return PartidaPVE(tablero, 10)


@pytest.fixture
def partida_con_barcos_colocados(tablero_barcos_colocados_manualmente):
    return PartidaPVE(tablero_barcos_colocados_manualmente, 10, True)


@pytest.fixture
def partida_sin_barcos_colocados(tablero):
    return PartidaPVE(tablero, 10, True)


class TestPartidaPVE:
    """Clase encargada de testear la lógica de una PartidaPVE"""
    
    def test_constructor(self, partida_pve, tablero):
        """Comprueba que se incializan correctamente los atributos y se ejecuta el método privado de colocar barcos atuomáticamente"""
        assert partida_pve.tablero_maquina == tablero
        assert partida_pve._disparos_maximos == 10
        assert partida_pve._disparos_realizados == 0
        
        contador_prueba = 0
        contador_lancha = 0
        contador_submarino = 0
        for fila in partida_pve.obtener_tablero_propio():
            for celda in fila:
                if celda == "L":
                    contador_lancha += 1
                elif celda == "S":
                    contador_submarino += 1
                elif celda == "P":
                    contador_prueba +=1
                    
        assert contador_lancha == 2
        assert contador_submarino == 3
        assert contador_prueba == 1
        
    
    @pytest.mark.parametrize("x, y, esperado", [
        (0, 1, ResultadoDisparo.TOCADO),
        (0, 2, ResultadoDisparo.TOCADO),
    ])
    def test_disparo_tocado(self, partida_con_barcos_colocados, x, y, esperado):
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
        
    def test_disparo_hundido(self, partida_con_barcos_colocados):
        assert partida_con_barcos_colocados.disparar(0, 0) == ResultadoDisparo.HUNDIDO
        
        
    @pytest.mark.parametrize("x, y, esperado", [
        (5, 5, ResultadoDisparo.AGUA),
        (4, 4, ResultadoDisparo.AGUA),
    ])
    def test_disparo_agua(self, partida_con_barcos_colocados, x, y, esperado):
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
    
    @pytest.mark.parametrize("x, y, esperado", [
        (-2, 5, ResultadoDisparo.INVALIDO),
        (8, 4, ResultadoDisparo.INVALIDO),
    ])
    def test_disparo_agua(self, partida_con_barcos_colocados, x, y, esperado):
        assert partida_con_barcos_colocados.disparar(x, y) == esperado
        
        
    def test_disparo_repetido(self, partida_con_barcos_colocados):
        partida_con_barcos_colocados.disparar(0, 1)
        assert partida_con_barcos_colocados.disparar(0, 1) == ResultadoDisparo.REPETIDO
        
    
    def test_disparar_aumenta_disparos_realizados(self, partida_pve):
        partida_pve.disparar(0, 0)
        assert partida_pve._disparos_realizados == 1
        partida_pve.disparar(0, 2)
        assert partida_pve._disparos_realizados == 2
        
    
    def test_disparo_repetido_no_aumenta_disparos_realizados(self, partida_pve):
        partida_pve.disparar(0, 0)
        partida_pve.disparar(0, 0)
        partida_pve.disparar(0, 0)
        assert partida_pve._disparos_realizados == 1
        
    
    def test_disparo_invalido_no_aumenta_disparos_realizados(self, partida_pve):
        partida_pve.disparar(-2, 0)
        partida_pve.disparar(5, 12)
        assert partida_pve._disparos_realizados == 0
        
    
    def test_obtener_tablero_propio_devuelve_barcos(self, partida_pve, barcos):
        contador_caracteres_barco_en_tablero = 0
        tablero = partida_pve.obtener_tablero_propio()
        for fila in tablero:
            for celda in fila:
                if celda not in ["~", "X", "O"]:
                    contador_caracteres_barco_en_tablero += 1
        
        cantidad_caracteres_barcos = 0
        for barco in barcos:
            cantidad_caracteres_barcos += barco.tamanyo
            
        assert contador_caracteres_barco_en_tablero == cantidad_caracteres_barcos
        
    
    def test_obtener_tablero_rival_no_devuelve_barcos(self, partida_pve):
        contador_caracteres_barco_en_tablero = 0
        tablero = partida_pve.obtener_tablero_rival()
        for fila in tablero:
            for celda in fila:
                if celda not in ["~", "X", "O"]:
                    contador_caracteres_barco_en_tablero += 1
        
        assert contador_caracteres_barco_en_tablero == 0
        
    
    def test_colocar_barco(self, partida_sin_barcos_colocados, barcos):
        assert partida_sin_barcos_colocados.colocar_barco(barcos[0]) == True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[1]) == True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[2]) == True
        
    
    def test_hay_victoria(self, partida_con_barcos_colocados):
        partida_con_barcos_colocados.disparar(0, 0)
        assert partida_con_barcos_colocados.hay_victoria() == False
        partida_con_barcos_colocados.disparar(0, 1)
        assert partida_con_barcos_colocados.hay_victoria() == False
        partida_con_barcos_colocados.disparar(1, 1)
        assert partida_con_barcos_colocados.hay_victoria() == False
        partida_con_barcos_colocados.disparar(0, 2)
        assert partida_con_barcos_colocados.hay_victoria() == False
        partida_con_barcos_colocados.disparar(1, 2)
        assert partida_con_barcos_colocados.hay_victoria() == False
        partida_con_barcos_colocados.disparar(2, 2)
        assert partida_con_barcos_colocados.hay_victoria() == True