# tests/net/test_server.py

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch, call
from collections import deque
from net.server.server import Server
import time


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def server():
    """Fixture that provides a Server instance."""
    return Server("127.0.0.1", 8888)


@pytest.fixture
def client_writer_mock_1():
    """Fixture that provides a mock of the first client."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5001))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def client_writer_mock_2():
    """Fixture that provides a mock of the second client."""
    mock = AsyncMock()
    mock.get_extra_info = Mock(return_value=("127.0.0.1", 5002))
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def client_reader_mock():
    """Fixture that provides a mock of the client reader."""
    return AsyncMock()


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestServerConstructor:
    """Tests for the Server constructor."""

    def test_constructor_initializes_host(self, server):
        """Verifies that the host is initialized correctly."""
        assert server.host == "127.0.0.1"


    def test_constructor_initializes_port(self, server):
        """Verifies that the port is initialized correctly."""
        assert server.port == 8888


    def test_constructor_initializes_waiting_queue_empty(self, server):
        """Verifies that the waiting queue is initialized empty."""
        assert isinstance(server.waiting_queue, deque)
        assert len(server.waiting_queue) == 0


    def test_constructor_initializes_dictionaries(self, server):
        """Verifies that dictionaries are initialized correctly."""
        assert isinstance(server.queue_timestamps, dict)
        assert isinstance(server._ids, dict)
        assert isinstance(server.player_game, dict)


    def test_constructor_initializes_counters(self, server):
        """Verifies that counters are initialized correctly."""
        assert server._player_counter == 1
        assert server._game_counter == 1


    def test_constructor_initializes_queue_timeout(self, server):
        """Verifies that the queue timeout is set correctly."""
        assert server.QUEUE_TIMEOUT == 15


    def test_constructor_initializes_locks(self, server):
        """Verifies that asyncio locks are initialized correctly."""
        assert isinstance(server._queue_lock, asyncio.Lock)
        assert isinstance(server._counter_lock, asyncio.Lock)
        assert isinstance(server._game_lock, asyncio.Lock)


    def test_constructor_active_games_empty(self, server):
        """Verifies that the active games list is initialized empty."""
        assert isinstance(server.active_games, list)
        assert len(server.active_games) == 0


    @pytest.mark.parametrize("host,port", [
        ("0.0.0.0", 8888),
        ("localhost", 5000),
        ("192.168.1.100", 9000),
    ])
    def test_constructor_multiple_hosts_ports(self, host, port):
        """Verifies that the constructor accepts multiple combinations."""
        server = Server(host, port)
        assert server.host == host
        assert server.port == port


# =============================================================================
# INTERNAL STRUCTURE
# =============================================================================

class TestServerStructure:
    """Tests for the internal structure of the server."""

    @pytest.mark.asyncio
    async def test_add_client_to_queue(self, server, client_writer_mock_1):
        """Verifies that a client can be added to the waiting queue."""
        async with server._queue_lock:
            server.waiting_queue.append(client_writer_mock_1)
            server.queue_timestamps[client_writer_mock_1] = time.time()

        assert client_writer_mock_1 in server.waiting_queue
        assert client_writer_mock_1 in server.queue_timestamps


    @pytest.mark.asyncio
    async def test_assign_player_id(self, server, client_writer_mock_1):
        """Verifies that unique IDs are assigned to players."""
        async with server._counter_lock:
            id1 = server._player_counter
            server._player_counter += 1
            id2 = server._player_counter
            server._player_counter += 1

        assert id1 == 1
        assert id2 == 2
        assert id1 != id2


    @pytest.mark.asyncio
    async def test_register_client_in_ids_dictionary(self, server, client_writer_mock_1):
        """Verifies that client IDs are registered correctly."""
        async with server._counter_lock:
            player_id = server._player_counter
            server._player_counter += 1
            server._ids[client_writer_mock_1] = player_id

        assert client_writer_mock_1 in server._ids


    def test_waiting_queue_is_fifo(self, server, client_writer_mock_1, client_writer_mock_2):
        """Verifies that the waiting queue is FIFO."""
        server.waiting_queue.append(client_writer_mock_1)
        server.waiting_queue.append(client_writer_mock_2)

        first_client = server.waiting_queue.popleft()
        second_client = server.waiting_queue.popleft()

        assert first_client == client_writer_mock_1
        assert second_client == client_writer_mock_2


# =============================================================================
# PLAYER COUNTER
# =============================================================================

class TestServerPlayerCounter:
    """Tests for the player counter."""

    @pytest.mark.asyncio
    async def test_counter_starts_at_one(self, server):
        """Verifies that the counter starts at 1."""
        assert server._player_counter == 1


    @pytest.mark.asyncio
    async def test_counter_increments_correctly(self, server):
        """Verifies that the counter increments correctly."""
        async with server._counter_lock:
            id1 = server._player_counter
            server._player_counter += 1
            id2 = server._player_counter
            server._player_counter += 1
            id3 = server._player_counter

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3


    @pytest.mark.asyncio
    async def test_counter_is_thread_safe(self, server):
        """Verifies that the counter is thread-safe."""
        async def increment_counter():
            async with server._counter_lock:
                server._player_counter += 1

        # Simulate multiple parallel increments
        await asyncio.gather(*[increment_counter() for _ in range(10)])

        assert server._player_counter == 11


# =============================================================================
# QUEUE MANAGEMENT
# =============================================================================

class TestServerQueueManagement:
    """Tests for waiting queue management."""

    @pytest.mark.asyncio
    async def test_add_client_to_queue_with_timestamp(self, server, client_writer_mock_1):
        """Verifies that timestamp is recorded when adding a client."""
        async with server._queue_lock:
            server.waiting_queue.append(client_writer_mock_1)
            entry_time = time.time()
            server.queue_timestamps[client_writer_mock_1] = entry_time

        assert server.queue_timestamps[client_writer_mock_1] <= entry_time


    @pytest.mark.asyncio
    async def test_get_clients_from_queue(self, server, client_writer_mock_1, client_writer_mock_2):
        """Verifies that clients can be retrieved from the queue correctly."""
        async with server._queue_lock:
            server.waiting_queue.append(client_writer_mock_1)
            server.waiting_queue.append(client_writer_mock_2)

            client1 = server.waiting_queue.popleft()
            client2 = server.waiting_queue.popleft()

        assert client1 == client_writer_mock_1
        assert client2 == client_writer_mock_2
        assert len(server.waiting_queue) == 0


    @pytest.mark.asyncio
    async def test_remove_client_from_queue_timestamps(self, server, client_writer_mock_1):
        """Verifies that a client can be removed from queue_timestamps."""
        server.queue_timestamps[client_writer_mock_1] = time.time()

        if client_writer_mock_1 in server.queue_timestamps:
            del server.queue_timestamps[client_writer_mock_1]

        assert client_writer_mock_1 not in server.queue_timestamps


# =============================================================================
# ID DICTIONARY
# =============================================================================

class TestServerIdDictionary:
    """Tests for the IDs dictionary."""

    @pytest.mark.asyncio
    async def test_register_client_id(self, server, client_writer_mock_1):
        """Verifies that a client ID is registered correctly."""
        test_uuid = 1
        server._ids[client_writer_mock_1] = test_uuid

        assert server._ids[client_writer_mock_1] == test_uuid


    @pytest.mark.asyncio
    async def test_multiple_clients_with_different_ids(self, server, client_writer_mock_1, client_writer_mock_2):
        """Verifies that multiple clients have different IDs."""
        server._ids[client_writer_mock_1] = 1
        server._ids[client_writer_mock_2] = 2

        assert server._ids[client_writer_mock_1] != server._ids[client_writer_mock_2]


    @pytest.mark.asyncio
    async def test_remove_client_id(self, server, client_writer_mock_1):
        """Verifies that a client ID can be removed."""
        server._ids[client_writer_mock_1] = 1

        if client_writer_mock_1 in server._ids:
            del server._ids[client_writer_mock_1]

        assert client_writer_mock_1 not in server._ids


# =============================================================================
# PLAYER_GAME DICTIONARY
# =============================================================================

class TestServerPlayerGame:
    """Tests for the player_game dictionary."""

    @pytest.mark.asyncio
    async def test_register_player_in_game(self, server, client_writer_mock_1):
        """Verifies that a player is registered in a game."""
        game_mock = Mock()
        server.player_game[client_writer_mock_1] = game_mock

        assert server.player_game[client_writer_mock_1] == game_mock


    @pytest.mark.asyncio
    async def test_remove_player_from_game(self, server, client_writer_mock_1):
        """Verifies that a player can be removed from the dictionary."""
        server.player_game[client_writer_mock_1] = Mock()

        if client_writer_mock_1 in server.player_game:
            del server.player_game[client_writer_mock_1]

        assert client_writer_mock_1 not in server.player_game


# =============================================================================
# SERVER STATES
# =============================================================================

class TestServerStates:
    """Tests for the different states of the server."""

    def test_server_with_no_clients(self, server):
        """Verifies the initial state of the server with no clients."""
        assert len(server.waiting_queue) == 0
        assert len(server._ids) == 0
        assert len(server.active_games) == 0


    @pytest.mark.asyncio
    async def test_server_with_one_client_in_queue(self, server, client_writer_mock_1):
        """Verifies the state of the server with one client in queue."""
        async with server._queue_lock:
            server.waiting_queue.append(client_writer_mock_1)
            server.queue_timestamps[client_writer_mock_1] = time.time()

        async with server._counter_lock:
            server._ids[client_writer_mock_1] = 1

        assert len(server.waiting_queue) == 1
        assert len(server._ids) == 1


    @pytest.mark.asyncio
    async def test_server_with_multiple_clients_in_queue(self, server, client_writer_mock_1, client_writer_mock_2):
        """Verifies the state with multiple clients in queue."""
        async with server._queue_lock:
            server.waiting_queue.append(client_writer_mock_1)
            server.waiting_queue.append(client_writer_mock_2)
            server.queue_timestamps[client_writer_mock_1] = time.time()
            server.queue_timestamps[client_writer_mock_2] = time.time()

        assert len(server.waiting_queue) == 2
        assert len(server.queue_timestamps) == 2


# =============================================================================
# TIMEOUT
# =============================================================================

class TestServerTimeout:
    """Tests for timeout handling."""

    @pytest.mark.asyncio
    async def test_queue_timeout_is_15_seconds(self, server):
        """Verifies that the queue timeout is 15 seconds."""
        assert server.QUEUE_TIMEOUT == 15


    @pytest.mark.asyncio
    async def test_detect_expired_client(self, server, client_writer_mock_1):
        """Verifies that an expired client is correctly detected."""
        past_time = time.time() - (server.QUEUE_TIMEOUT + 1)
        server.queue_timestamps[client_writer_mock_1] = past_time

        current_time = time.time()
        elapsed = current_time - server.queue_timestamps[client_writer_mock_1]

        assert elapsed > server.QUEUE_TIMEOUT


    @pytest.mark.asyncio
    async def test_client_not_expired(self, server, client_writer_mock_1):
        """Verifies that a recent client is not expired."""
        recent_time = time.time() - 5  # 5 seconds ago
        server.queue_timestamps[client_writer_mock_1] = recent_time

        current_time = time.time()
        elapsed = current_time - server.queue_timestamps[client_writer_mock_1]

        assert elapsed < server.QUEUE_TIMEOUT


# =============================================================================
# ACTIVE GAMES
# =============================================================================

class TestServerActiveGames:
    """Tests for active games management."""

    def test_active_games_starts_empty(self, server):
        """Verifies that the active games list starts empty."""
        assert len(server.active_games) == 0


    def test_add_active_game(self, server):
        """Verifies that a game can be added to the active list."""
        game_mock = Mock()
        server.active_games.append(game_mock)

        assert len(server.active_games) == 1
        assert game_mock in server.active_games


    def test_remove_active_game(self, server):
        """Verifies that a game can be removed from the active list."""
        game_mock = Mock()
        server.active_games.append(game_mock)

        server.active_games.remove(game_mock)

        assert len(server.active_games) == 0
        assert game_mock not in server.active_games


    def test_multiple_active_games(self, server):
        """Verifies that multiple active games can be present."""
        games = [Mock() for _ in range(5)]

        for game in games:
            server.active_games.append(game)

        assert len(server.active_games) == 5


# =============================================================================
# SYNCHRONIZATION LOCKS
# =============================================================================

class TestServerLocks:
    """Tests for synchronization locks."""

    @pytest.mark.asyncio
    async def test_queue_lock_is_asyncio_lock(self, server):
        """Verifies that the queue lock is an asyncio.Lock."""
        assert isinstance(server._queue_lock, asyncio.Lock)


    @pytest.mark.asyncio
    async def test_counter_lock_is_asyncio_lock(self, server):
        """Verifies that the counter lock is an asyncio.Lock."""
        assert isinstance(server._counter_lock, asyncio.Lock)


    @pytest.mark.asyncio
    async def test_game_lock_is_asyncio_lock(self, server):
        """Verifies that the game lock is an asyncio.Lock."""
        assert isinstance(server._game_lock, asyncio.Lock)


    @pytest.mark.asyncio
    async def test_use_queue_lock(self, server):
        """Verifies that the queue lock can be acquired and released."""
        async with server._queue_lock:
            assert server._queue_lock.locked()

        assert not server._queue_lock.locked()


    @pytest.mark.asyncio
    async def test_multiple_locks_independent(self, server):
        """Verifies that the locks are independent."""
        async with server._queue_lock:
            # The counter lock should not be locked
            assert not server._counter_lock.locked()
            assert not server._game_lock.locked()