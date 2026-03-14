import pytest
from modelo.barco import Barco

# Barco tamaño 2
@pytest.fixture
def lancha():
    return Barco("Lancha", 2, "L")


# Barco tamaño 4
@pytest.fixture
def acorazado():
    return Barco("Acorazado", 4, "A",  True)


class TestBoat: 
    
    # SET_HORIZONTAL()
    @pytest.mark.parametrize("horizontal", [True, False])
    def test_set_horizontal_pvp(self, lancha, horizontal):
        lancha.set_horizontal(horizontal)
        assert lancha._horizontal == horizontal


    def test_set_horizontal_pve(self, lancha):
        lancha.set_horizontal(None)
        assert isinstance(lancha._horizontal, bool)
        
    
    # GET_HORIZONTAL()
    def test_get_horizontal_pve(self, lancha):
        assert lancha.get_horizontal() == lancha._horizontal
        
    
    # CALCULAR_MAXIMO()
    @pytest.mark.parametrize("alto_o_ancho, maximo", [
        (10, 8),
        (8, 6),
        (12, 10)
    ])
    def test_calcular_maximo(self, lancha, alto_o_ancho, maximo):
        assert lancha.calcular_maximo(alto_o_ancho) == maximo
        
    
    # RECIBIR_IMPACTO()
    def test_recibir_impacto(self, acorazado):
        acorazado.recibir_impacto()
        assert acorazado._vida_restante == 3
        acorazado.recibir_impacto()
        assert acorazado._vida_restante == 2
        
    
    # HUNDIDO()
    def test_hundido(self, lancha):
        lancha.recibir_impacto()
        assert lancha.hundido() == False  # vida_restante == 1
        lancha.recibir_impacto()
        assert lancha.hundido() == True   # vida_restante == 0
