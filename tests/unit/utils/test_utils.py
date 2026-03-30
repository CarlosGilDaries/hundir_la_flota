import pytest
import logging
import os
from unittest.mock import patch, MagicMock, AsyncMock
from utils.utils import Util
from utils.exceptions import VolverAlMenu, SalirDelPrograma
from utils.log import configurar_logger
from utils.log_decorator import log_async


class TestUtilOpcionValida:
    """Tests para la validación de opciones de la clase Util."""
    
    @pytest.mark.parametrize("valor, opcion_maxima, esperado", [
        ("2", 10, True),
        ("0", 10, True),
        ("10", 10, True),
        ("-2", 10, False),
        ("12", 10, False),
        ("2.33", 10, False),
        ("H", 10, False),
        ("", 10, False),
        (" 2", 10, False),
        ("2 ", 10, False),
    ])
    def test_opcion_valida_rango_completo(self, valor, opcion_maxima, esperado):
        """Verifica validación con diferentes valores dentro y fuera de rango."""
        assert Util.opcion_valida(valor, opcion_maxima) == esperado

    def test_opcion_valida_cero_minimo(self):
        """Verifica que cero es la opción mínima válida."""
        assert Util.opcion_valida("0", 5) is True

    def test_opcion_valida_negativo_invalido(self):
        """Verifica que números negativos no son válidos."""
        assert Util.opcion_valida("-1", 10) is False

    def test_opcion_valida_igual_maximo(self):
        """Verifica que el valor máximo es incluido en el rango."""
        assert Util.opcion_valida("10", 10) is True

    def test_opcion_valida_mayor_maximo(self):
        """Verifica que valores mayores que máximo no son válidos."""
        assert Util.opcion_valida("11", 10) is False

    def test_opcion_valida_decimal_invalido(self):
        """Verifica que números decimales no son válidos."""
        assert Util.opcion_valida("2.5", 10) is False

    def test_opcion_valida_letra_invalida(self):
        """Verifica que letras no son válidas."""
        assert Util.opcion_valida("a", 10) is False

    def test_opcion_valida_especial_invalido(self):
        """Verifica que caracteres especiales no son válidos."""
        assert Util.opcion_valida("!", 10) is False


class TestUtilEsNumeroEntero:
    """Tests para validación de números enteros."""
    
    @pytest.mark.parametrize("valor, esperado", [
        ("2", True),
        ("0", True),
        ("-5", True),
        ("1000", True),
        ("2.33", False),
        ("H", False),
        ("2a", False),
        ("", False),
    ])
    def test_es_numero_entero_rango_completo(self, valor, esperado):
        """Verifica identificación de números enteros para valores variados."""
        assert Util.es_numero_entero(valor) == esperado

    def test_es_numero_entero_positivo(self):
        """Verifica que números positivos son identificados."""
        assert Util.es_numero_entero("123") is True

    def test_es_numero_entero_negativo(self):
        """Verifica que números negativos son identificados."""
        assert Util.es_numero_entero("-123") is True

    def test_es_numero_entero_cero(self):
        """Verifica que cero es identificado como número entero."""
        assert Util.es_numero_entero("0") is True

    def test_es_numero_entero_decimal(self):
        """Verifica que decimales no son números enteros."""
        assert Util.es_numero_entero("3.14") is False

    def test_es_numero_entero_vacio(self):
        """Verifica que string vacío no es número entero."""
        assert Util.es_numero_entero("") is False

    def test_es_numero_entero_letra(self):
        """Verifica que letras no son números enteros."""
        assert Util.es_numero_entero("abc") is False

    def test_es_numero_entero_mezcla(self):
        """Verifica que mezcla de letra y número no es válida."""
        assert Util.es_numero_entero("12a") is False


