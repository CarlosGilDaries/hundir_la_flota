# controller/controller_pvp_client.py

import asyncio
from controller.controller import Controller
from net.protocol.messages import MessageType, get_type, create_message
from net.client.client_socket import ClientSocket
from view.console.console_view import ConsoleView


class PvPClientController(Controller):
    """
    Controller for the PvP game client. Handles communication with the server
    and coordinates the game flow using the console view.
    """

    def __init__(self, client_socket: ClientSocket, view: ConsoleView) -> None:
        """
        Initializes the PvP client controller.

        Args:
            client_socket (ClientSocket): Client responsible for server communication.
            view (ConsoleView): View used to display information to the player.
        """
        self._client = client_socket
        self._view = view
        self._state = None
        self._playing = True
        self._placing = False
        self._my_turn = False
        self._input_task = None
        self._available_ships = []
        self._input_active = False

        self._handlers = {
            MessageType.WAIT: self._handle_wait,
            MessageType.START: self._handle_start,
            MessageType.SHIP_LIST: self._handle_ship_list,
            MessageType.CONFIRMATION: self._handle_confirmation,
            MessageType.RECEIVED: self._handle_received,
            MessageType.BOARD_STATE: self._handle_board_state,
            MessageType.RESULT: self._handle_result,
            MessageType.TURN: self._handle_turn,
            MessageType.END: self._handle_end,
            MessageType.ERROR: self._handle_error,
            MessageType.ABANDON: self._handle_abandon,
            MessageType.CONNECTION_CLOSED: self._handle_connection_closed,
            MessageType.QUEUE_TIMEOUT: self._handle_queue_timeout
        }


    async def start(self) -> None:
        """
        Starts the connection to the server and begins listening for messages.
        """
        self._view.display_message("\nConectando al servidor...\n")
        await self._client.connect()
        await self._listen_to_server()


    async def _listen_to_server(self) -> None:
        """
        Continuously listens for messages from the server.
        """
        while self._playing:
            message = await self._client.receive()
            # print("MESSAGE RECEIVED BY CONTROLLER:", message)
            if message is None:
                self._view.clear_console()
                self._view.display_message("Conexión cerrada por el servidor. Pulse Intro para continuar...")
                self._playing = False
                break

            msg_type = get_type(message)
            # print("MESSAGE TYPE:", msg_type)
            await self._dispatch(msg_type, message)


    async def _dispatch(self, msg_type: MessageType, message: dict) -> None:
        """
        Dispatches the received message to the appropriate handler.

        Args:
            msg_type (MessageType): Type of the received message.
            message (dict): Message data.
        """
        handler = self._handlers.get(msg_type)
        if handler:
            await handler(message)
        else:
            self._view.display_message(f"Mensaje desconocido: {msg_type}")


    async def async_input(self, prompt: str) -> str:
        """
        Asks for user input without blocking the asyncio loop.

        Args:
            prompt (str): Text displayed to the user.

        Returns:
            str: User input.
        """
        loop = asyncio.get_event_loop()
        try:
            self._input_active = True
            value = await loop.run_in_executor(None, input, prompt)
            return value

        except KeyboardInterrupt:
            await self.leave_game()
            return "salir"

        finally:
            self._input_active = False


    async def read_integer(self, prompt: str, min_val: int | None = None, max_val: int | None = None) -> int | None:
        """
        Asks the user for a validated integer.

        Args:
            prompt (str): Text displayed to the user.
            min_val (int | None): Minimum allowed value.
            max_val (int | None): Maximum allowed value.

        Returns:
            int | None: Entered number or None if the user decides to exit.
        """
        while True:
            value = await self.async_input(prompt)

            if value.lower() == "salir":
                await self.leave_game()
                return None

            try:
                number = int(value)

                if min_val is not None and number < min_val:
                    raise ValueError

                if max_val is not None and number > max_val:
                    raise ValueError

                return number

            except ValueError:
                if min_val is not None and max_val is not None:
                    self._view.display_message(
                        f"\nERROR: Introduce un número entre {min_val} y {max_val}"
                    )
                else:
                    self._view.display_message("\nERROR: Introduce un número válido")


    async def placement_phase(self) -> None:
        """
        Manages the ship placement phase for the player.
        """
        try:
            while True:
                if not self._available_ships:
                    self._view.display_message("No hay barcos disponibles.")
                    return

                valid_indices = [ship["index"] for ship in self._available_ships]

                # select ship
                while True:
                    index = await self.read_integer(
                        "\nSelecciona número de barco: "
                    )

                    if index is None:
                        return

                    if index in valid_indices:
                        break

                    self._view.display_message(
                        f"\nERROR: Índice inválido. Opciones: {valid_indices}"
                    )

                ship = next(s for s in self._available_ships if s["index"] == index)
                size = ship["size"]

                # coordinates
                x = await self.read_integer("\nCoordenada X para colocación del barco (0-9): ", 0, 9)
                if x is None:
                    return

                y = await self.read_integer("\nCoordenada Y para colocación del barco (0-9): ", 0, 9)
                if y is None:
                    return

                # orientation
                while True:
                    orientation = await self.async_input(
                        "\nHorizontal o Vertical (h/v): "
                    )

                    if orientation.lower() == "salir":
                        await self.leave_game()
                        return

                    if orientation.lower() in ("h", "v"):
                        horizontal = orientation.lower() == "h"
                        break

                    self._view.display_message(
                        "\nERROR: Debes introducir 'h' o 'v'"
                    )

                if not self._validate_ship_fits(x, y, size, horizontal):
                    self._view.display_message(
                        "\nERROR: El barco se sale del tablero. Prueba otra posición."
                    )
                    continue

                # send to server
                await self._client.send(
                    create_message(
                        MessageType.SELECT_SHIP,
                        index=index,
                        name=ship["name"],
                        x=x,
                        y=y,
                        horizontal=horizontal
                    )
                )
                break

        except asyncio.CancelledError:
            return


    async def turn_phase(self) -> None:
        """
        Manages the player's turn to fire.
        """
        self._view.display_message("\nEscribe 'salir' para abandonar.")
        try:
            x = await self.read_integer(
                "\nCoordenada X del disparo (0-9): ", 0, 9
            )

            if x is None:
                return

            y = await self.read_integer(
                "\nCoordenada Y del disparo (0-9): ", 0, 9
            )
            if y is None:
                return

            await self._client.send(
                create_message(
                    MessageType.SHOT,
                    x=x,
                    y=y
                )
            )

        except asyncio.CancelledError:
            return


    async def _handle_start(self, message: dict) -> None:
        """
        Handles the game start, assigning player number and beginning the placement phase.
        """
        self._view.clear_console()
        self._view.display_message(f"\nEres el jugador {message['player']}\n")
        self._placing = True
        self._view.display_message("Fase de colocación de barcos iniciada.")
        # if not self._input_task or self._input_task.done():
        #     self._input_task = asyncio.create_task(self.placement_phase())


    async def _handle_ship_list(self, message: dict) -> None:
        """
        Handles the list of ships sent by the server.
        Displays available ships and starts the placement phase.
        """
        ships = message["ships"]
        self._available_ships = ships
        self._view.display_message("\nEscribe 'salir' para abandonar.")
        self._view.display_message("\nBarcos disponibles:\n")
        for s in ships:
            self._view.display_message(f"{s['index']} - {s['name']} ({s['size']})")

        if self._placing and (not self._input_task or self._input_task.done()):
            self._input_task = asyncio.create_task(self.placement_phase())


    async def _handle_confirmation(self, message: dict) -> None:
        """
        Displays a confirmation message from the server.
        """
        self._view.clear_console()
        self._view.display_message(f"\nConfirmación: {message['message']}")


    async def _handle_wait(self, message: dict) -> None:
        """
        Handles the waiting state when the player cannot act.
        Cancels any ongoing input task.
        """
        self._view.display_message(message["message"])

        self._placing = False

        if self._input_task:
            self._input_task.cancel()
            self._input_task = None


    async def _handle_turn(self, message: dict) -> None:
        """
        Handles the current turn, enabling or disabling user input.
        """
        # FINISH PLACEMENT
        if self._placing:
            self._placing = False

            if self._input_task:
                self._input_task.cancel()
                self._input_task = None

        self._my_turn = message["your_turn"]

        if self._my_turn:
            self._view.display_message("\nEs tu turno.")

            self._input_task = asyncio.create_task(self.turn_phase())

        else:
            self._view.display_message("\nTurno del rival.")


    async def _handle_result(self, message: dict) -> None:
        """
        Displays the result of a shot fired by the player.
        """
        self._view.clear_console()
        result = message['result'] if message['result'] != "REPEATED" else "REPEATED_PVP"
        text = f"{self._view.get_text(result)}"
        self._view.display_message(f"\nDisparo en ({message['x']},{message['y']}): {text}")


    async def _handle_received(self, message: dict) -> None:
        """
        Displays the result of a shot received by the player.
        """
        self._view.clear_console()
        result = message['result'] if message['result'] != "REPEATED" else "REPEATED_PVP"
        text = f"{self._view.get_text(result)}"
        self._view.display_message(f"\nTe dispararon en ({message['x']},{message['y']}): {text}")


    async def _handle_board_state(self, message: dict) -> None:
        """
        Updates the display of the player's and opponent's boards.
        """
        if self._input_active:
            return

        self._view.display_boards(
            message["own"],
            message["opponent"]
        )


    async def _handle_end(self, message: dict) -> None:
        """
        Handles the end of the game, showing the result and closing the connection.
        """
        victory = message["victory"]
        self._view.display_final_message(victory, True)
        await self.async_input("\nPULSA INTRO PARA VOLVER AL MENÚ...")
        self._playing = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()
        await self._client.disconnect()


    async def _handle_abandon(self, message: dict) -> None:
        """
        Handles the end of the game due to opponent abandonment.
        """
        abandon = message["abandon"]
        self._view.display_abandon_message(abandon)
        self._playing = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()
        await self.async_input("\nPULSA INTRO PARA VOLVER AL MENÚ...")
        await self._client.disconnect()


    async def _handle_connection_closed(self, message: dict) -> None:
        """
        Handles disconnection due to server shutdown.
        """
        self._view.clear_console()
        self._view.display_message("Conexión cerrada por el servidor. Pulse Intro para continuar...")
        self._playing = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()
        await self._client.disconnect()


    async def _handle_queue_timeout(self, message: dict) -> None:
        """
        Handles timeout while waiting for an opponent in the queue.
        """
        self._view.clear_console()
        self._view.display_message("\nNo se encontró ningún rival disponible tras 15 segundos. Vuelva a intentarlo más tarde.\n")
        await self.async_input("\nPULSA INTRO PARA VOLVER AL MENÚ...")
        self._playing = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()
        await self._client.disconnect()


    async def _handle_error(self, message: dict) -> None:
        """
        Handles an error message received from the server.
        If the player is in placement phase, restarts the placement task.
        """
        self._view.display_message(f"\nError: {message['message']}")

        if self._placing:
            if not self._input_task or self._input_task.done():
                self._input_task = asyncio.create_task(self.placement_phase())


    def _validate_ship_fits(self, x: int, y: int, size: int, horizontal: bool) -> bool:
        """
        Checks if a ship fits within the board.

        Args:
            x (int): Starting X coordinate.
            y (int): Starting Y coordinate.
            size (int): Ship size.
            horizontal (bool): Ship orientation.

        Returns:
            bool: True if the ship fits inside the board.
        """
        if horizontal:
            return x + size <= 10
        else:
            return y + size <= 10


    async def leave_game(self) -> None:
        """
        Abandons the current game and closes the connection to the server.
        """
        self._view.display_message("Saliendo de la partida...")
        self._playing = False
        self._placing = False
        if self._input_task and not self._input_task.done():
            self._input_task.cancel()
        await self._client.send({"type": "exit"})
        await self._client.disconnect()