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
def tablero(barcos):
    return Tablero(6, 6, barcos, "~", "X", "O")


@pytest.fixture
def tablero_barcos_colocados_manualmente(barcos):
    tablero = Tablero(6, 6, barcos, "~", "X", "O")
    y = 0
    for barco in tablero.barcos:
        tablero.colocar_barco_manual(barco, 0, y)
        y += 1

    return tablero


@pytest.fixture
def partida_pve(tablero):
    return PartidaPVE(tablero, 10)


class TestPartidaPVE:
    """Clase encargada de testear la lógica de una PartidaPVE"""
    
    def test_constructor(self, partida_pve, tablero):
        """Comprueba que se incializan correctamente los atributos y se ejecuta el método de colocar barcos atuomáticamente"""
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
        
    
    # @pytest.mark.parametrize("x, y, esperado", [
    #     (0, 0, ResultadoDisparo.TOCADO),
    #     (1, 0, ResultadoDisparo.TOCADO),
    #     (2, 2, ResultadoDisparo.TOCADO),
    # ])
    # def test_disparo_tocado(self, partida_con_tablero_pequenyo, x, y, esperado):
    #     assert partida_con_tablero_pequenyo.disparar(x, y) == esperado