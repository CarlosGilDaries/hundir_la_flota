import pytest
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo

barcos_facil = [
    Barco("Lancha", 2, "L", None), 
    Barco("Submarino", 3, "S", False), 
    Barco("Acorazado", 4, "A", True), 
    Barco("Portaaviones", 5, "P", None)
]

barcos = [
    Barco("Lancha", 2, "L", None), 
    Barco("Submarino", 3, "S", False), 
    Barco("Destructor", 3, "D", True), 
    Barco("Acorazado", 4, "A", True), 
    Barco("Portaaviones", 5, "P", None)
    ]

caracteres_barcos = ["A", "D", "S", "L", "P"]
caracteres_tablero = ["~", "X", "O"]

@pytest.fixture(params=[
    (8, 8, barcos_facil, "~", "X", "O"),
    (10, 10, barcos, "~", "X", "O"),
    (12, 12, barcos, "~", "X", "O")
])
def tablero(request):
    """Fixture que devuelve distintas instancias de Tablero."""
    ancho, alto, barcos, carac_vacio, carac_tocado, carac_agua = request.param
    return Tablero(ancho, alto, barcos, carac_vacio, carac_tocado, carac_agua)


class TestTablero:
    """Tests de comportamiento de la clase Tablero."""
    
    def test_constructor_atributos(self, tablero):
        """Verifica que los atributos básicos se inicializan correctamente."""
        assert tablero.ancho in [8, 10, 12]
        assert tablero.alto in [8, 10, 12]
        assert tablero.barcos in [barcos, barcos_facil]
        assert tablero._caracter_vacio == "~"
        assert tablero._caracter_tocado == "X"
        assert tablero._caracter_agua == "O"
        assert tablero._barcos_colocados == 0
        for fila in tablero.get_todas_las_casillas():
            for columna in fila:
                assert columna == None
                
    
    # def test_get_casillas(self, tablero):
    #     """Comprueba que el método devuelve una copia del atributo casillas"""
    #     vista = tablero.get_casillas()
    #     for fila in vista:
    #         for columna in fila:
    #             assert columna in ["A", "D", "S", "L", "P", None]
    
    
    @pytest.mark.parametrize("x, y, caracter", [
        (4, 5, "X"),
        (0, 0, "O"),
    ])
    def test_marcar_disparo(self, tablero, x, y, caracter):
        """Comprueba que se marca correctamente el tablero con el caracter"""
        tablero.marcar_disparo(x, y, caracter)
        assert tablero.get_una_casilla(x, y) == caracter
    
    
    def test_ver_tablero_rival(self, tablero):
        """Comprueba que el método devuelve el tablero rival sin mostrar los barcos"""
        vista = tablero.ver_tablero_rival()
        for fila in vista:
            for columna in fila:
                assert columna not in caracteres_barcos