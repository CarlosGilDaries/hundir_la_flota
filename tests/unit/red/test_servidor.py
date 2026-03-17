import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
from collections import deque
from red.servidor.servidor import Servidor
import time


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def servidor():
    """Fixture que proporciona una instancia de Servidor."""
    return Servidor("127.0.0.1", 8888)


@pytest.fixture
def escritor_cliente_mock_1():
    """Fixture que proporciona un mock del primer cliente."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5001))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def escritor_cliente_mock_2():
    """Fixture que proporciona un mock del segundo cliente."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5002))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def lector_cliente_mock():
    """Fixture que proporciona un mock del lector del cliente."""
    return AsyncMock()


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestServidorConstructor:
    """Tests del constructor de Servidor."""

    def test_constructor_inicializa_host(self, servidor):
        """Verifica que se inicializa correctamente el host."""
        assert servidor.host == "127.0.0.1"

    def test_constructor_inicializa_puerto(self, servidor):
        """Verifica que se inicializa correctamente el puerto."""
        assert servidor.port == 8888

    def test_constructor_inicializa_cola_espera_vacia(self, servidor):
        """Verifica que la cola de espera se inicializa vacía."""
        assert isinstance(servidor.cola_espera, deque)
        assert len(servidor.cola_espera) == 0

    def test_constructor_inicializa_diccionarios(self, servidor):
        """Verifica que se inicializan correctamente los diccionarios."""
        assert isinstance(servidor.cola_tiempos, dict)
        assert isinstance(servidor._ids, dict)
        assert isinstance(servidor.jugador_partida, dict)

    def test_constructor_inicializa_contadores(self, servidor):
        """Verifica que los contadores se inicializan correctamente."""
        assert servidor._contador_jugadores == 1
        assert servidor._contador_partidas == 1

    def test_constructor_inicializa_timeout_cola(self, servidor):
        """Verifica que se establece el timeout de la cola correctamente."""
        assert servidor.TIMEOUT_COLA == 15

    def test_constructor_inicializa_locks(self, servidor):
        """Verifica que se inicializan correctamente los locks asyncios."""
        assert isinstance(servidor._lock_cola, asyncio.Lock)
        assert isinstance(servidor._lock_contador, asyncio.Lock)
        assert isinstance(servidor._lock_partida, asyncio.Lock)

    def test_constructor_partidas_activas_vacia(self, servidor):
        """Verifica que la lista de partidas activas se inicializa vacía."""
        assert isinstance(servidor.partidas_activas, list)
        assert len(servidor.partidas_activas) == 0

    @pytest.mark.parametrize("host,puerto", [
        ("0.0.0.0", 8888),
        ("localhost", 5000),
        ("192.168.1.100", 9000),
    ])
    def test_constructor_multiples_hosts_puertos(self, host, puerto):
        """Verifica que el constructor acepta múltiples combinaciones."""
        servidor = Servidor(host, puerto)
        assert servidor.host == host
        assert servidor.port == puerto


# =============================================================================
# ESTRUCTURA INTERNA
# =============================================================================

class TestServidorEstructura:
    """Tests de la estructura interna del servidor."""

    @pytest.mark.asyncio
    async def test_agregar_cliente_a_cola(self, servidor, escritor_cliente_mock_1):
        """Verifica que se puede agregar un cliente a la cola de espera."""
        async with servidor._lock_cola:
            servidor.cola_espera.append(escritor_cliente_mock_1)
            servidor.cola_tiempos[escritor_cliente_mock_1] = time.time()
        
        assert escritor_cliente_mock_1 in servidor.cola_espera
        assert escritor_cliente_mock_1 in servidor.cola_tiempos

    @pytest.mark.asyncio
    async def test_asignar_jugador_id(self, servidor, escritor_cliente_mock_1):
        """Verifica que se asignan IDs únicos a los jugadores."""
        async with servidor._lock_contador:
            id1 = servidor._contador_jugadores
            servidor._contador_jugadores += 1
            id2 = servidor._contador_jugadores
            servidor._contador_jugadores += 1
        
        assert id1 == 1
        assert id2 == 2
        assert id1 != id2

    @pytest.mark.asyncio
    async def test_registrar_cliente_en_diccionario_ids(self, servidor, escritor_cliente_mock_1):
        """Verifica que los IDs de clientes se registran correctamente."""
        async with servidor._lock_contador:
            jugador_id = servidor._contador_jugadores
            servidor._contador_jugadores += 1
            servidor._ids[escritor_cliente_mock_1] = jugador_id
        
        assert escritor_cliente_mock_1 in servidor._ids

    def test_cola_espera_es_fifo(self, servidor, escritor_cliente_mock_1, escritor_cliente_mock_2):
        """Verifica que la cola de espera es FIFO."""
        servidor.cola_espera.append(escritor_cliente_mock_1)
        servidor.cola_espera.append(escritor_cliente_mock_2)
        
        primer_cliente = servidor.cola_espera.popleft()
        segundo_cliente = servidor.cola_espera.popleft()
        
        assert primer_cliente == escritor_cliente_mock_1
        assert segundo_cliente == escritor_cliente_mock_2


