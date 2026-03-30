# net/server/server.py

from net.server.pvp_session import PvPSession
from utils.log import configure_logger
from utils.log_decorator import log_async
from config.log_events import (
    SERVER_START, PLAYER_CONNECTED, QUEUE_ADD, PLAYER_DISCONNECTED,
    PLAYER_EXIT, PLAYER_CONNECTION_LOST, MATCH_CREATED
)
from net.helpers.send import send
from collections import deque
import asyncio
import json
import time


class Server:
    """
    Asynchronous TCP server responsible for managing client connections
    and matching players for PVP games.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8888) -> None:
        """
        Initializes the server.

        Args:
            host (str): Server IP address.
            port (int): Port to listen for connections.
        """
        self.host = host
        self.port = port
        self.waiting_queue = deque()
        self.queue_timestamps = {}  # Maps writer -> timestamp of entering queue
        self.active_games = []
        self._player_counter = 1
        self._game_counter = 1
        self._ids = {}
        self.logger = configure_logger()
        self.player_game = {}
        self._queue_lock = asyncio.Lock()
        self._counter_lock = asyncio.Lock()
        self._game_lock = asyncio.Lock()
        self.QUEUE_TIMEOUT = 15  # Seconds


    async def start(self) -> None:
        """
        Starts the TCP server and begins accepting connections.
        The server runs indefinitely via `serve_forever()`.

        Returns:
            None
        """
        server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )

        self.logger.info(f"{SERVER_START} host={self.host} port={self.port}")

        asyncio.create_task(self._matchmaker())

        async with server:
            await server.serve_forever()


    @log_async
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Manages the complete lifecycle of a connected client.

        Main responsibilities:
        - Assign a unique identifier to the player.
        - Register their connection in the server.
        - Add them to the waiting queue to be matched by the matchmaker.
        - Send the initial waiting message.
        - Receive and process messages sent by the client.
        - Forward messages to the corresponding game session if one exists.
        - Detect disconnections or exit requests.
        - Release resources and clean up references when the client leaves.

        Args:
            reader (asyncio.StreamReader): Client socket read stream.
            writer (asyncio.StreamWriter): Client socket write stream.

        Returns:
            None
        """
        addr = writer.get_extra_info("peername")

        async with self._counter_lock:
            player_id = self._player_counter
            self._player_counter += 1
            self._ids[writer] = player_id

        self.logger.info(f"{PLAYER_CONNECTED} player={player_id} addr={addr}")

        async with self._queue_lock:
            self.waiting_queue.append(writer)
            self.queue_timestamps[writer] = time.time()  # Store entry timestamp
            self.logger.info(f"{QUEUE_ADD} player={player_id} waiting={len(self.waiting_queue)}")

        await send(writer, {
            "type": "wait",
            "message": "Esperando rival..."
        })

        try:
            while True:
                data = await reader.readline()

                if not data:
                    self.logger.info(f"{PLAYER_DISCONNECTED} player={player_id} addr={addr}")

                    game = None
                    async with self._game_lock:
                        if writer in self.player_game:
                            game = self.player_game[writer]

                    if game:
                        await game.player_disconnected(writer, is_abandon=True)

                    break

                message = json.loads(data.decode().strip())
                if message.get("type") == "salir":
                    self.logger.info(f"{PLAYER_EXIT} player={player_id} addr={addr}")

                    game = None
                    async with self._game_lock:
                        if writer in self.player_game:
                            game = self.player_game[writer]

                    if game:
                        await game.player_disconnected(writer, is_abandon=True)

                    break

                game = None
                async with self._game_lock:
                    if writer in self.player_game:
                        game = self.player_game[writer]

                if game:
                    await game.receive_message(writer, message)

        except ConnectionResetError:
            self.logger.warning(f"{PLAYER_CONNECTION_LOST} player={player_id} addr={addr}")

            game = None
            async with self._game_lock:
                if writer in self.player_game:
                    game = self.player_game[writer]

            if game:
                await game.player_disconnected(writer, is_abandon=True)

        finally:
            game = None
            async with self._game_lock:
                if writer in self.player_game:
                    game = self.player_game[writer]

            if game:
                await game.player_disconnected(writer)

            async with self._queue_lock:
                if writer in self.waiting_queue:
                    self.waiting_queue.remove(writer)
                if writer in self.queue_timestamps:
                    del self.queue_timestamps[writer]

            async with self._counter_lock:
                if writer in self._ids:
                    del self._ids[writer]

            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass


    async def _matchmaker(self) -> None:
        """
        Asynchronous task that pairs players from the waiting queue
        and creates games when enough players are available.
        Also checks for timeouts on players who have waited too long.
        """
        while True:
            # Check for timeouts
            await self._check_queue_timeouts()

            session = None
            async with self._queue_lock:
                if len(self.waiting_queue) >= 2:
                    p1 = self.waiting_queue.popleft()
                    p2 = self.waiting_queue.popleft()
                    # Clean up timestamps
                    if p1 in self.queue_timestamps:
                        del self.queue_timestamps[p1]
                    if p2 in self.queue_timestamps:
                        del self.queue_timestamps[p2]
                else:
                    p1 = p2 = None

            if p1 is not None and p2 is not None:
                async with self._counter_lock:
                    id1 = self._ids.get(p1, -1)
                    id2 = self._ids.get(p2, -1)

                    # If either was cleaned up, do not create session
                    if id1 < 0 or id2 < 0:
                        p1 = p2 = None
                    else:
                        addr1 = p1.get_extra_info("peername")
                        addr2 = p2.get_extra_info("peername")

                        game_id = self._game_counter
                        self._game_counter += 1

            if p1 is not None and p2 is not None:
                session = PvPSession(
                    p1,
                    p2,
                    id1,
                    id2,
                    addr1,
                    addr2,
                    game_id,
                    self.logger,
                    self.player_game,
                    self._game_lock,
                    self.active_games
                )

                async with self._game_lock:
                    self.active_games.append(session)

            if session:
                await session.start()
                self.logger.info(f"{MATCH_CREATED} match={game_id} player1={id1} player2={id2}")

            await asyncio.sleep(0.1)


    async def _check_queue_timeouts(self) -> None:
        """
        Checks if any players in the waiting queue have exceeded the wait timeout.
        If so, removes them from the queue and sends a timeout message.

        Returns:
            None
        """
        current_time = time.time()

        async with self._queue_lock:
            timed_out_players = []

            # Identify players that have timed out
            for writer in list(self.waiting_queue):
                if writer in self.queue_timestamps:
                    wait_time = current_time - self.queue_timestamps[writer]
                    if wait_time >= self.QUEUE_TIMEOUT:
                        timed_out_players.append(writer)

            # Remove from queue
            for writer in timed_out_players:
                try:
                    self.waiting_queue.remove(writer)
                    del self.queue_timestamps[writer]
                except (ValueError, KeyError):
                    pass

        # Send messages (outside the lock to avoid blocking)
        for writer in timed_out_players:
            try:
                await send(writer, {
                    "type": "timeout_cola",
                    "razon": "rivales_no_disponibles"
                })

                # Get ID for logging
                async with self._counter_lock:
                    player_id = self._ids.get(writer, -1)

                if player_id >= 0:
                    self.logger.info(f"PLAYER_TIMEOUT player={player_id} reason=no_opponent_available")

            except Exception as e:
                self.logger.warning(f"Error sending timeout: {e}")


if __name__ == "__main__":
    server = Server()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped manually. Closing games...")
        for session in server.active_games:
            for w in session._writers.values():
                try:
                    w.close()
                    asyncio.run(w.wait_closed())
                except:
                    pass
        print("[INFO] All games closed.")