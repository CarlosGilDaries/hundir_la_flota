import pytest
import json
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from red.cliente.cliente_socket import ClienteSocket


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def cliente_socket():
    """Fixture que proporciona una instancia de ClienteSocket."""
    return ClienteSocket("127.0.0.1", 8888)


@pytest.fixture
def lector_mock():
    """Fixture que proporciona un mock de StreamReader."""
    return AsyncMock()


@pytest.fixture
def escritor_mock():
    """Fixture que proporciona un mock de StreamWriter."""
    mock = AsyncMock()
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def mensaje_prueba():
    """Fixture con un mensaje JSON de prueba."""
    return {
        "tipo": "inicio",
        "jugador": 1,
        "estado": "esperando"
    }


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestClienteSocketConstructor:
    """Tests del constructor de ClienteSocket."""

    def test_constructor_inicializa_host(self, cliente_socket):
        """Verifica que el constructor inicializa correctamente el host."""
        assert cliente_socket._host == "127.0.0.1"

    def test_constructor_inicializa_puerto(self, cliente_socket):
        """Verifica que el constructor inicializa correctamente el puerto."""
        assert cliente_socket._puerto == 8888

    def test_constructor_inicializa_reader_none(self, cliente_socket):
        """Verifica que el reader se inicializa como None."""
        assert cliente_socket._reader is None

    def test_constructor_inicializa_writer_none(self, cliente_socket):
        """Verifica que el writer se inicializa como None."""
        assert cliente_socket._writer is None

    @pytest.mark.parametrize("host,puerto", [
        ("localhost", 5000),
        ("192.168.1.100", 9000),
        ("0.0.0.0", 8000),
    ])
    def test_constructor_multiples_hosts_puertos(self, host, puerto):
        """Verifica que el constructor acepta múltiples combinaciones de host/puerto."""
        cliente = ClienteSocket(host, puerto)
        assert cliente._host == host
        assert cliente._puerto == puerto


# =============================================================================
# CONECTAR
# =============================================================================

class TestClienteSocketConectar:
    """Tests del método conectar."""

    @pytest.mark.asyncio
    async def test_conectar_establece_conexion(self, cliente_socket, lector_mock, escritor_mock):
        """Verifica que conectar establece correctamente la conexión."""
        with patch('asyncio.open_connection', return_value=(lector_mock, escritor_mock)):
            await cliente_socket.conectar()
            
            assert cliente_socket._reader == lector_mock
            assert cliente_socket._writer == escritor_mock

    @pytest.mark.asyncio
    async def test_conectar_usa_host_correcto(self, cliente_socket, lector_mock, escritor_mock):
        """Verifica que conectar utiliza el host correcto."""
        with patch('asyncio.open_connection', return_value=(lector_mock, escritor_mock)) as mock_open:
            await cliente_socket.conectar()
            
            mock_open.assert_called_once_with("127.0.0.1", 8888)

    @pytest.mark.asyncio
    async def test_conectar_lanza_exception_si_falla(self, cliente_socket):
        """Verifica que se propaga excepción si la conexión falla."""
        with patch('asyncio.open_connection', side_effect=OSError("Conexión rechazada")):
            with pytest.raises(OSError):
                await cliente_socket.conectar()

    @pytest.mark.asyncio
    async def test_conectar_con_diferentes_puertos(self, lector_mock, escritor_mock):
        """Verifica conexión con diferentes puertos."""
        with patch('asyncio.open_connection', return_value=(lector_mock, escritor_mock)) as mock_open:
            cliente = ClienteSocket("localhost", 5000)
            await cliente.conectar()
            
            mock_open.assert_called_once_with("localhost", 5000)


# =============================================================================
# ENVIAR
# =============================================================================