# =============================================================================
# CONTADOR DE JUGADORES
# =============================================================================

class TestServidorContadorJugadores:
    """Tests del contador de jugadores."""

    @pytest.mark.asyncio
    async def test_contador_comienza_en_uno(self, servidor):
        """Verifica que el contador comienza en 1."""
        assert servidor._contador_jugadores == 1

    @pytest.mark.asyncio
    async def test_contador_incrementa_correctamente(self, servidor):
        """Verifica que el contador se incrementa correctamente."""
        async with servidor._lock_contador:
            id1 = servidor._contador_jugadores
            servidor._contador_jugadores += 1
            id2 = servidor._contador_jugadores
            servidor._contador_jugadores += 1
            id3 = servidor._contador_jugadores
        
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    @pytest.mark.asyncio
    async def test_contador_es_thread_safe(self, servidor):
        """Verifica que el contador es thread-safe."""
        async def incrementar_contador():
            async with servidor._lock_contador:
                servidor._contador_jugadores += 1
        
        # Simular múltiples incrementos paralelos
        await asyncio.gather(*[incrementar_contador() for _ in range(10)])
        
        assert servidor._contador_jugadores == 11


# =============================================================================
# MANEJO DE COLA
# =============================================================================

class TestServidorManejoCola:
    """Tests del manejo de la cola de espera."""

    @pytest.mark.asyncio
    async def test_agregar_cliente_a_cola_con_timestamp(self, servidor, escritor_cliente_mock_1):
        """Verifica que al agregar cliente se registra el timestamp."""
        async with servidor._lock_cola:
            servidor.cola_espera.append(escritor_cliente_mock_1)
            tiempo_entrada = time.time()
            servidor.cola_tiempos[escritor_cliente_mock_1] = tiempo_entrada
        
        assert servidor.cola_tiempos[escritor_cliente_mock_1] <= tiempo_entrada

    @pytest.mark.asyncio
    async def test_obtener_clientes_de_cola(self, servidor, escritor_cliente_mock_1, escritor_cliente_mock_2):
        """Verifica que se pueden obtener clientes de la cola correctamente."""
        async with servidor._lock_cola:
            servidor.cola_espera.append(escritor_cliente_mock_1)
            servidor.cola_espera.append(escritor_cliente_mock_2)
            
            cliente1 = servidor.cola_espera.popleft()
            cliente2 = servidor.cola_espera.popleft()
        
        assert cliente1 == escritor_cliente_mock_1
        assert cliente2 == escritor_cliente_mock_2
        assert len(servidor.cola_espera) == 0

    @pytest.mark.asyncio
    async def test_limpiar_cliente_de_cola_tiempos(self, servidor, escritor_cliente_mock_1):
        """Verifica que se puede limpiar un cliente de cola_tiempos."""
        servidor.cola_tiempos[escritor_cliente_mock_1] = time.time()
        
        if escritor_cliente_mock_1 in servidor.cola_tiempos:
            del servidor.cola_tiempos[escritor_cliente_mock_1]
        
        assert escritor_cliente_mock_1 not in servidor.cola_tiempos


