# tests/unit/net/test_client_socket.py

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from net.client.client_socket import ClientSocket


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def client_socket():
    """Fixture that provides a ClientSocket instance."""
    return ClientSocket("127.0.0.1", 8888)


@pytest.fixture
def mock_reader():
    """Fixture that provides a mock StreamReader."""
    return AsyncMock()


@pytest.fixture
def mock_writer():
    """Fixture that provides a mock StreamWriter."""
    mock = AsyncMock()
    mock.write = Mock()
    mock.drain = AsyncMock()
    mock.close = Mock()
    mock.wait_closed = AsyncMock()
    return mock


@pytest.fixture
def test_message():
    """Fixture with a test JSON message."""
    return {
        "type": "start",
        "player": 1,
        "state": "waiting"
    }


# =============================================================================
# CONSTRUCTOR
# =============================================================================

class TestClientSocketConstructor:
    """Tests for the ClientSocket constructor."""

    def test_constructor_initializes_host(self, client_socket):
        """Verifies that the constructor correctly initializes the host."""
        assert client_socket._host == "127.0.0.1"


    def test_constructor_initializes_port(self, client_socket):
        """Verifies that the constructor correctly initializes the port."""
        assert client_socket._port == 8888


    def test_constructor_initializes_reader_none(self, client_socket):
        """Verifies that the reader is initialized as None."""
        assert client_socket._reader is None


    def test_constructor_initializes_writer_none(self, client_socket):
        """Verifies that the writer is initialized as None."""
        assert client_socket._writer is None


    @pytest.mark.parametrize("host,port", [
        ("localhost", 5000),
        ("192.168.1.100", 9000),
        ("0.0.0.0", 8000),
    ])
    def test_constructor_multiple_hosts_ports(self, host, port):
        """Verifies that the constructor accepts multiple host/port combinations."""
        client = ClientSocket(host, port)
        assert client._host == host
        assert client._port == port


# =============================================================================
# CONNECT
# =============================================================================

class TestClientSocketConnect:
    """Tests for the connect method."""

    @pytest.mark.asyncio
    async def test_connect_establishes_connection(self, client_socket, mock_reader, mock_writer):
        """Verifies that connect correctly establishes the connection."""
        with patch('asyncio.open_connection', return_value=(mock_reader, mock_writer)):
            await client_socket.connect()

            assert client_socket._reader == mock_reader
            assert client_socket._writer == mock_writer


    @pytest.mark.asyncio
    async def test_connect_uses_correct_host(self, client_socket, mock_reader, mock_writer):
        """Verifies that connect uses the correct host."""
        with patch('asyncio.open_connection', return_value=(mock_reader, mock_writer)) as mock_open:
            await client_socket.connect()

            mock_open.assert_called_once_with("127.0.0.1", 8888)


    @pytest.mark.asyncio
    async def test_connect_raises_exception_on_failure(self, client_socket):
        """Verifies that an exception is propagated if the connection fails."""
        with patch('asyncio.open_connection', side_effect=OSError("Connection refused")):
            with pytest.raises(OSError):
                await client_socket.connect()


    @pytest.mark.asyncio
    async def test_connect_with_different_ports(self, mock_reader, mock_writer):
        """Verifies connection with different ports."""
        with patch('asyncio.open_connection', return_value=(mock_reader, mock_writer)) as mock_open:
            client = ClientSocket("localhost", 5000)
            await client.connect()

            mock_open.assert_called_once_with("localhost", 5000)


# =============================================================================
# SEND
# =============================================================================

