# net/protocol/messages.py

from enum import Enum
from typing import Any, TypedDict, TypeAlias


class MessageType(str, Enum):
    """
    Enumeration of client-server protocol message types.
    Each value represents an action or event within the game flow.
    """
    WAIT = "wait"
    START = "start"
    SHIP_LIST = "ship_list"
    SELECT_SHIP = "select_ship"
    SHOT = "shot"
    RESULT = "result"
    RECEIVED = "received"
    BOARD_STATE = "board_state"
    TURN = "turn"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    END = "end"
    EXIT = "exit"
    ABANDON = "abandon"
    CONNECTION_CLOSED = "connection_closed"
    QUEUE_TIMEOUT = "queue_timeout"


class BaseMessage(TypedDict):
    """
    Base type for all protocol messages.

    All messages must include the `type` field.
    """
    type: str


class StartMessage(BaseMessage):
    """
    Message sent by the server when starting the game.

    Attributes:
        type (str): Message type ("start").
        player (int): Assigned player identifier (1 or 2).
    """
    player: int


class ShipListMessage(BaseMessage):
    """
    Message containing the list of ships pending placement.

    Attributes:
        ships (list[dict[str, Any]]): List of available ships.
    """
    ships: list[dict[str, Any]]


class SelectShipMessage(BaseMessage):
    """
    Message sent by the client to place a ship.

    Attributes:
        index (int): Index of the selected ship.
        x (int): Horizontal coordinate.
        y (int): Vertical coordinate.
        horizontal (bool): Ship orientation.
    """
    index: int
    x: int
    y: int
    horizontal: bool


class ShotMessage(BaseMessage):
    """
    Message sent by the client to fire a shot.

    Attributes:
        x (int): Horizontal coordinate of the shot.
        y (int): Vertical coordinate of the shot.
    """
    x: int
    y: int


class ResultMessage(BaseMessage):
    """
    Shot result sent to the attacking player.

    Attributes:
        result (str): Shot result.
        x (int): Horizontal coordinate.
        y (int): Vertical coordinate.
    """
    result: str
    x: int
    y: int


class ReceivedMessage(BaseMessage):
    """
    Message sent to the opponent when they receive a shot.

    Attributes:
        result (str): Shot result.
        x (int): Horizontal coordinate.
        y (int): Vertical coordinate.
    """
    result: str
    x: int
    y: int


class TurnMessage(BaseMessage):
    """
    Message indicating whether it is the player's turn.

    Attributes:
        your_turn (bool): Indicates if the player can shoot.
    """
    your_turn: bool


class BoardStateMessage(BaseMessage):
    """
    Message containing the board state.

    Attributes:
        own (Any): Player's own board state.
        opponent (Any): Visible opponent board state.
    """
    own: Any
    opponent: Any


class ConfirmationMessage(BaseMessage):
    """
    Confirmation message for an action.

    Attributes:
        message (str): Informational text.
    """
    message: str


class ErrorMessage(BaseMessage):
    """
    Error message sent by the server.

    Attributes:
        message (str): Error description.
    """
    message: str


class EndMessage(BaseMessage):
    """
    Message sent at the end of the game.

    Attributes:
        victory (bool): Indicates whether the player has won.
        pvp (bool): Indicates if the game is PvP.
    """
    victory: bool
    pvp: bool


class AbandonMessage(BaseMessage):
    """
    Message sent if a player disconnects.

    Attributes:
        abandon (bool): Indicates if the opponent has disconnected.
    """
    abandon: bool


class ConnectionClosedMessage(BaseMessage):
    """
    Message sent if the server shuts down.

    Attributes:
        message (str): Message communicating the server closure.
    """
    message: str


class QueueTimeoutMessage(BaseMessage):
    """
    Message sent if the player waits more than 15 seconds without an opponent.

    Attributes:
        reason (str): Reason for the timeout (no opponents available).
    """
    reason: str


ProtocolMessage: TypeAlias = (
    StartMessage
    | ShipListMessage
    | SelectShipMessage
    | ShotMessage
    | ResultMessage
    | ReceivedMessage
    | TurnMessage
    | BoardStateMessage
    | ConfirmationMessage
    | ErrorMessage
    | EndMessage
    | AbandonMessage
    | ConnectionClosedMessage
    | QueueTimeoutMessage
)


def create_message(msg_type: MessageType, **data: Any) -> dict[str, Any]:
    """
    Builds a protocol message.
    The message always contains the `type` field and may include any
    additional data required for the event.

    Args:
        msg_type (MessageType): Type of message.
        **data (Any): Additional message data.

    Returns:
        dict[str, Any]: Dictionary ready to be serialized as JSON.
    """
    message = {"type": msg_type.value}
    message.update(data)
    return message


def get_type(message: dict[str, Any]) -> MessageType:
    """
    Converts the received `type` field into its Enum value.

    Args:
        message (dict[str, Any]): Message received from client or server.

    Returns:
        MessageType: Type of the message.
    """
    return MessageType(message["type"])