# =============================================================================
# DICCIONARIO DE IDS
# =============================================================================

class TestServidorDiccionarioIds:
    """Tests del diccionario de IDs."""

    @pytest.mark.asyncio
    async def test_registrar_id_cliente(self, servidor, escritor_cliente_mock_1):
        """Verifica que se registra correctamente el ID de un cliente."""
        uuid_prueba = 1
        servidor._ids[escritor_cliente_mock_1] = uuid_prueba
        
        assert servidor._ids[escritor_cliente_mock_1] == uuid_prueba

    @pytest.mark.asyncio
    async def test_multiples_clientes_con_ids_diferentes(self, servidor, escritor_cliente_mock_1, escritor_cliente_mock_2):
        """Verifica que múltiples clientes tienen IDs diferentes."""
        servidor._ids[escritor_cliente_mock_1] = 1
        servidor._ids[escritor_cliente_mock_2] = 2
        
        assert servidor._ids[escritor_cliente_mock_1] != servidor._ids[escritor_cliente_mock_2]

    @pytest.mark.asyncio
    async def test_limpiar_id_cliente(self, servidor, escritor_cliente_mock_1):
        """Verifica que se puede limpiar el ID de un cliente."""
        servidor._ids[escritor_cliente_mock_1] = 1
        
        if escritor_cliente_mock_1 in servidor._ids:
            del servidor._ids[escritor_cliente_mock_1]
        
        assert escritor_cliente_mock_1 not in servidor._ids


# =============================================================================
# DICCIONARIO JUGADOR_PARTIDA
# =============================================================================

class TestServidorJugadorPartida:
    """Tests del diccionario jugador_partida."""

    @pytest.mark.asyncio
    async def test_registrar_jugador_en_partida(self, servidor, escritor_cliente_mock_1):
        """Verifica que se registra un jugador en una partida."""
        partida_mock = Mock()
        servidor.jugador_partida[escritor_cliente_mock_1] = partida_mock
        
        assert servidor.jugador_partida[escritor_cliente_mock_1] == partida_mock

    @pytest.mark.asyncio
    async def test_limpiar_jugador_de_partida(self, servidor, escritor_cliente_mock_1):
        """Verifica que se puede limpiar un jugador del diccionario."""
        servidor.jugador_partida[escritor_cliente_mock_1] = Mock()
        
        if escritor_cliente_mock_1 in servidor.jugador_partida:
            del servidor.jugador_partida[escritor_cliente_mock_1]
        
        assert escritor_cliente_mock_1 not in servidor.jugador_partida


# =============================================================================
# ESTADOS DEL SERVIDOR
# =============================================================================

class TestServidorEstados:
    """Tests de los diferentes estados del servidor."""

    def test_servidor_sin_clientes(self, servidor):
        """Verifica el estado inicial del servidor sin clientes."""
        assert len(servidor.cola_espera) == 0
        assert len(servidor._ids) == 0
        assert len(servidor.partidas_activas) == 0

    @pytest.mark.asyncio
    async def test_servidor_con_un_cliente_en_cola(self, servidor, escritor_cliente_mock_1):
        """Verifica el estado del servidor con un cliente en cola."""
        async with servidor._lock_cola:
            servidor.cola_espera.append(escritor_cliente_mock_1)
            servidor.cola_tiempos[escritor_cliente_mock_1] = time.time()
        
        async with servidor._lock_contador:
            servidor._ids[escritor_cliente_mock_1] = 1
        
        assert len(servidor.cola_espera) == 1
        assert len(servidor._ids) == 1

    @pytest.mark.asyncio
    async def test_servidor_con_multiples_clientes_en_cola(self, servidor, escritor_cliente_mock_1, escritor_cliente_mock_2):
        """Verifica el estado con múltiples clientes en cola."""
        async with servidor._lock_cola:
            servidor.cola_espera.append(escritor_cliente_mock_1)
            servidor.cola_espera.append(escritor_cliente_mock_2)
            servidor.cola_tiempos[escritor_cliente_mock_1] = time.time()
            servidor.cola_tiempos[escritor_cliente_mock_2] = time.time()
        
        assert len(servidor.cola_espera) == 2
        assert len(servidor.cola_tiempos) == 2


