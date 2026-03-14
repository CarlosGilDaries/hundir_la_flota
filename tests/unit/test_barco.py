import pytest
from modelo.barco import Barco


@pytest.fixture(params=[
    ("Lancha", 2, "L", None),
    ("Submarino", 3, "S", False),
    ("Acorazado", 4, "A", True),
    ("Portaaviones", 5, "P", None),
])
def barco(request):
    """Fixture que devuelve distintas instancias de Barco."""
    nombre, tamanyo, caracter, horizontal = request.param
    return Barco(nombre, tamanyo, caracter, horizontal)


class TestBarco:
    """Tests de comportamiento de la clase Barco."""

    def test_constructor_atributos(self, barco):
        """Verifica que los atributos básicos se inicializan correctamente."""
        assert barco.nombre in ["Lancha", "Submarino", "Acorazado", "Portaaviones"]
        assert barco._vida_restante == barco.tamanyo
        assert isinstance(barco.caracter, str)


    def test_constructor_horizontal(self, barco):
        """Comprueba que la orientación inicial es un booleano."""
        assert isinstance(barco.get_horizontal(), bool)


    @pytest.mark.parametrize("horizontal", [True, False])
    def test_set_horizontal(self, barco, horizontal):
        """Verifica que se puede establecer la orientación manualmente."""
        barco.set_horizontal(horizontal)
        assert barco.get_horizontal() is horizontal


    def test_set_horizontal_random(self, barco):
        """Verifica que se asigna orientación aleatoria si no se especifica."""
        barco.set_horizontal(None)
        assert isinstance(barco.get_horizontal(), bool)


    @pytest.mark.parametrize("dimension", [8, 10, 12])
    def test_calcular_maximo(self, barco, dimension):
        """Comprueba el cálculo de la posición máxima del barco."""
        esperado = dimension - barco.tamanyo
        assert barco.calcular_maximo(dimension) == esperado


    def test_recibir_impacto(self, barco):
        """Verifica que la vida restante disminuye al recibir un impacto."""
        vida_inicial = barco._vida_restante
        barco.recibir_impacto()
        assert barco._vida_restante == vida_inicial - 1


    def test_hundido(self, barco):
        """Comprueba que el barco solo se considera hundido cuando su vida es 0."""
        while barco._vida_restante > 0:
            assert barco.hundido() is False
            barco.recibir_impacto()

        assert barco.hundido() is True