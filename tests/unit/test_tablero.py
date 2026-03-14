import pytest
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo

barcos_facil = [
    Barco("Lancha", 2, "L", None), 
    Barco("Submarino", 3, "S", None), 
    Barco("Acorazado", 4, "A", None), 
    Barco("Portaaviones", 5, "P", None)
]

barcos = [
    Barco("Lancha", 2, "L", True), 
    Barco("Submarino", 3, "S", False), 
    Barco("Destructor", 3, "D", True), 
    Barco("Acorazado", 4, "A", True), 
    Barco("Portaaviones", 5, "P", False)
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


@pytest.fixture
def tablero_pvp():
    """Fixture que devuelve una instancia de un tablero pvp"""
    return Tablero(10, 10, barcos, "~", "X", "O")


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
        
    
    @pytest.mark.parametrize("barco, x, y", [
        (barcos[0], 0, 0),
        (barcos[1], 1, 1),
        (barcos[2], 3, 3)
    ])
    def test_introducir_barco_en_tablero(self, tablero, barco, x, y):
        """Comprueba que se puede coloar barcos en el tablero"""
        tablero._introducir_barco_en_tablero(barco, x, y)
        if barco.get_horizontal():
            for i in range(barco.tamanyo):
                assert tablero.get_una_casilla(x, y).nombre == barco.nombre
                x = x + 1
        else:
            for i in range(barco.tamanyo):
                assert tablero.get_una_casilla(x, y).nombre == barco.nombre
                y = y + 1
                
    
    def test_colocar_barco_aleatorio(self, tablero):
        """Comprueba que se puede colocar barcos aleatoriamente"""
        for barco in barcos:
            assert tablero.colocar_barco_aleatorio(barco) == True

# barcos = [
#     Barco("Lancha", 2, "L", True), 
#     Barco("Submarino", 3, "S", False), 
#     Barco("Destructor", 3, "D", True), 
#     Barco("Acorazado", 4, "A", True), 
#     Barco("Portaaviones", 5, "P", False)
#     ]  
            
    @pytest.mark.parametrize("barco, x, y, esperado", [
        (barcos[0], 1, 2, True),    # Tamaño 2 horizontal
        (barcos[1], 4, 5, True),    # Tamaño 3 vertical
        (barcos[2], 8, 2, False),   # Tamaño 3 horizontal - Se sale del tablero por el eje x
        (barcos[3], 0, 0, True),    # Tamaño 4 horizontal
        (barcos[4], 9, 9, False)    # Tamaño 5 vertical - Se sale del tablero por el eje y
    ])
    def test_colocar_barco_manual(self, tablero_pvp, barco, x, y, esperado):
        """Comprueba que se pueden introducir barcos manualmente"""
        assert tablero_pvp.colocar_barco_manual(barco, x, y) == esperado
    
    
    def test_ver_tablero_rival(self, tablero):
        """Comprueba que el método devuelve el tablero rival sin mostrar los barcos"""
        vista = tablero.ver_tablero_rival()
        for fila in vista:
            for columna in fila:
                assert columna not in caracteres_barcos
             
                
    @pytest.mark.parametrize("barco, x, y, esperado", [
        (barcos[0], 1, 2, True),    # Tamaño 2 horizontal
        (barcos[1], 4, 5, False),   # Tamaño 3 vertical - Ya hay barco en posición
        (barcos[2], 8, 2, False),   # Tamaño 3 horizontal - Se sale del tablero por el eje x
        (barcos[3], 0, 0, False),   # Tamaño 4 - Ya hay barco en posición
        (barcos[4], 9, 9, False)    # Tamaño 5 vertical - Se sale del tablero por el eje y
    ])           
    def test_puede_colocarse(self, tablero_pvp, barco, x, y, esperado):
        """Comprueba la validación para colocar barcos"""
        tablero_pvp._introducir_barco_en_tablero(barcos[0], 4, 7)
        tablero_pvp._introducir_barco_en_tablero(barcos[0], 0, 0)
        assert tablero_pvp._puede_colocarse(barco, x, y) == esperado