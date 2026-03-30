import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from net.server.pvp_session import PvPSession


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def player1_writer_mock():
    """Fixture that provides a mock writer for player 1."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5001))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def player2_writer_mock():
    """Fixture that provides a mock writer for player 2."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5002))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def logger_mock():
    """Fixture that provides a mock logger."""
    mock = Mock()
    mock.info = Mock()
    mock.error = Mock()
    mock.warning = Mock()
    mock.debug = Mock()
    return mock


@pytest.fixture
def player_game_dict():
    """Fixture that provides an empty player_game dictionary."""
    return {}


@pytest.fixture
def game_lock():
    """Fixture that provides an asyncio.Lock for the game."""
    return asyncio.Lock()


@pytest.fixture
def active_games_list():
    """Fixture that provides an empty list for active games."""
    return []


@pytest.fixture
def pvp_session(player1_writer_mock, player2_writer_mock, logger_mock,
                player_game_dict, game_lock, active_games_list):
    """Fixture that provides a PvPSession instance."""
    return PvPSession(
        player1_writer_mock,
        player2_writer_mock,
        1,  # id1
        2,  # id2
        ("127.0.0.1", 5001),  # addr1
        ("127.0.0.1", 5002),  # addr2
        1,  # game_id
        logger_mock,
        player_game_dict,
        game_lock,
        active_games_list
    )


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestPvPSessionConstructor:
    """Tests for the PvPSession constructor."""

    def test_constructor_assigns_game_id(self, pvp_session):
        """Verifies that the game ID is assigned correctly."""
        assert pvp_session.game_id == 1


    def test_constructor_initializes_writers_correctly(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that writers are registered correctly."""
        assert pvp_session._writers[1] == player1_writer_mock
        assert pvp_session._writers[2] == player2_writer_mock


    def test_constructor_registers_players(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that the mapping of writer to player is registered."""
        assert pvp_session._players[player1_writer_mock] == 1
        assert pvp_session._players[player2_writer_mock] == 2


    def test_constructor_assigns_player_ids(self, pvp_session):
        """Verifies that player IDs are assigned correctly."""
        assert pvp_session._player_ids[1] == 1
        assert pvp_session._player_ids[2] == 2


    def test_constructor_stores_addresses(self, pvp_session):
        """Verifies that addresses are stored correctly."""
        assert pvp_session._addrs[1] == ("127.0.0.1", 5001)
        assert pvp_session._addrs[2] == ("127.0.0.1", 5002)


    def test_constructor_creates_game_service(self, pvp_session):
        """Verifies that the game service is created correctly."""
        assert pvp_session._service is not None
        assert hasattr(pvp_session._service, 'state')


    def test_constructor_registers_in_player_game_dict(self, pvp_session, player_game_dict, player1_writer_mock, player2_writer_mock):
        """Verifies that the session is registered in the player_game dictionary."""
        assert player_game_dict[player1_writer_mock] == pvp_session
        assert player_game_dict[player2_writer_mock] == pvp_session


    def test_constructor_assigns_logger(self, pvp_session, logger_mock):
        """Verifies that the logger is assigned correctly."""
        assert pvp_session.logger == logger_mock


    def test_constructor_initializes_ended_event(self, pvp_session):
        """Verifies that the ended event is initialized."""
        assert isinstance(pvp_session._ended_event, asyncio.Event)


    def test_constructor_stores_game_lock(self, pvp_session, game_lock):
        """Verifies that the game lock is stored correctly."""
        assert pvp_session._game_lock == game_lock


    def test_constructor_stores_active_games(self, pvp_session, active_games_list):
        """Verifies that the reference to active games is stored."""
        assert pvp_session._active_games == active_games_list


# =============================================================================
# EVENT LOGGING
# =============================================================================

class TestPvPSessionLogEvent:
    """Tests for the _log_event method."""

    def test_log_event_simple(self, pvp_session, logger_mock):
        """Verifies that a simple event is logged."""
        logger_mock.reset_mock()
        pvp_session._log_event("TEST_EVENT")

        logger_mock.info.assert_called_once()
        call_args = logger_mock.info.call_args[0][0]
        assert "TEST_EVENT" in call_args
        assert "match=1" in call_args


    def test_log_event_with_parameters(self, pvp_session, logger_mock):
        """Verifies that events with parameters are logged."""
        logger_mock.reset_mock()
        pvp_session._log_event("EVENT_WITH_PARAMS", player=1, x=5, y=5)

        logger_mock.info.assert_called_once()
        call_args = logger_mock.info.call_args[0][0]
        assert "player=1" in call_args
        assert "x=5" in call_args
        assert "y=5" in call_args


    def test_log_event_includes_game_id(self, pvp_session, logger_mock):
        """Verifies that the log always includes the game ID."""
        pvp_session._log_event("EVENT")

        call_args = logger_mock.info.call_args[0][0]
        assert "match=1" in call_args


    def test_log_event_multiple_parameters(self, pvp_session, logger_mock):
        """Verifies that multiple parameters can be logged."""
        pvp_session._log_event("EVENT", param1="value1", param2="value2", param3=123)

        call_args = logger_mock.info.call_args[0][0]
        assert "param1=value1" in call_args
        assert "param2=value2" in call_args
        assert "param3=123" in call_args


# =============================================================================
# INTERNAL STRUCTURE
# =============================================================================

class TestPvPSessionStructure:
    """Tests for the internal structure of PvPSession."""

    def test_writers_dictionary_maps_players(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that the writers dictionary correctly maps players."""
        assert pvp_session._writers[1] == player1_writer_mock
        assert pvp_session._writers[2] == player2_writer_mock
        assert len(pvp_session._writers) == 2


    def test_players_dictionary_maps_writers(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that the players dictionary correctly maps writers."""
        assert pvp_session._players[player1_writer_mock] == 1
        assert pvp_session._players[player2_writer_mock] == 2
        assert len(pvp_session._players) == 2


    def test_get_writer_by_player(self, pvp_session, player1_writer_mock):
        """Verifies that a writer can be obtained by player number."""
        writer = pvp_session._writers[1]
        assert writer == player1_writer_mock


    def test_get_player_number_by_writer(self, pvp_session, player2_writer_mock):
        """Verifies that the player number can be obtained from the writer."""
        player = pvp_session._players[player2_writer_mock]
        assert player == 2


    def test_get_player_address(self, pvp_session):
        """Verifies that a player's address can be obtained."""
        addr = pvp_session._addrs[1]
        assert addr == ("127.0.0.1", 5001)


    def test_get_player_id(self, pvp_session):
        """Verifies that a player's ID can be obtained."""
        player_id = pvp_session._player_ids[1]
        assert player_id == 1


# =============================================================================
# GAME STATE
# =============================================================================

class TestPvPSessionGameState:
    """Tests for the game state."""

    def test_ended_event_not_set_initial(self, pvp_session):
        """Verifies that the ended event is not initially set."""
        assert not pvp_session._ended_event.is_set()


    def test_game_service_exists(self, pvp_session):
        """Verifies that the game service is created correctly."""
        assert pvp_session._service is not None


    def test_game_service_has_essential_methods(self, pvp_session):
        """Verifies that the service has the necessary methods."""
        assert hasattr(pvp_session._service, 'state')
        assert hasattr(pvp_session._service, 'shoot')
        assert hasattr(pvp_session._service, 'place_ship')
        assert hasattr(pvp_session._service, 'check_victory')


# =============================================================================
# SYNCHRONIZATION
# =============================================================================

class TestPvPSessionSynchronization:
    """Tests for player synchronization."""

    @pytest.mark.asyncio
    async def test_concurrent_access_with_lock(self, pvp_session):
        """Verifies that the lock synchronizes concurrent access."""
        counter = 0

        async def increment():
            nonlocal counter
            async with pvp_session._game_lock:
                counter += 1

        await asyncio.gather(*[increment() for _ in range(10)])

        assert counter == 10


    @pytest.mark.asyncio
    async def test_ended_event_can_be_set(self, pvp_session):
        """Verifies that the ended event can be set."""
        assert not pvp_session._ended_event.is_set()

        pvp_session._ended_event.set()

        assert pvp_session._ended_event.is_set()


    @pytest.mark.asyncio
    async def test_wait_for_ended_event(self, pvp_session):
        """Verifies that it is possible to wait for the ended event."""
        async def set_after():
            await asyncio.sleep(0.1)
            pvp_session._ended_event.set()

        task = asyncio.create_task(set_after())

        await pvp_session._ended_event.wait()
        await task

        assert pvp_session._ended_event.is_set()


# =============================================================================
# PLAYER COUNT
# =============================================================================

class TestPvPSessionTwoPlayers:
    """Tests that the session always has exactly 2 players."""

    def test_session_has_two_players(self, pvp_session):
        """Verifies that the session has exactly 2 players."""
        assert len(pvp_session._writers) == 2
        assert len(pvp_session._players) == 2


    def test_two_writers_registered(self, pvp_session):
        """Verifies that exactly 2 writers are registered."""
        writers = list(pvp_session._writers.values())
        assert len(writers) == 2
        assert writers[0] is not writers[1]


    def test_player_numbers_are_1_and_2(self, pvp_session):
        """Verifies that the player numbers are 1 and 2."""
        numbers = list(pvp_session._writers.keys())
        assert set(numbers) == {1, 2}


    def test_two_player_ids(self, pvp_session):
        """Verifies that there are exactly 2 player IDs."""
        ids = list(pvp_session._player_ids.values())
        assert len(ids) == 2
        assert 1 in pvp_session._player_ids.values()
        assert 2 in pvp_session._player_ids.values()


# =============================================================================
# CONNECTION INFORMATION
# =============================================================================

class TestPvPSessionConnectionInfo:
    """Tests for connection information."""

    def test_addresses_registered_correctly(self, pvp_session):
        """Verifies that addresses are registered correctly."""
        assert pvp_session._addrs[1] == ("127.0.0.1", 5001)
        assert pvp_session._addrs[2] == ("127.0.0.1", 5002)


    def test_different_port_per_player(self, pvp_session):
        """Verifies that each player has a different port."""
        port1 = pvp_session._addrs[1][1]
        port2 = pvp_session._addrs[2][1]

        assert port1 != port2
        assert port1 == 5001
        assert port2 == 5002


    def test_same_host_for_both(self, pvp_session):
        """Verifies that both players are on the same host (for local tests)."""
        host1 = pvp_session._addrs[1][0]
        host2 = pvp_session._addrs[2][0]

        assert host1 == host2
        assert host1 == "127.0.0.1"


# =============================================================================
# BIDIRECTIONAL MAPPING
# =============================================================================

class TestPvPSessionBidirectionalMapping:
    """Tests for the bidirectional writer <-> player mapping."""

    def test_get_player_from_writer(self, pvp_session, player1_writer_mock):
        """Verifies that the player can be obtained from the writer."""
        player = pvp_session._players[player1_writer_mock]
        assert player == 1


    def test_get_writer_from_player(self, pvp_session, player2_writer_mock):
        """Verifies that the writer can be obtained from the player."""
        writer = pvp_session._writers[2]
        assert writer == player2_writer_mock


    def test_bidirectional_mapping_consistent(self, pvp_session, player1_writer_mock):
        """Verifies that the bidirectional mapping is consistent."""
        # From writer to player
        player = pvp_session._players[player1_writer_mock]

        # From player to writer
        recovered_writer = pvp_session._writers[player]

        assert recovered_writer == player1_writer_mock


    def test_both_players_mapped(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that both players are correctly mapped."""
        p1 = pvp_session._players[player1_writer_mock]
        p2 = pvp_session._players[player2_writer_mock]

        assert p1 == 1
        assert p2 == 2

        w1 = pvp_session._writers[p1]
        w2 = pvp_session._writers[p2]

        assert w1 == player1_writer_mock
        assert w2 == player2_writer_mock


# =============================================================================
# VALIDATIONS
# =============================================================================

class TestPvPSessionValidations:
    """Tests for internal validations."""

    def test_writers_not_none(self, pvp_session, player1_writer_mock, player2_writer_mock):
        """Verifies that writers are not None."""
        assert pvp_session._writers[1] is not None
        assert pvp_session._writers[2] is not None


    def test_game_id_positive(self, pvp_session):
        """Verifies that the game ID is positive."""
        assert pvp_session.game_id > 0


    def test_logger_not_none(self, pvp_session):
        """Verifies that the logger is assigned."""
        assert pvp_session.logger is not None


    def test_service_not_none(self, pvp_session):
        """Verifies that the game service is assigned."""
        assert pvp_session._service is not None