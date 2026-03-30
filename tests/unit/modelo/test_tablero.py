import pytest
from modelo.board import Tablero
from modelo.ship import Barco
from modelo.result import ResultadoDisparo

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def barcos():
    """Proporciona una lista de barcos de prueba con distintos tamaños y orientación horizontal."""
    return [
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True),
        Barco("Destructor", 3, "D", True),
        Barco("Acorazado", 4, "A", True),
        Barco("Portaaviones", 5, "P", True),
    ]


@pytest.fixture
def tablero(barcos):
    """Crea un tablero de pruebas."""
    return Tablero(10, 10, barcos, "~", "X", "O")


@pytest.fixture
def tablero_vacio():
    """Crea un tablero vacío de pruebas con los barcos disponibles."""
    barcos = [
        Barco("Lancha", 2, "L", True),
        Barco("Submarino", 3, "S", True),
    ]
    return Tablero(10, 10, barcos, "~", "X", "O")


@pytest.fixture
def tablero_con_barcos(tablero_vacio):
    """Crea un tablero de pruebas con los barcos colocados en posiciones conocidas."""
    y = 0
    for barco in tablero_vacio.barcos:
        tablero_vacio.colocar_barco_manual(barco, 0, y)
        y += 1
    return tablero_vacio

class TestTablero:
    """Test de comportamiento de la clase Tablero"""

    # ============================================================================
    # CONSTRUCTOR
    # ============================================================================
    def test_constructor(self, tablero):
        """Verifica que el constructor inicializa correctamente los atributos del tablero."""
        assert tablero.ancho == 10
        assert tablero.alto == 10
        assert isinstance(tablero.barcos, list)
        assert tablero._caracter_vacio == "~"
        assert tablero._caracter_tocado == "X"
        assert tablero._caracter_agua == "O"
        assert tablero._barcos_colocados == 0

        for fila in tablero.get_todas_las_casillas():
            assert all(celda is None for celda in fila)


    # ============================================================================
    # DISPAROS
    # ============================================================================
    
    @pytest.mark.parametrize("x, y, caracter", [
        (0, 0, "X"),
        (4, 5, "O"),
    ])
    def test_marcar_disparo(self, tablero, x, y, caracter):
        """Comprueba que marcar_disparo guarda el carácter en la casilla indicada."""
        tablero.marcar_disparo(x, y, caracter)
        assert tablero.get_una_casilla(x, y) == caracter
        
        
    def test_disparo_tocado(self, tablero_vacio):
        """Verifica que un disparo sobre un barco devuelve resultado TOCADO."""
        barco = Barco("Lancha", 2, "L", True)
        tablero_vacio.colocar_barco_manual(barco, 0, 0)

        resultado = tablero_vacio.recibir_disparo(0, 0)

        assert resultado == [ResultadoDisparo.TOCADO, "X"]


    def test_disparo_hundido(self, tablero_vacio):
        """Comprueba que un barco se marca como hundido tras recibir todos los impactos."""
        barco = Barco("Lancha", 2, "L", True)
        tablero_vacio.colocar_barco_manual(barco, 0, 0)

        tablero_vacio.recibir_disparo(0, 0)
        resultado = tablero_vacio.recibir_disparo(1, 0)

        assert resultado == [ResultadoDisparo.HUNDIDO, "X"]


    def test_disparo_repetido(self, tablero_vacio):
        """Verifica que disparar dos veces en la misma casilla devuelve REPETIDO."""
        barco = Barco("Lancha", 2, "L", True)
        tablero_vacio.colocar_barco_manual(barco, 0, 0)

        tablero_vacio.recibir_disparo(0, 0)
        resultado = tablero_vacio.recibir_disparo(0, 0)

        assert resultado == [ResultadoDisparo.REPETIDO, "X"]


    @pytest.mark.parametrize("x,y", [
        (-1, 0),
        (0, -1),
        (20, 0),
        (0, 20),
    ])
    def test_disparo_fuera_tablero(self, tablero, x, y):
        """Comprueba que disparar fuera del tablero devuelve resultado INVALIDO."""
        resultado = tablero.recibir_disparo(x, y)
        assert resultado == [ResultadoDisparo.INVALIDO, ""]


    def test_disparo_agua(self, tablero):
        """Verifica que un disparo en una casilla vacía devuelve AGUA."""
        resultado = tablero.recibir_disparo(5, 5)
        assert resultado == [ResultadoDisparo.AGUA, "O"]


    # ============================================================================
    # COLOCACIÓN BARCOS
    # ============================================================================
    
    @pytest.mark.parametrize("barco, x, y, esperado", [
        (Barco("Lancha", 2, "L", True), 0, 0, True),
        (Barco("Submarino", 3, "S", False), 5, 5, True),
        (Barco("Destructor", 3, "D", True), 9, 0, False),
    ])
    def test_colocar_barco_manual(self, tablero, barco, x, y, esperado):
        """Valida que colocar_barco_manual coloca el barco solo si la posición es válida."""
        resultado = tablero.colocar_barco_manual(barco, x, y)
        assert resultado is esperado


    def test_colocar_barco_aleatorio(self, tablero, barcos):
        """Comprueba que los barcos pueden colocarse aleatoriamente en el tablero."""
        for barco in barcos:
            assert tablero.colocar_barco_aleatorio(barco)

        assert tablero._barcos_colocados == len(barcos)


    # ============================================================================
    # MOSTRAR TABLEROS
    # ============================================================================

    def test_ver_tablero_muestra_barcos(self, tablero_con_barcos):
        """Verifica que ver_tablero muestra los caracteres de los barcos colocados."""
        vista = tablero_con_barcos.ver_tablero()

        assert vista[0][0] == "L"
        assert vista[0][1] == "L"
        assert vista[1][0] == "S"
        assert vista[1][1] == "S"
        assert vista[1][2] == "S"


    def test_ver_tablero_muestra_disparos(self, tablero_con_barcos):
        """Comprueba que ver_tablero refleja los disparos realizados en el tablero."""
        tablero_con_barcos.marcar_disparo(0, 0, "X")
        tablero_con_barcos.marcar_disparo(5, 5, "O")

        vista = tablero_con_barcos.ver_tablero()

        assert vista[0][0] == "X"
        assert vista[5][5] == "O"
        

    def test_ver_tablero_rival_oculta_barcos(self, tablero_con_barcos):
        """Verifica que ver_tablero_rival oculta los barcos y muestra solo casillas vacías."""
        vista = tablero_con_barcos.ver_tablero_rival()

        for fila in vista:
            for celda in fila:
                assert celda == "~"


    def test_ver_tablero_rival_muestra_disparos(self, tablero_con_barcos):
        """Comprueba que ver_tablero_rival muestra únicamente los disparos realizados."""
        tablero_con_barcos.marcar_disparo(0, 0, "X")
        tablero_con_barcos.marcar_disparo(4, 4, "O")

        vista = tablero_con_barcos.ver_tablero_rival()

        assert vista[0][0] == "X"
        assert vista[4][4] == "O"
        
    
    # ============================================================================
    # GET CASILLAS DE TABLERO
    # ============================================================================
    
    def test_get_todas_las_casillas(self, tablero_con_barcos):
        """Comprueba que get_todas_las_casillas devuelve la matriz completa del tablero."""
        casillas = tablero_con_barcos.get_todas_las_casillas()

        assert isinstance(casillas[0][0], Barco)
        assert casillas[5][5] is None


    def test_get_una_casilla(self, tablero_con_barcos):
        """Verifica que get_una_casilla devuelve el contenido correcto de una posición."""
        assert isinstance(tablero_con_barcos.get_una_casilla(0, 0), Barco)
        assert tablero_con_barcos.get_una_casilla(5, 5) is None


    # ============================================================================
    # ESTADOS
    # ============================================================================
    
    def test_todos_colocados(self, tablero):
        """Comprueba que todos_colocados devuelve True cuando todos los barcos están en el tablero."""
        y = 0

        for barco in tablero.barcos:
            assert not tablero.todos_colocados()
            tablero.colocar_barco_manual(barco, 0, y)
            y += 1

        assert tablero.todos_colocados()


    def test_todos_hundidos(self, tablero_vacio):
        """Verifica que todos_hundidos devuelve True cuando todos los barcos han sido destruidos."""
        y = 0

        for barco in tablero_vacio.barcos:
            tablero_vacio.colocar_barco_manual(barco, 0, y)
            y += 1

        assert not tablero_vacio.todos_hundidos()

        tablero_vacio.recibir_disparo(0, 0)
        tablero_vacio.recibir_disparo(1, 0)

        tablero_vacio.recibir_disparo(0, 1)
        tablero_vacio.recibir_disparo(1, 1)
        tablero_vacio.recibir_disparo(2, 1)

        assert tablero_vacio.todos_hundidos()