class TestClientSocketSend:
    """Tests for the send method."""

    @pytest.mark.asyncio
    async def test_send_serializes_json(self, client_socket, mock_writer, test_message):
        """Verifies that send correctly serializes the message to JSON."""
        client_socket._writer = mock_writer

        await client_socket.send(test_message)

        expected_message = json.dumps(test_message) + "\n"
        mock_writer.write.assert_called_once_with(expected_message.encode())


    @pytest.mark.asyncio
    async def test_send_encodes_to_bytes(self, client_socket, mock_writer, test_message):
        """Verifies that the message is correctly encoded to bytes."""
        client_socket._writer = mock_writer

        await client_socket.send(test_message)

        kwargs = mock_writer.write.call_args
        sent_message = kwargs[0][0]
        assert isinstance(sent_message, bytes)


    @pytest.mark.asyncio
    async def test_send_adds_newline(self, client_socket, mock_writer):
        """Verifies that a newline is added at the end of the message."""
        client_socket._writer = mock_writer
        message = {"type": "test"}

        await client_socket.send(message)

        sent_message = mock_writer.write.call_args[0][0].decode()
        assert sent_message.endswith("\n")


    @pytest.mark.asyncio
    async def test_send_calls_drain(self, client_socket, mock_writer, test_message):
        """Verifies that drain is called after writing."""
        client_socket._writer = mock_writer

        await client_socket.send(test_message)

        mock_writer.drain.assert_called_once()


    @pytest.mark.asyncio
    async def test_send_multiple_messages(self, client_socket, mock_writer):
        """Verifies that multiple messages can be sent sequentially."""
        client_socket._writer = mock_writer
        messages = [
            {"type": "start"},
            {"type": "shot", "x": 5, "y": 5},
            {"type": "exit"}
        ]

        for message in messages:
            await client_socket.send(message)

        assert mock_writer.write.call_count == 3
        assert mock_writer.drain.call_count == 3


    @pytest.mark.asyncio
    async def test_send_preserves_message_structure(self, client_socket, mock_writer):
        """Verifies that the message structure is preserved when sending."""
        client_socket._writer = mock_writer
        message = {"type": "shot", "x": 3, "y": 7, "data": {"extra": "info"}}

        await client_socket.send(message)

        sent_message = json.loads(mock_writer.write.call_args[0][0].decode().strip())
        assert sent_message == message


# =============================================================================
# RECEIVE
# =============================================================================

class TestClientSocketReceive:
    """Tests for the receive method."""

    @pytest.mark.asyncio
    async def test_receive_parses_valid_json(self, client_socket, mock_reader, test_message):
        """Verifies that receive correctly parses valid JSON."""
        client_socket._reader = mock_reader
        message_json = json.dumps(test_message) + "\n"
        mock_reader.readline = AsyncMock(return_value=message_json.encode())

        result = await client_socket.receive()

        assert result == test_message


    @pytest.mark.asyncio
    async def test_receive_returns_none_when_server_closes(self, client_socket, mock_reader):
        """Verifies that receive returns None when the server closes the connection."""
        client_socket._reader = mock_reader
        mock_reader.readline = AsyncMock(return_value=b"")

        result = await client_socket.receive()

        assert result is None


    @pytest.mark.asyncio
    async def test_receive_returns_none_with_invalid_json(self, client_socket, mock_reader):
        """Verifies that receive returns None if the JSON is invalid."""
        client_socket._reader = mock_reader
        mock_reader.readline = AsyncMock(return_value=b"INVALID JSON\n")

        result = await client_socket.receive()

        assert result is None


    @pytest.mark.asyncio
    async def test_receive_strips_whitespace(self, client_socket, mock_reader, test_message):
        """Verifies that whitespace is stripped when receiving."""
        client_socket._reader = mock_reader
        message_with_spaces = "  " + json.dumps(test_message) + "  \n"
        mock_reader.readline = AsyncMock(return_value=message_with_spaces.encode())

        result = await client_socket.receive()

        assert result == test_message


    @pytest.mark.asyncio
    @pytest.mark.parametrize("message", [
        {"type": "start"},
        {"type": "shot", "x": 5, "y": 5},
        {"type": "result", "result": "HIT"},
        {"type": "error", "message": "Validation error"},
    ])
    async def test_receive_multiple_message_types(self, client_socket, mock_reader, message):
        """Verifies that different message types are received correctly."""
        client_socket._reader = mock_reader
        message_json = json.dumps(message) + "\n"
        mock_reader.readline = AsyncMock(return_value=message_json.encode())

        result = await client_socket.receive()

        assert result == message


    @pytest.mark.asyncio
    async def test_receive_handles_special_characters(self, client_socket, mock_reader):
        """Verifies that special characters are handled correctly."""
        client_socket._reader = mock_reader
        message = {"type": "error", "message": "Error: ¡Connection lost!"}
        message_json = json.dumps(message, ensure_ascii=False) + "\n"
        mock_reader.readline = AsyncMock(return_value=message_json.encode())

        result = await client_socket.receive()

        assert result == message


