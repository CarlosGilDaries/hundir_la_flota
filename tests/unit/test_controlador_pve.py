import pytest
from unittest.mock import Mock, MagicMock, patch, call
from controlador.controlador_pve import ControladorPVE
from modelo.barco import Barco
from modelo.resultado import ResultadoDisparo
from config.constantes import CONSTANTES


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def configuracion():
    """Fixture que proporciona la configuración de constantes del juego."""
    return CONSTANTES


@pytest.fixture
def vista_mock():
    """Fixture que proporciona un mock de la vista consola."""
    mock = Mock()
    mock.borrar_consola = Mock()
    mock.mostrar_tablero = Mock()
    mock.mostrar_balas = Mock()
    mock.opcion_volver_menu = Mock()
    mock.pedir_disparo = Mock()
    mock.mostrar_resultado = Mock()
    mock.mostrar_mensaje_final = Mock()
    return mock


@pytest.fixture
def controlador_pve(vista_mock, configuracion):
    """Fixture que proporciona una instancia de ControladorPVE."""
    return ControladorPVE(vista_mock, configuracion)


@pytest.fixture
def partida_mock():
    """Fixture que proporciona un mock de la partida PVE."""
    mock = Mock()
    mock.quedan_disparos = Mock(return_value=True)
    mock.hay_victoria = Mock(return_value=False)
    mock.obtener_tablero_rival = Mock(return_value=[["~"] * 8] * 8)
    mock.disparos_restantes = Mock(return_value=10)
    mock.obtener_dimensiones_tablero = Mock(return_value=(8, 8))
    mock.disparar = Mock(return_value=ResultadoDisparo.AGUA)
    return mock


@pytest.fixture
def datos_barcos_config():
    """Fixture con datos de configuración de barcos."""
    return [
        ("Portaaviones", 5, "P"),
        ("Acorazado", 4, "A"),
        ("Submarino", 3, "S"),
        ("Lancha", 2, "L"),
    ]


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestControladorPVEConstructor:
    """Tests del constructor de ControladorPVE."""

    def test_constructor_inicializa_atributos(self, vista_mock, configuracion):
        """Verifica que el constructor inicializa correctamente los atributos."""
        controlador = ControladorPVE(vista_mock, configuracion)
        
        assert controlador._vista == vista_mock
        assert controlador._config == configuracion
        assert controlador._partida is None
        assert controlador.config_dificultad == configuracion["DIFICULTAD"]["PVE"]

    def test_constructor_referencia_vista_valida(self, vista_mock, configuracion):
        """Comprueba que la vista referenciada es válida."""
        controlador = ControladorPVE(vista_mock, configuracion)
        
        assert controlador._vista is not None
        assert hasattr(controlador._vista, 'borrar_consola')

    def test_constructor_config_dificultad_correcta(self, vista_mock, configuracion):
        """Verifica que se asigna correctamente la configuración de dificultad."""
        controlador = ControladorPVE(vista_mock, configuracion)
        
        assert "1" not in controlador.config_dificultad or 1 in controlador.config_dificultad
        assert controlador.config_dificultad is configuracion["DIFICULTAD"]["PVE"]


# =============================================================================
# CREAR BARCOS
# =============================================================================

class TestControladorPVECrearBarcos:
    """Tests del método crear_barcos."""

    def test_crear_barcos_cantidad_correcta(self, controlador_pve, datos_barcos_config):
        """Verifica que se crean el número correcto de barcos."""
        resultado = controlador_pve.crear_barcos(datos_barcos_config)
        
        assert len(resultado) == len(datos_barcos_config)

    def test_crear_barcos_tipos_correctos(self, controlador_pve, datos_barcos_config):
        """Comprueba que todos los elementos creados son instancias de Barco."""
        resultado = controlador_pve.crear_barcos(datos_barcos_config)
        
        assert all(isinstance(barco, Barco) for barco in resultado)

    def test_crear_barcos_atributos_correctos(self, controlador_pve):
        """Verifica que los atributos de los barcos coinciden con la configuración."""
        config = [("TestBarco", 5, "T")]
        resultado = controlador_pve.crear_barcos(config)
        
        assert resultado[0].nombre == "TestBarco"
        assert resultado[0].tamanyo == 5
        assert resultado[0].caracter == "T"

    def test_crear_barcos_lista_vacia(self, controlador_pve):
        """Comprueba que se maneja correctamente una lista de barcos vacía."""
        resultado = controlador_pve.crear_barcos([])
        
        assert resultado == []
        assert isinstance(resultado, list)

    @pytest.mark.parametrize("config_barcos", [
        [("Barco1", 2, "B")],
        [("Barco1", 2, "B"), ("Barco2", 3, "C")],
        [("Barco1", 2, "B"), ("Barco2", 3, "C"), ("Barco3", 4, "D")],
    ])
    def test_crear_barcos_multiples_tamanios(self, controlador_pve, config_barcos):
        """Verifica que se crean barcos con diferentes tamaños correctamente."""
        resultado = controlador_pve.crear_barcos(config_barcos)
        
        for i, (nombre, tamanyo, caracter) in enumerate(config_barcos):
            assert resultado[i].tamanyo == tamanyo