class TestExcepcionesCustom:
    """Tests para excepciones personalizadas."""
    
    def test_excepcion_volver_al_menu_se_lanza(self):
        """Verifica que VolverAlMenu se puede lanzar."""
        with pytest.raises(VolverAlMenu):
            raise VolverAlMenu()

    def test_excepcion_volver_al_menu_es_exception(self):
        """Verifica que VolverAlMenu hereda de Exception."""
        assert issubclass(VolverAlMenu, Exception)

    def test_excepcion_volver_al_menu_con_mensaje(self):
        """Verifica que VolverAlMenu acepta un mensaje."""
        mensaje = "Volviendo al menú"
        with pytest.raises(VolverAlMenu, match=mensaje):
            raise VolverAlMenu(mensaje)

    def test_excepcion_salir_del_programa_se_lanza(self):
        """Verifica que SalirDelPrograma se puede lanzar."""
        with pytest.raises(SalirDelPrograma):
            raise SalirDelPrograma()

    def test_excepcion_salir_del_programa_es_exception(self):
        """Verifica que SalirDelPrograma hereda de Exception."""
        assert issubclass(SalirDelPrograma, Exception)

    def test_excepcion_salir_del_programa_con_mensaje(self):
        """Verifica que SalirDelPrograma acepta un mensaje."""
        mensaje = "Saliendo del programa"
        with pytest.raises(SalirDelPrograma, match=mensaje):
            raise SalirDelPrograma(mensaje)

    def test_excepciones_distintas(self):
        """Verifica que ambas excepciones se pueden distinguir."""
        with pytest.raises(VolverAlMenu):
            raise VolverAlMenu()
        
        with pytest.raises(SalirDelPrograma):
            raise SalirDelPrograma()


class TestConfigurarLogger:
    """Tests para la función configurar_logger."""
    
    @pytest.fixture(autouse=True)
    def limpiar_loggers(self):
        """Limpia todos los loggers de prueba después de cada test."""
        yield
        # Limpiar handlers de todos los loggers de prueba
        for nombre in ["test_logger_custom", "test_console", "test_file", "test_level", "test_no_duplica", "test_singleton", "test_cleanup"]:
            logger = logging.getLogger(nombre)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
    
    def test_configurar_logger_retorna_logger(self):
        """Verifica que configurar_logger retorna un objeto logger."""
        logger = configurar_logger()
        assert isinstance(logger, logging.Logger)

    def test_configurar_logger_nombre_personalizado(self):
        """Verifica que se puede especificar nombre personalizado."""
        nombre = "test_logger_custom"
        logger = configurar_logger(nombre=nombre)
        assert logger.name == nombre

    def test_configurar_logger_archivo_predeterminado(self):
        """Verifica que utiliza archivo predeterminado."""
        logger = configurar_logger(nombre="test_default_file")
        assert len([h for h in logger.handlers if isinstance(h, logging.FileHandler)]) > 0

    def test_configurar_logger_tiene_console_handler(self):
        """Verifica que el logger tiene handler para consola."""
        logger = configurar_logger(nombre="test_console")
        # Buscar StreamHandler que no sea FileHandler
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
        assert len(console_handlers) > 0

    def test_configurar_logger_tiene_file_handler(self):
        """Verifica que el logger tiene handler para archivo."""
        logger = configurar_logger(nombre="test_file")
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_configurar_logger_no_duplica_handlers(self):
        """Verifica que no duplica handlers en llamadas sucesivas."""
        nombre = "test_no_duplica"
        logger1 = configurar_logger(nombre=nombre)
        handlers_1 = len(logger1.handlers)
        
        logger2 = configurar_logger(nombre=nombre)
        handlers_2 = len(logger2.handlers)
        
        assert handlers_1 == handlers_2

    def test_configurar_logger_nivel_info(self):
        """Verifica que el nivel de log es INFO."""
        logger = configurar_logger(nombre="test_level")
        assert logger.level == logging.INFO

    def test_configurar_logger_misma_instancia(self):
        """Verifica que devuelve la misma instancia para igual nombre."""
        nombre = "test_singleton"
        logger1 = configurar_logger(nombre=nombre)
        logger2 = configurar_logger(nombre=nombre)
        
        assert logger1 is logger2

    def test_configurar_logger_consola_tiene_formato(self):
        """Verifica que el handler de consola tiene formato."""
        logger = configurar_logger(nombre="test_formato")
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
        assert len(console_handlers) > 0
        assert console_handlers[0].formatter is not None

    def test_configurar_logger_puede_registrar_mensajes(self):
        """Verifica que puede registrar mensajes correctamente."""
        logger = configurar_logger(nombre="test_log_messages")
        # No debe lanzar excepción
        logger.info("Mensaje de prueba")
        assert True