class TestClienteSocketEnviar:
    """Tests del método enviar."""

    @pytest.mark.asyncio
    async def test_enviar_serializa_json(self, cliente_socket, escritor_mock, mensaje_prueba):
        """Verifica que enviar serializa correctamente el mensaje a JSON."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.enviar(mensaje_prueba)
        
        mensaje_esperado = json.dumps(mensaje_prueba) + "\n"
        escritor_mock.write.assert_called_once_with(mensaje_esperado.encode())

    @pytest.mark.asyncio
    async def test_enviar_codifica_a_bytes(self, cliente_socket, escritor_mock, mensaje_prueba):
        """Verifica que el mensaje se codifica correctamente a bytes."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.enviar(mensaje_prueba)
        
        kwargs = escritor_mock.write.call_args
        mensaje_enviado = kwargs[0][0]
        assert isinstance(mensaje_enviado, bytes)

    @pytest.mark.asyncio
    async def test_enviar_agrega_salto_linea(self, cliente_socket, escritor_mock):
        """Verifica que se agrega salto de línea al final del mensaje."""
        cliente_socket._writer = escritor_mock
        mensaje = {"tipo": "test"}
        
        await cliente_socket.enviar(mensaje)
        
        mensaje_enviado = escritor_mock.write.call_args[0][0].decode()
        assert mensaje_enviado.endswith("\n")

    @pytest.mark.asyncio
    async def test_enviar_llama_drain(self, cliente_socket, escritor_mock, mensaje_prueba):
        """Verifica que se invoca drain después de escribir."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.enviar(mensaje_prueba)
        
        escritor_mock.drain.assert_called_once()

    @pytest.mark.asyncio
    async def test_enviar_multiples_mensajes(self, cliente_socket, escritor_mock):
        """Verifica que se pueden enviar múltiples mensajes secuencialmente."""
        cliente_socket._writer = escritor_mock
        mensajes = [
            {"tipo": "inicio"},
            {"tipo": "disparo", "x": 5, "y": 5},
            {"tipo": "salir"}
        ]
        
        for mensaje in mensajes:
            await cliente_socket.enviar(mensaje)
        
        assert escritor_mock.write.call_count == 3
        assert escritor_mock.drain.call_count == 3

    @pytest.mark.asyncio
    async def test_enviar_preserva_estructura_mensaje(self, cliente_socket, escritor_mock):
        """Verifica que la estructura del mensaje se preserva al enviar."""
        cliente_socket._writer = escritor_mock
        mensaje = {"tipo": "disparo", "x": 3, "y": 7, "datos": {"extra": "info"}}
        
        await cliente_socket.enviar(mensaje)
        
        mensaje_enviado = json.loads(escritor_mock.write.call_args[0][0].decode().strip())
        assert mensaje_enviado == mensaje


# =============================================================================
# RECIBIR
# =============================================================================

class TestClienteSocketRecibir:
    """Tests del método recibir."""

    @pytest.mark.asyncio
    async def test_recibir_parsea_json_valido(self, cliente_socket, lector_mock, mensaje_prueba):
        """Verifica que recibir parsea correctamente JSON válido."""
        cliente_socket._reader = lector_mock
        mensaje_json = json.dumps(mensaje_prueba) + "\n"
        lector_mock.readline = AsyncMock(return_value=mensaje_json.encode())
        
        resultado = await cliente_socket.recibir()
        
        assert resultado == mensaje_prueba

    @pytest.mark.asyncio
    async def test_recibir_devuelve_none_cuando_servidor_cierra(self, cliente_socket, lector_mock):
        """Verifica que devuelve None cuando el servidor cierra la conexión."""
        cliente_socket._reader = lector_mock
        lector_mock.readline = AsyncMock(return_value=b"")
        
        resultado = await cliente_socket.recibir()
        
        assert resultado is None

    @pytest.mark.asyncio
    async def test_recibir_devuelve_none_con_json_invalido(self, cliente_socket, lector_mock):
        """Verifica que devuelve None si el JSON es inválido."""
        cliente_socket._reader = lector_mock
        lector_mock.readline = AsyncMock(return_value=b"JSON INVALIDO\n")
        
        resultado = await cliente_socket.recibir()
        
        assert resultado is None

    @pytest.mark.asyncio
    async def test_recibir_elimina_espacios_en_blanco(self, cliente_socket, lector_mock, mensaje_prueba):
        """Verifica que se eliminan espacios en blanco al recibir."""
        cliente_socket._reader = lector_mock
        mensaje_con_espacios = "  " + json.dumps(mensaje_prueba) + "  \n"
        lector_mock.readline = AsyncMock(return_value=mensaje_con_espacios.encode())
        
        resultado = await cliente_socket.recibir()
        
        assert resultado == mensaje_prueba

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mensaje", [
        {"tipo": "inicio"},
        {"tipo": "disparo", "x": 5, "y": 5},
        {"tipo": "resultado", "resultado": "TOCADO"},
        {"tipo": "error", "mensaje": "Error de validación"},
    ])
    async def test_recibir_multiples_tipos_mensaje(self, cliente_socket, lector_mock, mensaje):
        """Verifica que se reciben correctamente diferentes tipos de mensajes."""
        cliente_socket._reader = lector_mock
        mensaje_json = json.dumps(mensaje) + "\n"
        lector_mock.readline = AsyncMock(return_value=mensaje_json.encode())
        
        resultado = await cliente_socket.recibir()
        
        assert resultado == mensaje

    @pytest.mark.asyncio
    async def test_recibir_maneja_caracteres_especiales(self, cliente_socket, lector_mock):
        """Verifica que se manejan correctamente caracteres especiales."""
        cliente_socket._reader = lector_mock
        mensaje = {"tipo": "error", "mensaje": "Error: ¡Conexión perdida!"}
        mensaje_json = json.dumps(mensaje, ensure_ascii=False) + "\n"
        lector_mock.readline = AsyncMock(return_value=mensaje_json.encode())
        
        resultado = await cliente_socket.recibir()
        
        assert resultado == mensaje


# =============================================================================
# DESCONECTAR
# =============================================================================

class TestClienteSocketDesconectar:
    """Tests del método desconectar."""

    @pytest.mark.asyncio
    async def test_desconectar_cierra_writer(self, cliente_socket, escritor_mock):
        """Verifica que desconectar cierra el writer."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.desconectar()
        
        escritor_mock.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_desconectar_espera_cierre_seguro(self, cliente_socket, escritor_mock):
        """Verifica que se espera el cierre seguro del writer."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.desconectar()
        
        escritor_mock.wait_closed.assert_called_once()

    @pytest.mark.asyncio
    async def test_desconectar_asigna_writer_none(self, cliente_socket, escritor_mock):
        """Verifica que el writer se asigna a None después de desconectar."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.desconectar()
        
        assert cliente_socket._writer is None

    @pytest.mark.asyncio
    async def test_desconectar_maneja_writer_none(self, cliente_socket):
        """Verifica que desconectar maneja el caso de writer None."""
        cliente_socket._writer = None
        
        # No debe lanzar excepción
        await cliente_socket.desconectar()
        
        assert cliente_socket._writer is None

    @pytest.mark.asyncio
    async def test_desconectar_maneja_excepciones(self, cliente_socket, escritor_mock):
        """Verifica que desconectar maneja excepciones sin fallar."""
        cliente_socket._writer = escritor_mock
        escritor_mock.close.side_effect = Exception("Error al cerrar")
        
        # No debe lanzar excepción
        await cliente_socket.desconectar()

    @pytest.mark.asyncio
    async def test_desconectar_multiples_veces(self, cliente_socket, escritor_mock):
        """Verifica que desconectar se puede llamar multiple veces sin error."""
        cliente_socket._writer = escritor_mock
        
        await cliente_socket.desconectar()
        await cliente_socket.desconectar()
        
        assert cliente_socket._writer is None