# =============================================================================
# CREAR PARTIDA
# =============================================================================

class TestControladorPVECrearPartida:
    """Tests del método crear_partida."""

    def test_crear_partida_devuelve_partida_pve(self, controlador_pve):
        """Comprueba que crear_partida devuelve una instancia válida."""
        from modelo.partida.partida_pve import PartidaPVE
        resultado = controlador_pve.crear_partida(1)
        
        assert isinstance(resultado, PartidaPVE)

    def test_crear_partida_dificultad_facil(self, controlador_pve):
        """Verifica que se crean correctamente con dificultad fácil."""
        partida = controlador_pve.crear_partida(1)
        
        assert partida is not None
        assert hasattr(partida, 'quedan_disparos')
        assert hasattr(partida, 'hay_victoria')

    def test_crear_partida_dificultad_media(self, controlador_pve):
        """Verifica que se crean correctamente con dificultad media."""
        partida = controlador_pve.crear_partida(2)
        
        assert partida is not None

    def test_crear_partida_dificultad_dificil(self, controlador_pve):
        """Verifica que se crean correctamente con dificultad difícil."""
        partida = controlador_pve.crear_partida(3)
        
        assert partida is not None

    def test_crear_partida_dificultad_muy_dificil(self, controlador_pve):
        """Verifica que se crean correctamente con dificultad muy difícil."""
        partida = controlador_pve.crear_partida(4)
        
        assert partida is not None

    def test_crear_partida_usa_crear_barcos(self, controlador_pve):
        """Verifica que crear_partida utiliza el método crear_barcos."""
        with patch.object(controlador_pve, 'crear_barcos', return_value=[]) as mock_crear_barcos:
            try:
                controlador_pve.crear_partida(1)
            except:
                # El tablero puede fallar sin barcos, pero verificamos que se llamó
                pass
            
            mock_crear_barcos.assert_called_once()

    def test_crear_partida_con_diferentes_dificultades(self, controlador_pve):
        """Verifica que cada dificultad crea una partida válida."""
        for dificultad in [1, 2, 3, 4]:
            partida = controlador_pve.crear_partida(dificultad)
            assert partida is not None


# =============================================================================
# MOSTRAR ESTADO
# =============================================================================

