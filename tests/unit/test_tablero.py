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
        
        for fila in tablero.get_casillas():
            for columna in fila:
                assert columna == None