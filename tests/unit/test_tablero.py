import pytest
from modelo.tablero import Tablero
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo

caracteres_barcos = ["A", "D", "S", "L", "P"]
caracteres_tablero = ["~", "X", "O"]

@pytest.fixture
def barcos_facil():
    """Ficture que devuelve una lista de barcos para el nivel fácil"""
    return [
        Barco("Lancha", 2, "L", None), 
        Barco("Submarino", 3, "S", None), 
        Barco("Acorazado", 4, "A", None), 
        Barco("Portaaviones", 5, "P", None)
    ]


@pytest.fixture
def barcos():
    """Fixture que develve una lista de barcos"""
    return [
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", False),
        Barco("Destructor", 3, "D", True),
        Barco("Acorazado", 4, "A", True),
        Barco("Portaaviones", 5, "P", False),
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


@pytest.fixture
def tablero_pvp(barcos):
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
    
    
    @pytest.mark.parametrize("x, y, caracter", [
        (4, 5, "X"),
        (0, 0, "O"),
    ])
    def test_marcar_disparo(self, tablero, x, y, caracter):
        """Comprueba que se marca correctamente el tablero con el caracter"""
        tablero.marcar_disparo(x, y, caracter)
        assert tablero.get_una_casilla(x, y) == caracter
        
    
    @pytest.mark.parametrize("barco, x, y", [
        (Barco("Lancha", 2, "L", True), 0, 0),
        (Barco("Submarino", 3, "S", True), 1, 1),
        (Barco("Destructor", 2, "L", True), 3, 3)
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
                
    
    def test_colocar_barco_aleatorio(self, tablero, barcos):
        """Comprueba que se puede colocar barcos aleatoriamente"""
        for barco in barcos:
            assert tablero.colocar_barco_aleatorio(barco) == True
        
        assert tablero._barcos_colocados == len(barcos)

            
    @pytest.mark.parametrize("barco, x, y, esperado", [
        (Barco("Lancha", 2, "L", True), 1, 2, True),            # Tamaño 2 horizontal
        (Barco("Submarino", 3, "S", False), 4, 5, True),        # Tamaño 3 vertical
        (Barco("Destructor", 3, "D", True), 8, 2, False),       # Tamaño 3 horizontal - Se sale del tablero por el eje x
        (Barco("Acorazado", 4, "A", True), 0, 0, True),         # Tamaño 4 horizontal
        (Barco("Portaaviones", 5, "P", False), 9, 9, False)     # Tamaño 5 vertical - Se sale del tablero por el eje y
    ])
    def test_colocar_barco_manual(self, tablero_pvp, barco, x, y, esperado):
        """Comprueba que se pueden introducir barcos manualmente y que aumente el estado de barcos_colocados"""
        barcos_antes = tablero_pvp._barcos_colocados
        resultado = tablero_pvp.colocar_barco_manual(barco, x, y)
        assert resultado == esperado
        incremento = 1 if esperado else 0
        assert tablero_pvp._barcos_colocados == barcos_antes + incremento
    
    
    def test_ver_tablero_rival(self, tablero):
        """Comprueba que el método devuelve el tablero rival sin mostrar los barcos"""
        vista = tablero.ver_tablero_rival()
        for fila in vista:
            for columna in fila:
                assert columna not in caracteres_barcos
             
                
    @pytest.mark.parametrize("barco, x, y, esperado", [
        (Barco("Lancha", 2, "L", True), 1, 2, True),            # Tamaño 2 horizontal
        (Barco("Submarino", 3, "S", False), 4, 5, False),       # Tamaño 3 vertical - Ya hay barco en posición
        (Barco("Destructor", 3, "D", True), 8, 2, False),       # Tamaño 3 horizontal - Se sale del tablero por el eje x
        (Barco("Acorazado", 4, "A", True), 0, 0, False),        # Tamaño 4 - Ya hay barco en posición
        (Barco("Portaaviones", 5, "P", False), 9, 9, False)     # Tamaño 5 vertical - Se sale del tablero por el eje y
    ])           
    def test_puede_colocarse(self, tablero_pvp, barco, x, y, esperado):
        """Comprueba la validación para colocar barcos"""
        tablero_pvp._introducir_barco_en_tablero(Barco("Lancha", 2, "L", True), 4, 7)
        tablero_pvp._introducir_barco_en_tablero(Barco("Lancha", 2, "L", True), 0, 0)
        assert tablero_pvp._puede_colocarse(barco, x, y) == esperado
        

    def test_todos_colocados(self):
        """Comprueba si se han colocado todos cada vez que se coloca un barco"""
        barcos = [
            Barco("Lancha", 2, "L", True),
            Barco("Submarino", 3, "S", True),
            Barco("Destructor", 3, "D", True),
            Barco("Acorazado", 4, "A", True),
            Barco("Portaaviones", 5, "P", True),
        ]

        tablero = Tablero(10, 10, barcos, "~", "X", "O")
        y = 0

        for barco in tablero.barcos:
            assert tablero.todos_colocados() is False
            tablero.colocar_barco_manual(barco, 0, y)
            y += 1

        assert tablero.todos_colocados() is True
        

    def test_recibir_disparo(self, tablero_pvp):
        """Comprueba los diferentes resultados de un disparo"""
        barco = Barco("Lancha", 2, "L", True)
        tablero_pvp.colocar_barco_manual(barco, 0, 0)
        assert tablero_pvp.recibir_disparo(0, 0) == [ResultadoDisparo.TOCADO, "X"]
        assert tablero_pvp.recibir_disparo(1, 0) == [ResultadoDisparo.HUNDIDO, "X"]
        assert tablero_pvp.recibir_disparo(0, 0) == [ResultadoDisparo.REPETIDO, "X"]
        assert tablero_pvp.recibir_disparo(1, 0) == [ResultadoDisparo.REPETIDO, "X"]
        assert tablero_pvp.recibir_disparo(-5, 0) == [ResultadoDisparo.INVALIDO, ""]
        assert tablero_pvp.recibir_disparo(7, 11) == [ResultadoDisparo.INVALIDO, ""]
        assert tablero_pvp.recibir_disparo(2, 5) == [ResultadoDisparo.AGUA, "O"]
        assert tablero_pvp.recibir_disparo(4, 7) == [ResultadoDisparo.AGUA, "O"]
    
    
    @pytest.mark.parametrize("x, y, esperado", [
        (1, 1, True),
        ("1", "1", False),
        (2, 2, True),
        (2, 10, False),
        (-3, 3, False),
        (8, 8, True),
        ("8", 8, False),
        (8, "8", False)
    ])
    def test_coordenadas_validas(self, tablero_pvp, x, y, esperado):
        """Comprueba si las coordenadas están dentro del tablero y son de tipo entero"""
        assert tablero_pvp._coordenadas_validas(x, y) == esperado
    
    # todo ver_tablero()
    # todo get_casillas()
    # todo get_una_casilla()
    # todo todos_hundidos()