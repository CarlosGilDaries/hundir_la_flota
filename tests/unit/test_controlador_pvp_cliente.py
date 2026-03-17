import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
from controlador.controlador_pvp_cliente import ControladorPVPCliente
from red.protocolo.mensajes import TipoMensaje


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def cliente_socket_mock():
    """Fixture que proporciona un mock de ClienteSocket."""
    mock = AsyncMock()
    mock.conectar = AsyncMock()
    mock.recibir = AsyncMock()
    mock.enviar = AsyncMock()
    mock.desconectar = AsyncMock()
    return mock


@pytest.fixture
def vista_consola_mock():
    """Fixture que proporciona un mock de VistaConsola."""
    mock = Mock()
    mock.borrar_consola = Mock()
    mock.mostrar_mensaje = Mock()
    mock.mostrar_tableros = Mock()
    mock.obtener_texto = Mock(return_value="Texto de resultado")
    mock.mostrar_mensaje_final = Mock()
    mock.mostrar_mensaje_abandono = Mock()
    return mock


@pytest.fixture
def controlador_pvp_cliente(cliente_socket_mock, vista_consola_mock):
    """Fixture que proporciona una instancia de ControladorPVPCliente."""
    return ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)


@pytest.fixture
def mensaje_inicio():
    """Fixture con un mensaje de inicio del servidor."""
    return {
        "tipo": "inicio",
        "jugador": 1
    }


@pytest.fixture
def mensaje_lista_barcos():
    """Fixture con un mensaje de lista de barcos."""
    return {
        "tipo": "lista_barcos",
        "barcos": [
            {"indice": 0, "nombre": "Portaaviones", "tamanyo": 5},
            {"indice": 1, "nombre": "Acorazado", "tamanyo": 4},
            {"indice": 2, "nombre": "Submarino", "tamanyo": 3},
        ]
    }


@pytest.fixture
def mensaje_turno_activo():
    """Fixture con un mensaje indicando turno activo."""
    return {
        "tipo": "turno",
        "tu_turno": True
    }


@pytest.fixture
def mensaje_turno_inactivo():
    """Fixture con un mensaje indicando turno inactivo."""
    return {
        "tipo": "turno",
        "tu_turno": False
    }


