from model.game.pvp_game import GameState
from config.texts import TRANSLATION
from config.log_events import (
    SESSION_CREATED, SESSION_STARTED, SESSION_ENDED,
    SHIP_PLACED, PLACEMENT_ERROR, FIRST_TURN,
    TURN_CHANGE, SHOT, SHOT_ERROR, WINNER, PLAYER_DISCONNECTED
)
from net.protocol.messages import MessageType, create_message, get_type
from net.helpers.send import send
from config.constants import CONSTANTS
from services.game_service import GameService
from utils.log_decorator import log_async
from typing import Dict, Any
from asyncio import StreamWriter
import asyncio


class PvPSession:
    """
    Represents a PVP game session between two connected players.

    Manages:
    - client-server message flow
    - game phases
    - turns
    - board synchronization
    """


    def __init__(self, writer1: StreamWriter, writer2: StreamWriter,
                 id1: int, id2: int, addr1, addr2, game_id: int,
                 logger, player_game: Dict[StreamWriter, "PvPSession"],
                 game_lock: asyncio.Lock, active_games: list) -> None:
        self._ended_event = asyncio.Event()
        self.game_id: int = game_id
        self._writers: Dict[int, StreamWriter] = {
            1: writer1,
            2: writer2
        }
        self._players: Dict[StreamWriter, int] = {
            writer1: 1,
            writer2: 2
        }
        self._player_ids = {
            1: id1,
            2: id2
        }
        self._addrs = {
            1: addr1,
            2: addr2
        }
        self._service = GameService(
            CONSTANTS["DIFFICULTY"]["PVP"],
            CONSTANTS["CHARACTERS"]
        )
        self._game_lock = game_lock
        self._active_games = active_games
        self.player_game = player_game

        # Register in shared dictionary with synchronization
        # Note: The server already protects this with game_lock before creating the session
        player_game[writer1] = self
        player_game[writer2] = self
        self.logger = logger

        self.logger.info(
            f"MATCH_SESSION_CREATED match={self.game_id} "
            f"player1={id1}@{addr1} player2={id2}@{addr2}"
        )


    def _log_event(self, event: str, **kwargs) -> None:
        """
        Helper to log events consistently.

        Args:
            event (str): Event name (from config.eventos_log)
            **kwargs: Additional parameters for the log (e.g., player=1, x=5, y=3)

        Returns:
            None
        """
        params = f"match={self.game_id}"
        for key, value in kwargs.items():
            params += f" {key}={value}"
        self.logger.info(f"{event} {params}")


    @log_async
    async def start(self) -> None:
        """
        Starts the game session by sending initial messages.

        Returns:
            None
        """
        self._log_event(SESSION_STARTED)

        for player, writer in self._writers.items():
            await send(writer, create_message(
                MessageType.START,
                player=player,
                state=self._service.state().value
            ))
            await self._send_ships(player)


    async def receive_message(self, writer: StreamWriter, message: dict) -> None:
        """
        Processes a message received from a client.

        Args:
            writer (StreamWriter): Client socket.
            message (dict): Received message.

        Returns:
            None
        """
        player = self._players[writer]
        msg_type = get_type(message)
        state = self._service.state()

        if state == GameState.PLACEMENT:
            await self._placement_phase(player, message, msg_type)

        elif state == GameState.PLAYING:
            await self._turn_phase(player, message, msg_type)


    async def _placement_phase(self, player: int, message: dict[str, Any], msg_type) -> None:
        """
        Manages the ship placement phase for a player.
        Processes the client's message to attempt placing a ship.
        If placement is valid, updates the board state and sends confirmation.
        If invalid, notifies the error.

        Args:
            player (int): Player identifier (1 or 2).
            message (dict[str, Any]): Message received from the client with
                ship placement data. Contains:
                    - index (int): ship index
                    - x (int): horizontal coordinate
                    - y (int): vertical coordinate
                    - horizontal (bool): ship orientation
            msg_type (MessageType): Type of received message.

        Returns:
            None
        """
        if msg_type != MessageType.SELECT_SHIP:
            return

        writer = self._writers[player]
        player_id = self._player_ids[player]

        try:
            placed = self._service.place_ship(
                player,
                message["index"],
                message["x"],
                message["y"],
                message["horizontal"]
            )

            if placed:
                await send(writer, create_message(
                    MessageType.CONFIRMATION,
                    message="Barco colocado correctamente"
                ))

                self._log_event(
                    SHIP_PLACED,
                    player=player_id,
                    boat=message.get("name", f"boat_{message['index']}"),
                    x=message["x"],
                    y=message["y"],
                    horizontal=message["horizontal"]
                )

            else:
                await send(writer, create_message(
                    MessageType.ERROR,
                    message="Posición inválida"
                ))

                self._log_event(
                    PLACEMENT_ERROR,
                    player=player_id,
                    boat=message.get("name", f"boat_{message['index']}"),
                    reason="invalid_position"
                )

                return

            await self._send_state(player)
            pending = self._service.remaining_ships(player)

            if pending:
                await self._send_ships(player)

            else:
                await send(writer, create_message(
                    MessageType.WAIT,
                    message="Esperando al rival..."
                ))

            if self._service.state() == GameState.PLAYING:
                await self._update_turns()
                self._log_event(FIRST_TURN, player=self._player_ids[self._service.current_turn()])

        except Exception as e:
            await send(writer, create_message(
                MessageType.ERROR,
                message=str(e)
            ))

            self._log_event(
                PLACEMENT_ERROR,
                player=player_id,
                boat=message.get("name", f"boat_{message.get('index', '?')}"),
                reason=str(e)
            )


    @log_async
    async def _turn_phase(self, player: int, message: dict[str, Any], msg_type: MessageType) -> None:
        """
        Manages the shooting phase during a player's turn.
        Receives shot coordinates, executes the action via the game service,
        and sends the result to both the shooter and the opponent.

        Args:
            player (int): Player identifier who is shooting.
            message (dict[str, Any]): Received message with shot coordinates.
                Contains:
                    - x (int): horizontal coordinate
                    - y (int): vertical coordinate
            msg_type (MessageType): Type of received message.

        Returns:
            None
        """
        if msg_type != MessageType.SHOT:
            return

        writer = self._writers[player]
        player_id = self._player_ids[player]

        try:
            result = self._service.shoot(
                player,
                message["x"],
                message["y"]
            )
            result_str = TRANSLATION[result]
            opponent = 2 if player == 1 else 1
            opponent_writer = self._writers[opponent]

            await send(writer, create_message(
                MessageType.RESULT,
                result=result_str,
                x=message["x"],
                y=message["y"]
            ))
            await send(opponent_writer, create_message(
                MessageType.RECEIVED,
                result=result_str,
                x=message["x"],
                y=message["y"]
            ))

            self._log_event(
                SHOT,
                player=player_id,
                x=message["x"],
                y=message["y"],
                result=result_str
            )

            await self._send_state(player)
            await self._send_state(opponent)

            if self._service.check_victory():
                self._log_event(WINNER, player=f"{player_id} addr={self._addrs[player]}")
                await self._finish_game()
                self._ended = True
                self._log_event(SESSION_ENDED)

            else:
                await self._update_turns()

        except Exception as e:
            await send(writer, create_message(
                MessageType.ERROR,
                message=str(e)
            ))

            self._log_event(
                SHOT_ERROR,
                player=player_id,
                x=message.get("x", "?"),
                y=message.get("y", "?"),
                reason=str(e)
            )


    async def _update_turns(self) -> None:
        """
        Notifies both players of the current turn.
        Sends a message indicating whether each player has the turn.

        Returns:
            None
        """
        turn = self._service.current_turn()
        self._log_event(TURN_CHANGE, player=self._player_ids[turn])

        for player, writer in list(self._writers.items()):
            await send(writer, create_message(
                MessageType.TURN,
                your_turn=player == turn
            ))


    async def _finish_game(self) -> None:
        """
        Ends the game and notifies both players of the result.
        Determines the winner through the game service and sends
        a victory/defeat message to each client.

        Returns:
            None
        """
        winner = self._service.winning_player()

        for player, writer in list(self._writers.items()):
            await send(writer, create_message(
                MessageType.END,
                victory=player == winner
            ))


    async def _send_state(self, player: int) -> None:
        """
        Sends the current board state to the player.
        Includes both the player's own board and the visible opponent's board.

        Args:
            player (int): Player identifier.

        Returns:
            None
        """
        writer = self._writers[player]
        state = self._service.get_boards_state(player)

        await send(writer, create_message(
            MessageType.BOARD_STATE,
            own=state["own"],
            opponent=state["opponent"]
        ))


    async def _send_ships(self, player: int) -> None:
        """
        Sends the list of ships that still need to be placed to the player.
        This message is used during the initial preparation phase.

        Args:
            player (int): Player identifier.

        Returns:
            None
        """
        writer = self._writers[player]
        ship_list = self._service.remaining_ships(player)

        await send(writer, create_message(
            MessageType.SHIP_LIST,
            ships=ship_list
        ))


    @log_async
    async def player_disconnected(self, writer: StreamWriter, is_abandon: bool = False) -> None:
        """
        Handles a player disconnection during a game.
        Automatically ends the game, granting victory to the remaining player
        if the disconnection was voluntary.

        Args:
            writer (StreamWriter): Connection of the disconnected player.
            is_abandon (bool): True if it was a voluntary exit (typed 'salir'),
                               False if it was a disconnection/server closure.

        Returns:
            None
        """
        # Atomic check with Event (only the first call proceeds)
        if self._ended_event.is_set():
            return

        self._ended_event.set()

        if writer not in self._players:
            return

        player = self._players[writer]
        opponent = 2 if player == 1 else 1
        opponent_writer = self._writers.get(opponent)

        self._log_event(
            PLAYER_DISCONNECTED,
            player=self._player_ids[player]
        )

        # Only log winner if it was a voluntary abandon
        if is_abandon:
            self._log_event(WINNER, player=f"{self._player_ids[opponent]} addr={self._addrs[opponent]}")
        else:
            self._log_event("SERVER_SHUTDOWN", player=f"{self._player_ids[player]} addr={self._addrs[player]}")

        # Notify opponent with appropriate message
        if opponent_writer:
            try:
                if is_abandon:
                    # Player voluntarily left → Victory by abandonment
                    msg_type = MessageType.ABANDON
                    data = {"abandon": True}
                else:
                    # Server shutdown → Connection closed
                    msg_type = MessageType.CONNECTION_CLOSED
                    data = {"reason": "server_shutdown"}

                await send(opponent_writer,
                           create_message(msg_type, **data))
            except:
                pass

        # Clean up references with synchronization
        async with self._game_lock:
            if writer in self.player_game:
                del self.player_game[writer]

            if opponent_writer and opponent_writer in self.player_game:
                del self.player_game[opponent_writer]

        # Remove from active games list
        try:
            self._active_games.remove(self)
        except ValueError:
            pass  # Already removed

        # Close writers if still open
        for w in list(self._writers.values()):
            try:
                w.close()
                await w.wait_closed()
            except:
                pass

        self._log_event(SESSION_ENDED)