# =============================================================================
# DISCONNECT
# =============================================================================

class TestClientSocketDisconnect:
    """Tests for the disconnect method."""

    @pytest.mark.asyncio
    async def test_disconnect_closes_writer(self, client_socket, mock_writer):
        """Verifies that disconnect closes the writer."""
        client_socket._writer = mock_writer

        await client_socket.disconnect()

        mock_writer.close.assert_called_once()


    @pytest.mark.asyncio
    async def test_disconnect_waits_for_secure_close(self, client_socket, mock_writer):
        """Verifies that disconnect waits for the writer to close securely."""
        client_socket._writer = mock_writer

        await client_socket.disconnect()

        mock_writer.wait_closed.assert_called_once()


    @pytest.mark.asyncio
    async def test_disconnect_sets_writer_to_none(self, client_socket, mock_writer):
        """Verifies that the writer is set to None after disconnecting."""
        client_socket._writer = mock_writer

        await client_socket.disconnect()

        assert client_socket._writer is None


    @pytest.mark.asyncio
    async def test_disconnect_handles_writer_none(self, client_socket):
        """Verifies that disconnect handles the case where writer is None."""
        client_socket._writer = None

        # Should not raise an exception
        await client_socket.disconnect()

        assert client_socket._writer is None


    @pytest.mark.asyncio
    async def test_disconnect_handles_exceptions(self, client_socket, mock_writer):
        """Verifies that disconnect handles exceptions without failing."""
        client_socket._writer = mock_writer
        mock_writer.close.side_effect = Exception("Error while closing")

        # Should not raise an exception
        await client_socket.disconnect()


    @pytest.mark.asyncio
    async def test_disconnect_multiple_times(self, client_socket, mock_writer):
        """Verifies that disconnect can be called multiple times without error."""
        client_socket._writer = mock_writer

        await client_socket.disconnect()
        await client_socket.disconnect()

        assert client_socket._writer is None


# =============================================================================
# INTEGRATION
# =============================================================================

class TestClientSocketIntegration:
    """Integration tests for ClientSocket."""

    @pytest.mark.asyncio
    async def test_full_flow_connect_send_receive(self, client_socket, mock_reader, mock_writer):
        """Verifies the complete flow of connect, send, and receive."""
        with patch('asyncio.open_connection', return_value=(mock_reader, mock_writer)):
            # Connect
            await client_socket.connect()
            assert client_socket._reader is not None
            assert client_socket._writer is not None

            # Send
            message = {"type": "test"}
            await client_socket.send(message)
            mock_writer.write.assert_called()

            # Receive
            response = {"type": "response"}
            mock_reader.readline = AsyncMock(
                return_value=(json.dumps(response) + "\n").encode()
            )
            result = await client_socket.receive()
            assert result == response

            # Disconnect
            await client_socket.disconnect()
            assert client_socket._writer is None


    @pytest.mark.asyncio
    async def test_multiple_sends_without_receive(self, client_socket, mock_writer):
        """Verifies that multiple sends can be done without waiting for a response."""
        client_socket._writer = mock_writer

        messages = [{"type": f"message_{i}"} for i in range(5)]

        for message in messages:
            await client_socket.send(message)

        assert mock_writer.write.call_count == 5