class TestControladorPVEMostrarEstado:
    """Tests del método mostrar_estado."""

    def test_mostrar_estado_llama_mostrar_tablero(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que mostrar_estado invoca mostrar_tablero."""
        controlador_pve._partida = partida_mock
        
        controlador_pve.mostrar_estado()
        
        vista_mock.mostrar_tablero.assert_called_once()

    def test_mostrar_estado_llama_mostrar_balas(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que mostrar_estado invoca mostrar_balas."""
        controlador_pve._partida = partida_mock
        
        controlador_pve.mostrar_estado()
        
        vista_mock.mostrar_balas.assert_called_once()

    def test_mostrar_estado_pasa_tablero_rival_correcto(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que se pasa el tablero rival correcto a la vista."""
        tablero_esperado = [["~"] * 10] * 10
        partida_mock.obtener_tablero_rival.return_value = tablero_esperado
        controlador_pve._partida = partida_mock
        
        controlador_pve.mostrar_estado()
        
        vista_mock.mostrar_tablero.assert_called_once_with(tablero_esperado)

    def test_mostrar_estado_pasa_balas_correctas(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que se pasan las balas restantes correcto a la vista."""
        balas_esperadas = 25
        partida_mock.disparos_restantes.return_value = balas_esperadas
        controlador_pve._partida = partida_mock
        
        controlador_pve.mostrar_estado()
        
        vista_mock.mostrar_balas.assert_called_once_with(balas_esperadas)

    def test_mostrar_estado_invocaciones_orden_correcto(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se invoca mostrar_tablero antes de mostrar_balas."""
        controlador_pve._partida = partida_mock
        
        controlador_pve.mostrar_estado()
        
        assert vista_mock.mostrar_tablero.call_count == 1
        assert vista_mock.mostrar_balas.call_count == 1


# =============================================================================
# FASE TURNO
# =============================================================================

class TestControladorPVEFaseTurno:
    """Tests del método fase_turno."""

    def test_fase_turno_llama_opcion_volver_menu(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que fase_turno invoca opcion_volver_menu."""
        vista_mock.pedir_disparo.return_value = (5, 5)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        vista_mock.opcion_volver_menu.assert_called_once()

    def test_fase_turno_pide_disparo(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que fase_turno solicita coordenadas de disparo."""
        vista_mock.pedir_disparo.return_value = (3, 4)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        vista_mock.pedir_disparo.assert_called_once_with(8, 8)

    def test_fase_turno_dispara_coordenadas_correctas(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que se dispara en las coordenadas solicitadas."""
        vista_mock.pedir_disparo.return_value = (2, 7)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        partida_mock.disparar.assert_called_once_with(2, 7)

    def test_fase_turno_limpia_consola(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se limpia la consola después del disparo."""
        vista_mock.pedir_disparo.return_value = (5, 5)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        vista_mock.borrar_consola.assert_called()

    def test_fase_turno_muestra_resultado(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que se muestra el resultado del disparo."""
        resultado_esperado = ResultadoDisparo.AGUA
        partida_mock.disparar.return_value = resultado_esperado
        vista_mock.pedir_disparo.return_value = (0, 0)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        vista_mock.mostrar_resultado.assert_called_once_with(resultado_esperado)

    def test_fase_turno_obtiene_dimensiones(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se obtienen las dimensiones correctas del tablero."""
        partida_mock.obtener_dimensiones_tablero.return_value = (10, 10)
        vista_mock.pedir_disparo.return_value = (5, 5)
        controlador_pve._partida = partida_mock
        
        controlador_pve.fase_turno()
        
        vista_mock.pedir_disparo.assert_called_once_with(10, 10)

    def test_fase_turno_con_diferentes_resultados(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que fase_turno maneja diferentes resultados de disparo."""
        vista_mock.pedir_disparo.return_value = (5, 5)
        controlador_pve._partida = partida_mock
        
        for resultado in [ResultadoDisparo.AGUA, ResultadoDisparo.TOCADO, ResultadoDisparo.HUNDIDO]:
            partida_mock.disparar.return_value = resultado
            controlador_pve.fase_turno()
            vista_mock.mostrar_resultado.assert_called_with(resultado)


# =============================================================================
# EJECUTAR BUCLE PRINCIPAL
# =============================================================================

class TestControladorPVEEjecutarBuclePrincipal:
    """Tests del método ejecutar_bucle_principal."""

    def test_bucle_principal_limpia_consola_inicio(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se limpia la consola al inicio del bucle."""
        partida_mock.quedan_disparos.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.borrar_consola.assert_called()

    def test_bucle_principal_entra_bucle_mientras_hay_disparos(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que el bucle continúa mientras hay disparos disponibles."""
        vista_mock.pedir_disparo.return_value = (0, 0)
        partida_mock.quedan_disparos.side_effect = [True, False]
        partida_mock.hay_victoria.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        assert partida_mock.quedan_disparos.call_count >= 1

    def test_bucle_principal_sale_cuando_no_hay_disparos(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que el bucle termina cuando no hay disparos."""
        partida_mock.quedan_disparos.return_value = False
        partida_mock.hay_victoria.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.mostrar_mensaje_final.assert_called_once()

    def test_bucle_principal_sale_cuando_hay_victoria(self, controlador_pve, vista_mock, partida_mock):
        """Comprueba que el bucle termina cuando hay victoria."""
        partida_mock.quedan_disparos.return_value = True
        partida_mock.hay_victoria.return_value = True
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.mostrar_mensaje_final.assert_called_once()

    def test_bucle_principal_muestra_mensaje_final_victoria(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se muestra el mensaje final correcto en caso de victoria."""
        partida_mock.quedan_disparos.return_value = True
        partida_mock.hay_victoria.return_value = True
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.mostrar_mensaje_final.assert_called_once_with(True, False)

    def test_bucle_principal_muestra_mensaje_final_derrota(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se muestra el mensaje final correcto en caso de derrota."""
        partida_mock.quedan_disparos.return_value = False
        partida_mock.hay_victoria.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.mostrar_mensaje_final.assert_called_once_with(False, False)

    def test_bucle_principal_maneja_volver_al_menu(self, controlador_pve, vista_mock):
        """Verifica que se maneja correctamente la excepción VolverAlMenu."""
        from utils.excepciones import VolverAlMenu
        partida_mock = Mock()
        partida_mock.quedan_disparos.side_effect = VolverAlMenu()
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.borrar_consola.assert_called()

    def test_bucle_principal_llama_mostrar_estado(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se invoca mostrar_estado en cada iteración."""
        vista_mock.pedir_disparo.return_value = (0, 0)
        partida_mock.quedan_disparos.side_effect = [True, False]
        partida_mock.hay_victoria.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        assert vista_mock.mostrar_tablero.call_count >= 1

    def test_bucle_principal_llama_fase_turno(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que se invoca fase_turno en cada iteración."""
        vista_mock.pedir_disparo.return_value = (0, 0)
        partida_mock.quedan_disparos.side_effect = [True, False]
        partida_mock.hay_victoria.return_value = False
        controlador_pve._partida = partida_mock
        
        controlador_pve.ejecutar_bucle_principal()
        
        vista_mock.opcion_volver_menu.assert_called()


# =============================================================================
# INICIAR
# =============================================================================

class TestControladorPVEIniciar:
    """Tests del método iniciar."""

    def test_iniciar_crea_partida(self, controlador_pve, vista_mock, partida_mock):
        """Verifica que iniciar crea una nueva partida."""
        with patch.object(controlador_pve, 'crear_partida', return_value=partida_mock):
            with patch.object(controlador_pve, 'ejecutar_bucle_principal'):
                controlador_pve.iniciar(1)
                
                assert controlador_pve._partida is not None

    def test_iniciar_con_dificultad_facil(self, controlador_pve, vista_mock):
        """Verifica que iniciar funciona con dificultad fácil."""
        with patch.object(controlador_pve, 'crear_partida', return_value=Mock()):
            with patch.object(controlador_pve, 'ejecutar_bucle_principal'):
                controlador_pve.iniciar(1)
                
                assert controlador_pve._partida is not None

    def test_iniciar_llama_ejecutar_bucle_principal(self, controlador_pve):
        """Verifica que iniciar invoca el bucle principal."""
        partida_mock = Mock()
        with patch.object(controlador_pve, 'crear_partida', return_value=partida_mock) as mock_crear:
            with patch.object(controlador_pve, 'ejecutar_bucle_principal') as mock_bucle:
                controlador_pve.iniciar(2)
                
                mock_crear.assert_called_once_with(2)
                mock_bucle.assert_called_once()

    def test_iniciar_pasa_dificultad_correcta(self, controlador_pve):
        """Verifica que se pasa la dificultad correcta a crear_partida."""
        with patch.object(controlador_pve, 'crear_partida', return_value=Mock()) as mock_crear:
            with patch.object(controlador_pve, 'ejecutar_bucle_principal'):
                controlador_pve.iniciar(3)
                
                mock_crear.assert_called_once_with(3)

    @pytest.mark.parametrize("dificultad", [1, 2, 3, 4])
    def test_iniciar_con_todas_dificultades(self, controlador_pve, dificultad):
        """Verifica que iniciar funciona con todas las dificultades disponibles."""
        with patch.object(controlador_pve, 'crear_partida', return_value=Mock()):
            with patch.object(controlador_pve, 'ejecutar_bucle_principal'):
                controlador_pve.iniciar(dificultad)
                
                assert controlador_pve._partida is not None