# =============================================================================
# TIMEOUT
# =============================================================================

class TestServidorTimeout:
    """Tests del manejo de timeout."""

    @pytest.mark.asyncio
    async def test_timeout_cola_es_15_segundos(self, servidor):
        """Verifica que el timeout de cola es de 15 segundos."""
        assert servidor.TIMEOUT_COLA == 15

    @pytest.mark.asyncio
    async def test_detectar_cliente_expirado(self, servidor, escritor_cliente_mock_1):
        """Verifica que se detecta correctamente un cliente expirado."""
        tiempo_pasado = time.time() - (servidor.TIMEOUT_COLA + 1)
        servidor.cola_tiempos[escritor_cliente_mock_1] = tiempo_pasado
        
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - servidor.cola_tiempos[escritor_cliente_mock_1]
        
        assert tiempo_transcurrido > servidor.TIMEOUT_COLA

    @pytest.mark.asyncio
    async def test_cliente_no_expirado(self, servidor, escritor_cliente_mock_1):
        """Verifica que un cliente reciente no está expirado."""
        tiempo_reciente = time.time() - 5  # Hace 5 segundos
        servidor.cola_tiempos[escritor_cliente_mock_1] = tiempo_reciente
        
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - servidor.cola_tiempos[escritor_cliente_mock_1]
        
        assert tiempo_transcurrido < servidor.TIMEOUT_COLA


# =============================================================================
# PARTIDAS ACTIVAS
# =============================================================================

class TestServidorPartidasActivas:
    """Tests del manejo de partidas activas."""

    def test_partidas_activas_comienza_vacia(self, servidor):
        """Verifica que la lista de partidas activas comienza vacía."""
        assert len(servidor.partidas_activas) == 0

    def test_agregar_partida_activa(self, servidor):
        """Verifica que se puede agregar una partida a la lista de activas."""
        partida_mock = Mock()
        servidor.partidas_activas.append(partida_mock)
        
        assert len(servidor.partidas_activas) == 1
        assert partida_mock in servidor.partidas_activas

    def test_remover_partida_activa(self, servidor):
        """Verifica que se puede remover una partida de la lista de activas."""
        partida_mock = Mock()
        servidor.partidas_activas.append(partida_mock)
        
        servidor.partidas_activas.remove(partida_mock)
        
        assert len(servidor.partidas_activas) == 0
        assert partida_mock not in servidor.partidas_activas

    def test_multiples_partidas_activas(self, servidor):
        """Verifica que se pueden tener múltiples partidas activas."""
        partidas = [Mock() for _ in range(5)]
        
        for partida in partidas:
            servidor.partidas_activas.append(partida)
        
        assert len(servidor.partidas_activas) == 5


# =============================================================================
# LOCKS DE SINCRONIZACIÓN
# =============================================================================

class TestServidorLocks:
    """Tests de los locks de sincronización."""

    @pytest.mark.asyncio
    async def test_lock_cola_es_asyncio_lock(self, servidor):
        """Verifica que el lock de cola es un asyncio.Lock."""
        assert isinstance(servidor._lock_cola, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_lock_contador_es_asyncio_lock(self, servidor):
        """Verifica que el lock de contador es un asyncio.Lock."""
        assert isinstance(servidor._lock_contador, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_lock_partida_es_asyncio_lock(self, servidor):
        """Verifica que el lock de partida es un asyncio.Lock."""
        assert isinstance(servidor._lock_partida, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_usar_lock_cola(self, servidor):
        """Verifica que se puede adquirir y liberar el lock de cola."""
        async with servidor._lock_cola:
            assert servidor._lock_cola.locked()
        
        assert not servidor._lock_cola.locked()

    @pytest.mark.asyncio
    async def test_multiples_locks_independientes(self, servidor):
        """Verifica que los locks son independientes."""
        async with servidor._lock_cola:
            # El lock de contador no debe estar bloqueado
            assert not servidor._lock_contador.locked()
            assert not servidor._lock_partida.locked()
