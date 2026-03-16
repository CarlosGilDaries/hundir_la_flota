import pytest
from utils.utils import Util

class TestUtils:
    """Clase encargada de testear las validaciones de la clase Util"""
    
    @pytest.mark.parametrize("valor, opcion_maxima, esperado", [
        ("2", 10, True),
        ("-2", 10, False),
        ("12", 10, False),
        ("2.33", 10, False),
        ("H", 10, False)
    ])
    def test_opcion_valida(self, valor, opcion_maxima, esperado):
        """Comprueba se valide correctamente las opciones."""
        assert Util.opcion_valida(valor, opcion_maxima) == esperado
        
    
    @pytest.mark.parametrize("valor, esperado", [
        ("2", True),
        ("2.33", False),
        ("H", False),
    ])
    def test_es_numero_entero(self, valor, esperado):
        """Comprueba que se valide si es número entero."""
        assert Util.es_numero_entero(valor) == esperado