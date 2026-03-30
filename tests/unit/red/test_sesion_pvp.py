import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
from red.servidor.sesion_pvp import SesionPVP
from red.protocolo.mensajes import TipoMensaje
from config.constants import CONSTANTES


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def escritor_jugador_1_mock():
    """Fixture que proporciona un mock del writer del jugador 1."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5001))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def escritor_jugador_2_mock():
    """Fixture que proporciona un mock del writer del jugador 2."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5002))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def logger_mock():
    """Fixture que proporciona un mock del logger."""
    mock = Mock()
    mock.info = Mock()
    mock.error = Mock()
    mock.warning = Mock()
    mock.debug = Mock()
    return mock


@pytest.fixture
def jugador_partida_dict():
    """Fixture que proporciona un diccionario vacío para jugador_partida."""
    return {}


@pytest.fixture
def lock_partida():
    """Fixture que proporciona un asyncio.Lock para la partida."""
    return asyncio.Lock()


@pytest.fixture
def partidas_activas_list():
    """Fixture que proporciona una lista vacía para partidas activas."""
    return []


@pytest.fixture
def sesion_pvp(escritor_jugador_1_mock, escritor_jugador_2_mock, logger_mock, 
               jugador_partida_dict, lock_partida, partidas_activas_list):
    """Fixture que proporciona una instancia de SesionPVP."""
    return SesionPVP(
        escritor_jugador_1_mock,
        escritor_jugador_2_mock,
        1,  # id1
        2,  # id2
        ("127.0.0.1", 5001),  # addr1
        ("127.0.0.1", 5002),  # addr2
        1,  # partida_id
        logger_mock,
        jugador_partida_dict,
        lock_partida,
        partidas_activas_list
    )


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestSesionPVPConstructor:
    """Tests del constructor de SesionPVP."""

    def test_constructor_asigna_partida_id(self, sesion_pvp):
        """Verifica que se asigna correctamente el ID de partida."""
        assert sesion_pvp.partida_id == 1

    def test_constructor_inicializa_writers_correctamente(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que se registran correctamente los writers."""
        assert sesion_pvp._writers[1] == escritor_jugador_1_mock
        assert sesion_pvp._writers[2] == escritor_jugador_2_mock

    def test_constructor_registra_jugadores(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que se registra la asignación de jugador a writer."""
        assert sesion_pvp._jugadores[escritor_jugador_1_mock] == 1
        assert sesion_pvp._jugadores[escritor_jugador_2_mock] == 2

    def test_constructor_asigna_player_ids(self, sesion_pvp):
        """Verifica que se asignan correctamente los IDs de jugadores."""
        assert sesion_pvp._player_ids[1] == 1
        assert sesion_pvp._player_ids[2] == 2

    def test_constructor_guarda_direcciones(self, sesion_pvp):
        """Verifica que se guarden correctamente las direcciones."""
        assert sesion_pvp._addrs[1] == ("127.0.0.1", 5001)
        assert sesion_pvp._addrs[2] == ("127.0.0.1", 5002)

    def test_constructor_crea_servicio_partida(self, sesion_pvp):
        """Verifica que se crea correctamente el servicio de partida."""
        assert sesion_pvp._service is not None
        assert hasattr(sesion_pvp._service, 'estado')

    def test_constructor_registra_en_jugador_partida(self, sesion_pvp, jugador_partida_dict, 
                                                     escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que la sesión se registra en el diccionario jugador_partida."""
        assert jugador_partida_dict[escritor_jugador_1_mock] == sesion_pvp
        assert jugador_partida_dict[escritor_jugador_2_mock] == sesion_pvp

    def test_constructor_asigna_logger(self, sesion_pvp, logger_mock):
        """Verifica que se asigna correctamente el logger."""
        assert sesion_pvp.logger == logger_mock

    def test_constructor_inicializa_evento_terminada(self, sesion_pvp):
        """Verifica que se inicializa el evento de partida terminada."""
        assert isinstance(sesion_pvp._evento_terminada, asyncio.Event)

    def test_constructor_almacena_lock_partida(self, sesion_pvp, lock_partida):
        """Verifica que se almacena correctamente el lock de partida."""
        assert sesion_pvp._lock_partida == lock_partida

    def test_constructor_almacena_partidas_activas(self, sesion_pvp, partidas_activas_list):
        """Verifica que se almacena la referencia a partidas activas."""
        assert sesion_pvp._partidas_activas == partidas_activas_list


# =============================================================================
# LOG DE EVENTOS
# =============================================================================

class TestSesionPVPLogEvento:
    """Tests del método _log_evento."""

    def test_log_evento_simple(self, sesion_pvp, logger_mock):
        """Verifica que se registra un evento simple."""
        logger_mock.reset_mock()
        sesion_pvp._log_evento("EVENTO_PRUEBA")
        
        logger_mock.info.assert_called_once()
        call_args = logger_mock.info.call_args[0][0]
        assert "EVENTO_PRUEBA" in call_args
        assert "match=1" in call_args

    def test_log_evento_con_parametros(self, sesion_pvp, logger_mock):
        """Verifica que se registran eventos con parámetros."""
        logger_mock.reset_mock()
        sesion_pvp._log_evento("EVENTO_CON_PARAMS", player=1, x=5, y=5)
        
        logger_mock.info.assert_called_once()
        call_args = logger_mock.info.call_args[0][0]
        assert "player=1" in call_args
        assert "x=5" in call_args
        assert "y=5" in call_args

    def test_log_evento_incluye_partida_id(self, sesion_pvp, logger_mock):
        """Verifica que el log siempre incluye el ID de partida."""
        sesion_pvp._log_evento("EVENTO")
        
        call_args = logger_mock.info.call_args[0][0]
        assert "match=1" in call_args

    def test_log_evento_multiples_parametros(self, sesion_pvp, logger_mock):
        """Verifica que se pueden registrar múltiples parámetros."""
        sesion_pvp._log_evento("EVENTO", param1="valor1", param2="valor2", param3=123)
        
        call_args = logger_mock.info.call_args[0][0]
        assert "param1=valor1" in call_args
        assert "param2=valor2" in call_args
        assert "param3=123" in call_args


# =============================================================================
# ESTRUCTURA INTERNA
# =============================================================================

class TestSesionPVPEstructura:
    """Tests de la estructura interna de SesionPVP."""

    def test_writers_diccionario_mapea_jugadores(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que el diccionario de writers mapea correctamente jugadores."""
        assert sesion_pvp._writers[1] == escritor_jugador_1_mock
        assert sesion_pvp._writers[2] == escritor_jugador_2_mock
        assert len(sesion_pvp._writers) == 2

    def test_jugadores_diccionario_mapea_writers(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que el diccionario de jugadores mapea correctamente los writers."""
        assert sesion_pvp._jugadores[escritor_jugador_1_mock] == 1
        assert sesion_pvp._jugadores[escritor_jugador_2_mock] == 2
        assert len(sesion_pvp._jugadores) == 2

    def test_obtener_writer_jugador(self, sesion_pvp, escritor_jugador_1_mock):
        """Verifica que se puede obtener el writer de un jugador."""
        writer = sesion_pvp._writers[1]
        assert writer == escritor_jugador_1_mock

    def test_obtener_numero_jugador_del_writer(self, sesion_pvp, escritor_jugador_2_mock):
        """Verifica que se puede obtener el número de jugador del writer."""
        jugador = sesion_pvp._jugadores[escritor_jugador_2_mock]
        assert jugador == 2

    def test_obtener_direccion_jugador(self, sesion_pvp):
        """Verifica que se puede obtener la dirección de un jugador."""
        addr = sesion_pvp._addrs[1]
        assert addr == ("127.0.0.1", 5001)

    def test_obtener_id_jugador(self, sesion_pvp):
        """Verifica que se puede obtener el ID de un jugador."""
        player_id = sesion_pvp._player_ids[1]
        assert player_id == 1


# =============================================================================
# ESTADO DE LA PARTIDA
# =============================================================================

class TestSesionPVPEstado:
    """Tests del estado de la partida."""

    def test_evento_terminada_no_activado_inicialmente(self, sesion_pvp):
        """Verifica que el evento de término no está activado inicialmente."""
        assert not sesion_pvp._evento_terminada.is_set()

    def test_partida_service_existe(self, sesion_pvp):
        """Verifica que el servicio de partida se crea correctamente."""
        assert sesion_pvp._service is not None

    def test_partida_service_tiene_metodos_esenciales(self, sesion_pvp):
        """Verifica que el servicio tiene los métodos necesarios."""
        assert hasattr(sesion_pvp._service, 'estado')
        assert hasattr(sesion_pvp._service, 'disparar')
        assert hasattr(sesion_pvp._service, 'colocar_barco')
        assert hasattr(sesion_pvp._service, 'hay_victoria')


# =============================================================================
# SINCRONIZACIÓN
# =============================================================================

class TestSesionPVPSincronizacion:
    """Tests de sincronización entre jugadores."""

    @pytest.mark.asyncio
    async def test_acceso_simultaneo_con_lock(self, sesion_pvp):
        """Verifica que el lock sincroniza accesos simultáneos."""
        contador = 0
        
        async def incrementar():
            nonlocal contador
            async with sesion_pvp._lock_partida:
                contador += 1
        
        await asyncio.gather(*[incrementar() for _ in range(10)])
        
        assert contador == 10

    @pytest.mark.asyncio
    async def test_evento_terminada_puede_ser_activado(self, sesion_pvp):
        """Verifica que el evento puede ser activado."""
        assert not sesion_pvp._evento_terminada.is_set()
        
        sesion_pvp._evento_terminada.set()
        
        assert sesion_pvp._evento_terminada.is_set()

    @pytest.mark.asyncio
    async def test_esperar_evento_terminada(self, sesion_pvp):
        """Verifica que se puede esperar el evento de término."""
        async def activar_despues():
            await asyncio.sleep(0.1)
            sesion_pvp._evento_terminada.set()
        
        tarea = asyncio.create_task(activar_despues())
        
        await sesion_pvp._evento_terminada.wait()
        await tarea
        
        assert sesion_pvp._evento_terminada.is_set()


# =============================================================================
# CONTEO DE JUGADORES
# =============================================================================

class TestSesionPVPCuentoDosJugadores:
    """Tests de que la sesión siempre tiene exactamente 2 jugadores."""

    def test_sesion_tiene_dos_jugadores(self, sesion_pvp):
        """Verifica que la sesión tiene exactamente 2 jugadores."""
        assert len(sesion_pvp._writers) == 2
        assert len(sesion_pvp._jugadores) == 2

    def test_dos_escritores_registrados(self, sesion_pvp):
        """Verifica que hay exactamente 2 writers registrados."""
        writers = list(sesion_pvp._writers.values())
        assert len(writers) == 2
        assert writers[0] is not writers[1]

    def test_numeros_jugadores_son_1_y_2(self, sesion_pvp):
        """Verifica que los números de jugadores son 1 y 2."""
        numeros = list(sesion_pvp._writers.keys())
        assert set(numeros) == {1, 2}

    def test_dos_player_ids(self, sesion_pvp):
        """Verifica que hay exactamente 2 player IDs."""
        ids = list(sesion_pvp._player_ids.values())
        assert len(ids) == 2
        assert 1 in sesion_pvp._player_ids.values()
        assert 2 in sesion_pvp._player_ids.values()


# =============================================================================
# INFORMACIÓN DE CONEXIÓN
# =============================================================================

class TestSesionPVPInformacionConexion:
    """Tests de la información de conexión."""

    def test_direcciones_registradas_correctamente(self, sesion_pvp):
        """Verifica que las direcciones se registren correctamente."""
        assert sesion_pvp._addrs[1] == ("127.0.0.1", 5001)
        assert sesion_pvp._addrs[2] == ("127.0.0.1", 5002)

    def test_numero_puerto_diferente_por_jugador(self, sesion_pvp):
        """Verifica que cada jugador tiene un puerto diferente."""
        puerto_1 = sesion_pvp._addrs[1][1]
        puerto_2 = sesion_pvp._addrs[2][1]
        
        assert puerto_1 != puerto_2
        assert puerto_1 == 5001
        assert puerto_2 == 5002

    def test_mismo_host_para_ambos(self, sesion_pvp):
        """Verifica que ambos jugadores están en el mismo host (para tests locales)."""
        host_1 = sesion_pvp._addrs[1][0]
        host_2 = sesion_pvp._addrs[2][0]
        
        assert host_1 == host_2
        assert host_1 == "127.0.0.1"


# =============================================================================
# MAPEO BIDIRECCIONAL
# =============================================================================

class TestSesionPVPMapeoBidireccional:
    """Tests del mapeo bidireccional writer <-> jugador."""

    def test_obtener_jugador_desde_writer(self, sesion_pvp, escritor_jugador_1_mock):
        """Verifica que se obtiene el jugador desde el writer."""
        jugador = sesion_pvp._jugadores[escritor_jugador_1_mock]
        assert jugador == 1

    def test_obtener_writer_desde_jugador(self, sesion_pvp, escritor_jugador_2_mock):
        """Verifica que se obtiene el writer desde el jugador."""
        writer = sesion_pvp._writers[2]
        assert writer == escritor_jugador_2_mock

    def test_mapeo_bidireccional_consistente(self, sesion_pvp, escritor_jugador_1_mock):
        """Verifica que el mapeo bidireccional es consistente."""
        # Desde writer a jugador
        jugador = sesion_pvp._jugadores[escritor_jugador_1_mock]
        
        # Desde jugador a writer
        writer_recuperado = sesion_pvp._writers[jugador]
        
        assert writer_recuperado == escritor_jugador_1_mock

    def test_ambos_jugadores_mapeados(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que ambos jugadores están correctamente mapeados."""
        j1 = sesion_pvp._jugadores[escritor_jugador_1_mock]
        j2 = sesion_pvp._jugadores[escritor_jugador_2_mock]
        
        assert j1 == 1
        assert j2 == 2
        
        w1 = sesion_pvp._writers[j1]
        w2 = sesion_pvp._writers[j2]
        
        assert w1 == escritor_jugador_1_mock
        assert w2 == escritor_jugador_2_mock


# =============================================================================
# VALIDACIONES
# =============================================================================

class TestSesionPVPValidaciones:
    """Tests de validaciones internas."""

    def test_writers_no_None(self, sesion_pvp, escritor_jugador_1_mock, escritor_jugador_2_mock):
        """Verifica que los writers no son None."""
        assert sesion_pvp._writers[1] is not None
        assert sesion_pvp._writers[2] is not None

    def test_partida_id_es_positivo(self, sesion_pvp):
        """Verifica que el ID de partida es positivo."""
        assert sesion_pvp.partida_id > 0

    def test_logger_no_None(self, sesion_pvp):
        """Verifica que el logger está asignado."""
        assert sesion_pvp.logger is not None

    def test_service_no_None(self, sesion_pvp):
        """Verifica que el servicio de partida está asignado."""
        assert sesion_pvp._service is not None
