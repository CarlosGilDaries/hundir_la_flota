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
def partida_con_pocos_disparos(tablero):
    return PartidaPVE(tablero, 2)


@pytest.fixture
def partida_con_barcos_colocados(tablero_barcos_colocados_manualmente):
    return PartidaPVE(tablero_barcos_colocados_manualmente, 10, True)


@pytest.fixture
def partida_sin_barcos_colocados(tablero):
    return PartidaPVE(tablero, 10, True)


def contar_celdas_barco(tablero):
        contador = 0
        for fila in tablero:
            for celda in fila:
                if celda not in ["~", "X", "O"]:
                    contador += 1
        return contador
    
    
def total_caracteres_barcos(lista_barcos):
    return sum(barco.tamanyo for barco in lista_barcos)


class TestPartidaPVE:
    """Clase encargada de testear la lógica de una PartidaPVE"""
  
    def test_constructor(self, partida_pve, tablero):
        """Comprueba que se incializan correctamente los atributos y se ejecuta el método privado de colocar barcos atuomáticamente"""
        cantidad_caracteres_barcos = total_caracteres_barcos(tablero.barcos)
        
        assert partida_pve.tablero_maquina == tablero
        assert partida_pve._disparos_maximos == 10
        assert partida_pve._disparos_realizados == 0             
        assert contar_celdas_barco(partida_pve.obtener_tablero_propio()) == cantidad_caracteres_barcos
        
    
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
    def test_disparo_invalido(self, partida_con_barcos_colocados, x, y, esperado):
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
        cantidad_caracteres_barco_en_tablero = total_caracteres_barcos(barcos)
        tablero = partida_pve.obtener_tablero_propio()           
        assert contar_celdas_barco(tablero) == cantidad_caracteres_barco_en_tablero
        
    
    def test_obtener_tablero_rival_no_devuelve_barcos(self, partida_pve):
        tablero = partida_pve.obtener_tablero_rival()      
        assert contar_celdas_barco(tablero) == 0
        
    
    def test_colocar_barco(self, partida_sin_barcos_colocados, barcos):
        assert partida_sin_barcos_colocados.colocar_barco(barcos[0]) is True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[1]) is True
        assert partida_sin_barcos_colocados.colocar_barco(barcos[2]) is True
        
    
    def test_hay_victoria(self, partida_con_barcos_colocados):
        disparos = [(0,0),(0,1),(1,1),(0,2),(1,2)]

        for x,y in disparos:
            partida_con_barcos_colocados.disparar(x,y)
            assert partida_con_barcos_colocados.hay_victoria() is False

        partida_con_barcos_colocados.disparar(2,2)
        assert partida_con_barcos_colocados.hay_victoria() is True
        
    
    def test_quedan_disparos(self, partida_con_pocos_disparos):
        assert partida_con_pocos_disparos.quedan_disparos() is True
        partida_con_pocos_disparos.disparar(0, 0)
        assert partida_con_pocos_disparos.quedan_disparos() is True
        partida_con_pocos_disparos.disparar(0, 1)
        assert partida_con_pocos_disparos.quedan_disparos() is False
        
    
    def test_disparos_restantes(self, partida_pve):
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos
        partida_pve.disparar(0, 0)
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos - partida_pve._disparos_realizados
        partida_pve.disparar(0, 1)
        assert partida_pve.disparos_restantes() == partida_pve._disparos_maximos - partida_pve._disparos_realizados
        
    
    def test_obtener_dimensiones_tablero(self, barcos):
        ancho = 10
        alto = 10
        tablero = Tablero(ancho, alto, barcos, "~", "X", "O")
        partida = PartidaPVE(tablero, 10)
        
        assert partida.obtener_dimensiones_tablero() == (ancho, alto)