# =============================================================================
# INTEGRACIÓN
# =============================================================================

class TestClienteSocketIntegracion:
    """Tests de integración del ClienteSocket."""

    @pytest.mark.asyncio
    async def test_flujo_completo_conexion_envio_recepcion(self, cliente_socket, lector_mock, escritor_mock):
        """Verifica el flujo completo de conexión, envío y recepción."""
        with patch('asyncio.open_connection', return_value=(lector_mock, escritor_mock)):
            # Conectar
            await cliente_socket.conectar()
            assert cliente_socket._reader is not None
            assert cliente_socket._writer is not None
            
            # Enviar
            mensaje = {"tipo": "prueba"}
            await cliente_socket.enviar(mensaje)
            escritor_mock.write.assert_called()
            
            # Recibir
            respuesta = {"tipo": "respuesta"}
            lector_mock.readline = AsyncMock(
                return_value=(json.dumps(respuesta) + "\n").encode()
            )
            resultado = await cliente_socket.recibir()
            assert resultado == respuesta
            
            # Desconectar
            await cliente_socket.desconectar()
            assert cliente_socket._writer is None

    @pytest.mark.asyncio
    async def test_multiples_envios_sin_recepcion(self, cliente_socket, escritor_mock):
        """Verifica que se pueden hacer múltiples envíos sin esperar respuesta."""
        cliente_socket._writer = escritor_mock
        
        mensajes = [{"tipo": f"mensaje_{i}"} for i in range(5)]
        
        for mensaje in mensajes:
            await cliente_socket.enviar(mensaje)
        
        assert escritor_mock.write.call_count == 5