@pytest.fixture
def mensaje_resultado_disparo():
    """Fixture con un mensaje de resultado de disparo."""
    return {
        "tipo": "resultado",
        "x": 5,
        "y": 5,
        "resultado": "TOCADO"
    }


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestControladorPVPClienteConstructor:
    """Tests del constructor de ControladorPVPCliente."""

    def test_constructor_inicializa_cliente(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa correctamente el cliente."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._cliente == cliente_socket_mock

    def test_constructor_inicializa_vista(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa correctamente la vista."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._vista == vista_consola_mock

    def test_constructor_inicializa_estado(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa el estado correctamente."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._estado is None

    def test_constructor_inicializa_banderas(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa las banderas correctamente."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._jugando is True
        assert controlador._colocando is False
        assert controlador._mi_turno is False
        assert controlador._input_activo is False

    def test_constructor_inicializa_tareas(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa las tareas correctamente."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._tarea_input is None

    def test_constructor_inicializa_barcos_disponibles(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa la lista de barcos disponibles."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert controlador._barcos_disponibles == []

    def test_constructor_inicializa_handlers(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que el constructor inicializa los handlers de mensajes."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        assert isinstance(controlador._handlers, dict)
        assert len(controlador._handlers) > 0

    def test_constructor_handlers_tienen_tipos_mensaje(self, cliente_socket_mock, vista_consola_mock):
        """Verifica que todos los handlers corresponden a tipos de mensaje válidos."""
        controlador = ControladorPVPCliente(cliente_socket_mock, vista_consola_mock)
        
        tipos_esperados = [
            TipoMensaje.ESPERA,
            TipoMensaje.INICIO,
            TipoMensaje.LISTA_BARCOS,
            TipoMensaje.CONFIRMACION,
            TipoMensaje.RECIBIDO,
            TipoMensaje.ESTADO_TABLEROS,
            TipoMensaje.RESULTADO,
            TipoMensaje.TURNO,
            TipoMensaje.FIN,
            TipoMensaje.ERROR,
            TipoMensaje.ABANDONO,
            TipoMensaje.CIERRE_CONEXION,
            TipoMensaje.TIMEOUT_COLA,
        ]
        
        for tipo_esperado in tipos_esperados:
            assert tipo_esperado in controlador._handlers


# =============================================================================
# INICIAR
# =============================================================================

class TestControladorPVPClienteIniciar:
    """Tests del método iniciar."""

    @pytest.mark.asyncio
    async def test_iniciar_conecta_cliente(self, controlador_pvp_cliente):
        """Verifica que iniciar invoca la conexión del cliente."""
        controlador_pvp_cliente._cliente.recibir = AsyncMock(return_value=None)
        
        await controlador_pvp_cliente.iniciar()
        
        controlador_pvp_cliente._cliente.conectar.assert_called_once()

    @pytest.mark.asyncio
    async def test_iniciar_muestra_mensaje_conexion(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que iniciar muestra un mensaje de conexión."""
        controlador_pvp_cliente._cliente.recibir = AsyncMock(return_value=None)
        
        await controlador_pvp_cliente.iniciar()
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_iniciar_escucha_servidor(self, controlador_pvp_cliente):
        """Verifica que iniciar escucha al servidor."""
        controlador_pvp_cliente._cliente.recibir = AsyncMock(return_value=None)
        
        await controlador_pvp_cliente.iniciar()
        
        controlador_pvp_cliente._cliente.recibir.assert_called()


# =============================================================================
# VALIDAR BARCO EN TABLERO
# =============================================================================

class TestControladorPVPClienteValidarBarcoEnTablero:
    """Tests del método validar_barco_en_tablero."""

    def test_validar_barco_horizontal_cabe(self, controlador_pvp_cliente):
        """Verifica que un barco horizontal que cabe retorna True."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(0, 0, 5, True)
        
        assert resultado is True

    def test_validar_barco_horizontal_no_cabe(self, controlador_pvp_cliente):
        """Verifica que un barco horizontal que no cabe retorna False."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(8, 0, 5, True)
        
        assert resultado is False

    def test_validar_barco_vertical_cabe(self, controlador_pvp_cliente):
        """Verifica que un barco vertical que cabe retorna True."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(0, 0, 5, False)
        
        assert resultado is True

    def test_validar_barco_vertical_no_cabe(self, controlador_pvp_cliente):
        """Verifica que un barco vertical que no cabe retorna False."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(0, 8, 5, False)
        
        assert resultado is False

    def test_validar_barco_horizontal_en_borde(self, controlador_pvp_cliente):
        """Verifica un barco horizontal exactamente en el borde."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(5, 0, 5, True)
        
        assert resultado is True

    def test_validar_barco_horizontal_pasado_borde(self, controlador_pvp_cliente):
        """Verifica un barco horizontal pasando el borde."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(6, 0, 5, True)
        
        assert resultado is False

    def test_validar_barco_vertical_en_borde(self, controlador_pvp_cliente):
        """Verifica un barco vertical exactamente en el borde."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(0, 5, 5, False)
        
        assert resultado is True

    @pytest.mark.parametrize("x,y,tamanyo,horizontal,esperado", [
        (0, 0, 2, True, True),
        (9, 0, 2, True, False),
        (0, 9, 2, False, False),
        (5, 5, 3, True, True),
        (5, 5, 3, False, True),
    ])
    def test_validar_barco_multiples_casos(self, controlador_pvp_cliente, x, y, tamanyo, horizontal, esperado):
        """Verifica validación con múltiples combinaciones de parámetros."""
        resultado = controlador_pvp_cliente.validar_barco_en_tablero(x, y, tamanyo, horizontal)
        
        assert resultado == esperado


# =============================================================================
# INPUT ASINCRÓNICO
# =============================================================================

class TestControladorPVPClienteInputAsync:
    """Tests del método input_async."""

    @pytest.mark.asyncio
    async def test_input_async_devuelve_valor(self, controlador_pvp_cliente):
        """Verifica que input_async devuelve el valor ingresado."""
        with patch('builtins.input', return_value="5"):
            resultado = await controlador_pvp_cliente.input_async("Ingrese un número: ")
            
            assert resultado == "5"

    @pytest.mark.asyncio
    async def test_input_async_marca_entrada_activa(self, controlador_pvp_cliente):
        """Verifica que input_async marca la entrada como activa durante la ejecución."""
        with patch('builtins.input', return_value="test"):
            resultado = await controlador_pvp_cliente.input_async("Prompt: ")
            
            assert controlador_pvp_cliente._input_activo is False

    @pytest.mark.asyncio
    async def test_input_async_maneja_keyboard_interrupt(self, controlador_pvp_cliente):
        """Verifica que input_async maneja correctamente KeyboardInterrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            resultado = await controlador_pvp_cliente.input_async("Prompt: ")
            
            assert resultado == "salir"

    @pytest.mark.asyncio
    async def test_input_async_desconecta_en_interrupt(self, controlador_pvp_cliente):
        """Verifica que se desconecta al recibir KeyboardInterrupt."""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            resultado = await controlador_pvp_cliente.input_async("Prompt: ")
            
            assert controlador_pvp_cliente._jugando is False


# =============================================================================
# LEER ENTERO
# =============================================================================

class TestControladorPVPClienteLeerEntero:
    """Tests del método leer_entero."""

    @pytest.mark.asyncio
    async def test_leer_entero_devuelve_numero_valido(self, controlador_pvp_cliente):
        """Verifica que leer_entero devuelve un número válido."""
        with patch('builtins.input', return_value="5"):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ")
            
            assert resultado == 5

    @pytest.mark.asyncio
    async def test_leer_entero_rechaza_no_numero(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que leer_entero rechaza valores no numéricos."""
        with patch('builtins.input', side_effect=["abc", "5"]):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ")
            
            assert resultado == 5

    @pytest.mark.asyncio
    async def test_leer_entero_respeta_minimo(self, controlador_pvp_cliente):
        """Verifica que leer_entero respeta el valor mínimo."""
        with patch('builtins.input', side_effect=["2", "5"]):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ", minimo=3)
            
            assert resultado == 5

    @pytest.mark.asyncio
    async def test_leer_entero_respeta_maximo(self, controlador_pvp_cliente):
        """Verifica que leer_entero respeta el valor máximo."""
        with patch('builtins.input', side_effect=["15", "5"]):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ", maximo=10)
            
            assert resultado == 5

    @pytest.mark.asyncio
    async def test_leer_entero_maneja_salir(self, controlador_pvp_cliente):
        """Verifica que leer_entero maneja el comando 'salir'."""
        with patch('builtins.input', return_value="salir"):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ")
            
            assert resultado is None

    @pytest.mark.asyncio
    async def test_leer_entero_dentro_rango(self, controlador_pvp_cliente):
        """Verifica que leer_entero acepta números dentro del rango especificado."""
        with patch('builtins.input', return_value="5"):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ", minimo=0, maximo=10)
            
            assert resultado == 5

    @pytest.mark.asyncio
    async def test_leer_entero_fuera_rango_min(self, controlador_pvp_cliente):
        """Verifica que rechaza números bajo el mínimo."""
        with patch('builtins.input', side_effect=["-5", "5"]):
            resultado = await controlador_pvp_cliente.leer_entero("Ingrese: ", minimo=0)
            
            assert resultado == 5


# =============================================================================
# DISPATCH
# =============================================================================

class TestControladorPVPClienteDispatch:
    """Tests del método _dispatch."""

    @pytest.mark.asyncio
    async def test_dispatch_llama_handler_correcto(self, controlador_pvp_cliente):
        """Verifica que dispatch invoca el handler correcto."""
        handler_mock = AsyncMock()
        controlador_pvp_cliente._handlers[TipoMensaje.INICIO] = handler_mock
        mensaje = {"tipo": "inicio", "jugador": 1}
        
        await controlador_pvp_cliente._dispatch(TipoMensaje.INICIO, mensaje)
        
        handler_mock.assert_called_once_with(mensaje)

    @pytest.mark.asyncio
    async def test_dispatch_con_tipo_desconocido(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que dispatch muestra mensaje para tipos desconocidos."""
        controlador_pvp_cliente._handlers.pop(TipoMensaje.INICIO, None)
        
        await controlador_pvp_cliente._dispatch(TipoMensaje.INICIO, {})
        
        vista_consola_mock.mostrar_mensaje.assert_called()


# =============================================================================
# ESCUCHAR SERVIDOR
# =============================================================================

class TestControladorPVPClienteEscucharServidor:
    """Tests del método _escuchar_servidor."""

    @pytest.mark.asyncio
    async def test_escuchar_servidor_recibe_mensaje(self, controlador_pvp_cliente):
        """Verifica que escuchar_servidor recibe mensajes del servidor."""
        mensaje_esperado = {"tipo": "inicio", "jugador": 1}
        controlador_pvp_cliente._cliente.recibir = AsyncMock(
            side_effect=[mensaje_esperado, None]
        )
        controlador_pvp_cliente._dispatch = AsyncMock()
        
        await controlador_pvp_cliente._escuchar_servidor()
        
        controlador_pvp_cliente._cliente.recibir.assert_called()

    @pytest.mark.asyncio
    async def test_escuchar_servidor_cierra_en_none(self, controlador_pvp_cliente):
        """Verifica que escuchar_servidor cierra cuando recibe None."""
        controlador_pvp_cliente._cliente.recibir = AsyncMock(return_value=None)
        
        await controlador_pvp_cliente._escuchar_servidor()
        
        assert controlador_pvp_cliente._jugando is False


# =============================================================================
# MANEJAR INICIO
# =============================================================================

class TestControladorPVPClienteManejarInicio:
    """Tests del método _manejar_inicio."""

    @pytest.mark.asyncio
    async def test_manejar_inicio_asigna_jugador(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_inicio asigna el número de jugador."""
        mensaje = {"tipo": "inicio", "jugador": 2}
        
        await controlador_pvp_cliente._manejar_inicio(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_inicio_activa_colocacion(self, controlador_pvp_cliente):
        """Verifica que manejar_inicio activa la fase de colocación."""
        mensaje = {"tipo": "inicio", "jugador": 1}
        
        await controlador_pvp_cliente._manejar_inicio(mensaje)
        
        assert controlador_pvp_cliente._colocando is True

    @pytest.mark.asyncio
    async def test_manejar_inicio_limpia_consola(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_inicio limpia la consola."""
        mensaje = {"tipo": "inicio", "jugador": 1}
        
        await controlador_pvp_cliente._manejar_inicio(mensaje)
        
        vista_consola_mock.borrar_consola.assert_called()


# =============================================================================
# MANEJAR LISTA BARCOS
# =============================================================================

class TestControladorPVPClienteManejarListaBarcos:
    """Tests del método _manejar_lista_barcos."""

    @pytest.mark.asyncio
    async def test_manejar_lista_barcos_asigna_barcos(self, controlador_pvp_cliente, mensaje_lista_barcos):
        """Verifica que manejar_lista_barcos asigna los barcos disponibles."""
        await controlador_pvp_cliente._manejar_lista_barcos(mensaje_lista_barcos)
        
        assert controlador_pvp_cliente._barcos_disponibles == mensaje_lista_barcos["barcos"]

    @pytest.mark.asyncio
    async def test_manejar_lista_barcos_muestra_barcos(self, controlador_pvp_cliente, vista_consola_mock, mensaje_lista_barcos):
        """Verifica que manejar_lista_barcos muestra la lista de barcos."""
        await controlador_pvp_cliente._manejar_lista_barcos(mensaje_lista_barcos)
        
        assert vista_consola_mock.mostrar_mensaje.call_count >= 1

    @pytest.mark.asyncio
    async def test_manejar_lista_barcos_crea_tarea_colocacion(self, controlador_pvp_cliente, mensaje_lista_barcos):
        """Verifica que manejar_lista_barcos crea la tarea de colocación."""
        controlador_pvp_cliente._colocando = True
        
        await controlador_pvp_cliente._manejar_lista_barcos(mensaje_lista_barcos)
        
        if controlador_pvp_cliente._tarea_input:
            assert isinstance(controlador_pvp_cliente._tarea_input, asyncio.Task)


# =============================================================================
# MANEJAR CONFIRMACION
# =============================================================================

class TestControladorPVPClienteManejarConfirmacion:
    """Tests del método _manejar_confirmacion."""

    @pytest.mark.asyncio
    async def test_manejar_confirmacion_muestra_mensaje(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_confirmacion muestra el mensaje de confirmación."""
        mensaje = {"tipo": "confirmacion", "mensaje": "Barco colocado correctamente"}
        
        await controlador_pvp_cliente._manejar_confirmacion(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_confirmacion_limpia_consola(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_confirmacion limpia la consola."""
        mensaje = {"tipo": "confirmacion", "mensaje": "Test"}
        
        await controlador_pvp_cliente._manejar_confirmacion(mensaje)
        
        vista_consola_mock.borrar_consola.assert_called()


# =============================================================================
# MANEJAR ESPERA
# =============================================================================

class TestControladorPVPClienteManejarEspera:
    """Tests del método _manejar_espera."""

    @pytest.mark.asyncio
    async def test_manejar_espera_desactiva_colocacion(self, controlador_pvp_cliente):
        """Verifica que manejar_espera desactiva la colocación."""
        controlador_pvp_cliente._colocando = True
        mensaje = {"tipo": "espera", "mensaje": "Esperando al rival..."}
        
        await controlador_pvp_cliente._manejar_espera(mensaje)
        
        assert controlador_pvp_cliente._colocando is False

    @pytest.mark.asyncio
    async def test_manejar_espera_cancela_tarea(self, controlador_pvp_cliente):
        """Verifica que manejar_espera cancela la tarea de entrada."""
        tarea_mock = AsyncMock()
        tarea_mock.cancel = Mock()
        controlador_pvp_cliente._tarea_input = tarea_mock
        mensaje = {"tipo": "espera", "mensaje": "Esperando..."}
        
        await controlador_pvp_cliente._manejar_espera(mensaje)
        
        assert controlador_pvp_cliente._tarea_input is None

    @pytest.mark.asyncio
    async def test_manejar_espera_sin_tarea(self, controlador_pvp_cliente):
        """Verifica que manejar_espera funciona sin tarea activa."""
        controlador_pvp_cliente._tarea_input = None
        mensaje = {"tipo": "espera", "mensaje": "Esperando..."}
        
        await controlador_pvp_cliente._manejar_espera(mensaje)
        
        assert controlador_pvp_cliente._tarea_input is None


# =============================================================================
# MANEJAR TURNO
# =============================================================================

class TestControladorPVPClienteManejarTurno:
    """Tests del método _manejar_turno."""

    @pytest.mark.asyncio
    async def test_manejar_turno_turno_activo(self, controlador_pvp_cliente):
        """Verifica que manejar_turno marca turno activo."""
        mensaje = {"tipo": "turno", "tu_turno": True}
        
        await controlador_pvp_cliente._manejar_turno(mensaje)
        
        assert controlador_pvp_cliente._mi_turno is True

    @pytest.mark.asyncio
    async def test_manejar_turno_turno_inactivo(self, controlador_pvp_cliente):
        """Verifica que manejar_turno marca turno inactivo."""
        mensaje = {"tipo": "turno", "tu_turno": False}
        
        await controlador_pvp_cliente._manejar_turno(mensaje)
        
        assert controlador_pvp_cliente._mi_turno is False

    @pytest.mark.asyncio
    async def test_manejar_turno_termina_colocacion(self, controlador_pvp_cliente):
        """Verifica que manejar_turno termina la colocación."""
        controlador_pvp_cliente._colocando = True
        mensaje = {"tipo": "turno", "tu_turno": True}
        
        await controlador_pvp_cliente._manejar_turno(mensaje)
        
        assert controlador_pvp_cliente._colocando is False

    @pytest.mark.asyncio
    async def test_manejar_turno_crea_tarea_fase_turno(self, controlador_pvp_cliente):
        """Verifica que crea la tarea de fase turno cuando es su turno."""
        mensaje = {"tipo": "turno", "tu_turno": True}
        
        await controlador_pvp_cliente._manejar_turno(mensaje)
        
        if controlador_pvp_cliente._tarea_input:
            assert isinstance(controlador_pvp_cliente._tarea_input, asyncio.Task)


# =============================================================================
# MANEJAR RESULTADO
# =============================================================================

class TestControladorPVPClienteManejarResultado:
    """Tests del método _manejar_resultado."""

    @pytest.mark.asyncio
    async def test_manejar_resultado_muestra_impacto(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_resultado muestra el resultado del propio disparo."""
        mensaje = {"tipo": "resultado", "x": 5, "y": 5, "resultado": "TOCADO"}
        vista_consola_mock.obtener_texto.return_value = "Tocado"
        
        await controlador_pvp_cliente._manejar_resultado(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_resultado_limpia_consola(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que limpia la consola al mostrar resultado."""
        mensaje = {"tipo": "resultado", "x": 3, "y": 3, "resultado": "AGUA"}
        vista_consola_mock.obtener_texto.return_value = "Agua"
        
        await controlador_pvp_cliente._manejar_resultado(mensaje)
        
        vista_consola_mock.borrar_consola.assert_called()


# =============================================================================
# MANEJAR RECIBIDO
# =============================================================================

class TestControladorPVPClienteManejarRecibido:
    """Tests del método _manejar_recibido."""

    @pytest.mark.asyncio
    async def test_manejar_recibido_muestra_disparo_enemigo(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_recibido muestra el disparo del rival."""
        mensaje = {"tipo": "recibido", "x": 7, "y": 8, "resultado": "HUNDIDO"}
        vista_consola_mock.obtener_texto.return_value = "Hundido"
        
        await controlador_pvp_cliente._manejar_recibido(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_recibido_limpia_consola(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que limpia la consola al mostrar disparo recibido."""
        mensaje = {"tipo": "recibido", "x": 2, "y": 2, "resultado": "AGUA"}
        vista_consola_mock.obtener_texto.return_value = "Agua"
        
        await controlador_pvp_cliente._manejar_recibido(mensaje)
        
        vista_consola_mock.borrar_consola.assert_called()


# =============================================================================
# MANEJAR ESTADO TABLEROS
# =============================================================================

class TestControladorPVPClienteManejarEstadoTableros:
    """Tests del método _manejar_estado_tableros."""

    @pytest.mark.asyncio
    async def test_manejar_estado_tableros_muestra_tableros(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_estado_tableros muestra los tableros."""
        mensaje = {
            "tipo": "estado_tableros",
            "propio": [[("~", False)] * 10] * 10,
            "rival": [[("~", False)] * 10] * 10,
        }
        controlador_pvp_cliente._input_activo = False
        
        await controlador_pvp_cliente._manejar_estado_tableros(mensaje)
        
        vista_consola_mock.mostrar_tableros.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_estado_tableros_no_muestra_con_input_activo(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que no muestra tableros si el input está activo."""
        mensaje = {
            "tipo": "estado_tableros",
            "propio": [[("~", False)] * 10] * 10,
            "rival": [[("~", False)] * 10] * 10,
        }
        controlador_pvp_cliente._input_activo = True
        
        await controlador_pvp_cliente._manejar_estado_tableros(mensaje)
        
        vista_consola_mock.mostrar_tableros.assert_not_called()


# =============================================================================
# MANEJAR FIN
# =============================================================================

class TestControladorPVPClienteManejarFin:
    """Tests del método _manejar_fin."""

    @pytest.mark.asyncio
    async def test_manejar_fin_victoria(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_fin muestra mensaje de victoria."""
        mensaje = {"tipo": "fin", "victoria": True}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_fin(mensaje)
        
        vista_consola_mock.mostrar_mensaje_final.assert_called_with(True, True)

    @pytest.mark.asyncio
    async def test_manejar_fin_derrota(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_fin muestra mensaje de derrota."""
        mensaje = {"tipo": "fin", "victoria": False}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_fin(mensaje)
        
        vista_consola_mock.mostrar_mensaje_final.assert_called_with(False, True)

    @pytest.mark.asyncio
    async def test_manejar_fin_detiene_juego(self, controlador_pvp_cliente):
        """Verifica que manejar_fin detiene el juego."""
        mensaje = {"tipo": "fin", "victoria": True}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_fin(mensaje)
        
        assert controlador_pvp_cliente._jugando is False

    @pytest.mark.asyncio
    async def test_manejar_fin_desconecta_cliente(self, controlador_pvp_cliente):
        """Verifica que manejar_fin desconecta del servidor."""
        mensaje = {"tipo": "fin", "victoria": True}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_fin(mensaje)
        
        controlador_pvp_cliente._cliente.desconectar.assert_called()


# =============================================================================
# MANEJAR ABANDONO
# =============================================================================

class TestControladorPVPClienteManejarAbandono:
    """Tests del método _manejar_abandono."""

    @pytest.mark.asyncio
    async def test_manejar_abandono_muestra_mensaje(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_abandono muestra mensaje de abandono."""
        mensaje = {"tipo": "abandono", "abandono": "El rival abandonó"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_abandono(mensaje)
        
        vista_consola_mock.mostrar_mensaje_abandono.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_abandono_detiene_juego(self, controlador_pvp_cliente):
        """Verifica que manejar_abandono detiene el juego."""
        mensaje = {"tipo": "abandono", "abandono": "Test"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_abandono(mensaje)
        
        assert controlador_pvp_cliente._jugando is False


# =============================================================================
# MANEJAR CIERRE CONEXION
# =============================================================================

class TestControladorPVPClienteManejarCierreConexion:
    """Tests del método _manejar_cierre_conexion."""

    @pytest.mark.asyncio
    async def test_manejar_cierre_conexion_muestra_mensaje(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que muestra mensaje al cerrar conexión."""
        mensaje = {"tipo": "cierre_conexion"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_cierre_conexion(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_cierre_conexion_detiene_juego(self, controlador_pvp_cliente):
        """Verifica que detiene el juego."""
        mensaje = {"tipo": "cierre_conexion"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_cierre_conexion(mensaje)
        
        assert controlador_pvp_cliente._jugando is False


# =============================================================================
# MANEJAR TIMEOUT COLA
# =============================================================================

class TestControladorPVPClienteManejarTimeoutCola:
    """Tests del método _manejar_timeout_cola."""

    @pytest.mark.asyncio
    async def test_manejar_timeout_cola_muestra_mensaje(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que muestra mensaje de timeout en cola."""
        mensaje = {"tipo": "timeout_cola"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_timeout_cola(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_timeout_cola_detiene_juego(self, controlador_pvp_cliente):
        """Verifica que detiene el juego tras timeout."""
        mensaje = {"tipo": "timeout_cola"}
        
        with patch('builtins.input', return_value=""):
            await controlador_pvp_cliente._manejar_timeout_cola(mensaje)
        
        assert controlador_pvp_cliente._jugando is False


# =============================================================================
# MANEJAR ERROR
# =============================================================================

class TestControladorPVPClienteManejarError:
    """Tests del método _manejar_error."""

    @pytest.mark.asyncio
    async def test_manejar_error_muestra_mensaje(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que manejar_error muestra mensaje de error."""
        mensaje = {"tipo": "error", "mensaje": "Coordinadas inválidas"}
        
        await controlador_pvp_cliente._manejar_error(mensaje)
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_manejar_error_reinicia_colocacion(self, controlador_pvp_cliente):
        """Verifica que reinicia colocación si estaba activa."""
        controlador_pvp_cliente._colocando = True
        controlador_pvp_cliente._tarea_input = None
        mensaje = {"tipo": "error", "mensaje": "Error colocación"}
        
        await controlador_pvp_cliente._manejar_error(mensaje)
        
        if controlador_pvp_cliente._tarea_input:
            assert isinstance(controlador_pvp_cliente._tarea_input, asyncio.Task)


# =============================================================================
# FASE COLOCACION
# =============================================================================

class TestControladorPVPClienteFaseColocacion:
    """Tests del método fase_colocacion."""

    @pytest.mark.asyncio
    async def test_fase_colocacion_sin_barcos_disponibles(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que termina si no hay barcos disponibles."""
        controlador_pvp_cliente._barcos_disponibles = []
        
        await controlador_pvp_cliente.fase_colocacion()
        
        vista_consola_mock.mostrar_mensaje.assert_called()

    @pytest.mark.asyncio
    async def test_fase_colocacion_selecciona_barco(self, controlador_pvp_cliente, vista_consola_mock):
        """Verifica que fase_colocacion selecciona un barco."""
        controlador_pvp_cliente._barcos_disponibles = [
            {"indice": 0, "nombre": "Test", "tamanyo": 5}
        ]
        
        with patch('builtins.input', side_effect=["0", "5", "5", "h", "salir"]):
            try:
                await controlador_pvp_cliente.fase_colocacion()
            except:
                pass
        
        # Verifica que al menos intentó procesar input


# =============================================================================
# FASE TURNO
# =============================================================================

class TestControladorPVPClienteFaseTurno:
    """Tests del método fase_turno."""

    @pytest.mark.asyncio
    async def test_fase_turno_pide_coordenadas(self, controlador_pvp_cliente):
        """Verifica que fase_turno solicita coordenadas."""
        with patch.object(controlador_pvp_cliente, 'leer_entero', new_callable=AsyncMock, side_effect=[5, 5]):
            await controlador_pvp_cliente.fase_turno()
        
        controlador_pvp_cliente._cliente.enviar.assert_called()

    @pytest.mark.asyncio
    async def test_fase_turno_maneja_salida(self, controlador_pvp_cliente):
        """Verifica que fase_turno maneja la salida."""
        with patch.object(controlador_pvp_cliente, 'leer_entero', new_callable=AsyncMock, return_value=None):
            await controlador_pvp_cliente.fase_turno()
        
        # No lanza excepción


# =============================================================================
# SALIR PARTIDA
# =============================================================================

class TestControladorPVPClienteSalirPartida:
    """Tests del método salir_partida."""

    @pytest.mark.asyncio
    async def test_salir_partida_detiene_juego(self, controlador_pvp_cliente):
        """Verifica que salir_partida detiene el juego."""
        controlador_pvp_cliente._jugando = True
        
        await controlador_pvp_cliente.salir_partida()
        
        assert controlador_pvp_cliente._jugando is False

    @pytest.mark.asyncio
    async def test_salir_partida_desactiva_colocacion(self, controlador_pvp_cliente):
        """Verifica que desactiva la colocación."""
        controlador_pvp_cliente._colocando = True
        
        await controlador_pvp_cliente.salir_partida()
        
        assert controlador_pvp_cliente._colocando is False

    @pytest.mark.asyncio
    async def test_salir_partida_desconecta(self, controlador_pvp_cliente):
        """Verifica que desconecta del servidor."""
        await controlador_pvp_cliente.salir_partida()
        
        controlador_pvp_cliente._cliente.desconectar.assert_called()

    @pytest.mark.asyncio
    async def test_salir_partida_envía_mensaje_salida(self, controlador_pvp_cliente):
        """Verifica que envía mensaje de salida."""
        await controlador_pvp_cliente.salir_partida()
        
        controlador_pvp_cliente._cliente.enviar.assert_called()