class TestLogAsyncDecorador:
    """Tests para el decorador log_async."""
    
    @pytest.mark.asyncio
    async def test_log_async_ejecuta_funcion_correctamente(self):
        """Verifica que la función decorada se ejecuta."""
        @log_async
        async def funcion_prueba():
            return "resultado"
        
        resultado = await funcion_prueba()
        assert resultado == "resultado"

    @pytest.mark.asyncio
    async def test_log_async_preserva_argumentos_posicionales(self):
        """Verifica que se conservan argumentos posicionales."""
        @log_async
        async def sumar(a, b):
            return a + b
        
        resultado = await sumar(2, 3)
        assert resultado == 5

    @pytest.mark.asyncio
    async def test_log_async_preserva_argumentos_nombrados(self):
        """Verifica que se conservan argumentos nombrados."""
        @log_async
        async def saludar(nombre, edad=20):
            return f"{nombre} tiene {edad}"
        
        resultado = await saludar("Juan", edad=25)
        assert resultado == "Juan tiene 25"

    @pytest.mark.asyncio
    async def test_log_async_preserva_nombre_funcion(self):
        """Verifica que el decorador conserva el name de la función."""
        @log_async
        async def funcion_especial():
            pass
        
        assert funcion_especial.__name__ == "funcion_especial"

    @pytest.mark.asyncio
    async def test_log_async_captura_excepcion_y_la_propaga(self):
        """Verifica que captura excepciones y las propaga."""
        @log_async
        async def funcion_con_error():
            raise ValueError("Error de prueba")
        
        with pytest.raises(ValueError, match="Error de prueba"):
            await funcion_con_error()

    @pytest.mark.asyncio
    async def test_log_async_registra_error(self):
        """Verifica que registra errores en el logger."""
        with patch('utils.log_decorator.logger') as logger_mock:
            @log_async
            async def funcion_falla():
                raise RuntimeError("Error esperado")
            
            try:
                await funcion_falla()
            except RuntimeError:
                pass
            
            logger_mock.error.assert_called()

    @pytest.mark.asyncio
    async def test_log_async_con_resultado_none(self):
        """Verifica que maneja funciones que retornan None."""
        @log_async
        async def no_retorna():
            pass
        
        resultado = await no_retorna()
        assert resultado is None

    @pytest.mark.asyncio
    async def test_log_async_con_excepcion_y_mensaje(self):
        """Verifica mensaje de error en excepción."""
        with patch('utils.log_decorator.logger') as logger_mock:
            @log_async
            async def lanza_error():
                raise KeyError("clave_perdida")
            
            try:
                await lanza_error()
            except KeyError:
                pass
            
            # Verificar que se registró el error
            assert logger_mock.error.called

    @pytest.mark.asyncio
    async def test_log_async_con_multiples_argumentos(self):
        """Verifica con varios argumentos posicionales y nombrados."""
        @log_async
        async def func_compleja(a, b, c, d=10, e=20):
            return a + b + c + d + e
        
        resultado = await func_compleja(1, 2, 3, d=5, e=10)
        assert resultado == 21

    @pytest.mark.asyncio
    async def test_log_async_preserva_tipo_retorno(self):
        """Verifica que preserva tipos de retorno correctamente."""
        @log_async
        async def retorna_lista():
            return [1, 2, 3]
        
        resultado = await retorna_lista()
        assert isinstance(resultado, list)
        assert resultado == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_log_async_preserva_diccionario_retorno(self):
        """Verifica que preserva diccionarios en retorno."""
        @log_async
        async def retorna_dict():
            return {"clave": "valor"}
        
        resultado = await retorna_dict()
        assert isinstance(resultado, dict)
        assert resultado["clave"] == "valor"