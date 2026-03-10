import asyncio
from controlador.controlador import Controlador
from red.protocolo.mensajes import TipoMensaje, obtener_tipo, crear_mensaje
from red.cliente.cliente_socket import ClienteSocket
from vista.consola.vista_consola import VistaConsola

class ControladorPVPCliente(Controlador):

    def __init__(self, cliente_socket: ClienteSocket, vista: VistaConsola) -> None:
        """
        Inicializa el controlador del cliente PVP.

        Args:
            cliente_socket (ClienteSocket): Cliente encargado de la comunicación con el servidor.
            vista (VistaConsola): Vista utilizada para mostrar información al jugador.

        Returns:
            None
        """
        self._cliente = cliente_socket
        self._vista = vista
        self._estado = None
        self._jugando = True
        self._colocando = False
        self._mi_turno = False
        self._tarea_input = None
        self._barcos_disponibles = []
        self._input_activo = False

        self._handlers = {
            TipoMensaje.ESPERA: self._manejar_espera,
            TipoMensaje.INICIO: self._manejar_inicio,
            TipoMensaje.LISTA_BARCOS: self._manejar_lista_barcos,
            TipoMensaje.CONFIRMACION: self._manejar_confirmacion,
            TipoMensaje.RECIBIDO: self._manejar_recibido,
            TipoMensaje.ESTADO_TABLEROS: self._manejar_estado_tableros,
            TipoMensaje.RESULTADO: self._manejar_resultado,
            TipoMensaje.TURNO: self._manejar_turno,
            TipoMensaje.FIN: self._manejar_fin,
            TipoMensaje.ERROR: self._manejar_error,
            TipoMensaje.ABANDONO: self._manejar_abandono
        }


    async def iniciar(self) -> None:
        """
        Inicia la conexión con el servidor y comienza a escuchar mensajes.

        Returns:
            None
        """
        self._vista.mostrar_mensaje("\nConectando al servidor...\n")
        await self._cliente.conectar()
        await self._escuchar_servidor()


    async def _escuchar_servidor(self) -> None:
        """
        Escucha continuamente mensajes provenientes del servidor.

        Returns:
            None
        """
        while self._jugando:
            mensaje = await self._cliente.recibir()
            # print("MENSAJE RECIBIDO POR CONTROLADOR:", mensaje)
            if mensaje is None:
                self._vista.mostrar_mensaje("Conexión cerrada por el servidor.")
                self._jugando = False
                break
            
            tipo = obtener_tipo(mensaje)
            # print("TIPO MENSAJE:", tipo)
            await self._dispatch(tipo, mensaje)


    async def _dispatch(self, tipo: TipoMensaje, mensaje: dict) -> None:
        """
        Despacha el mensaje recibido al handler correspondiente.

        Args:
            tipo (TipoMensaje): Tipo de mensaje recibido.
            mensaje (dict): Datos del mensaje.

        Returns:
            None
        """
        handler = self._handlers.get(tipo)
        if handler:
            await handler(mensaje)
        else:
            self._vista.mostrar_mensaje(f"Mensaje desconocido: {tipo}")


    async def input_async(self,  prompt: str) -> str:
        """
        Solicita input al usuario sin bloquear el loop de asyncio.

        Args:
            prompt (str): Texto mostrado al usuario.

        Returns:
            str: Texto introducido por el usuario.
        """
        loop = asyncio.get_event_loop()
        try:
            self._input_activo = True
            valor = await loop.run_in_executor(None, input, prompt)
            return valor

        except KeyboardInterrupt:
            await self.salir_partida()
            return "salir"

        finally:
            self._input_activo = False


    async def leer_entero(self, prompt: str, minimo: int | None = None, maximo: int | None = None) -> int | None:
        """
        Solicita al usuario un número entero validado.

        Args:
            prompt (str): Texto mostrado al usuario.
            minimo (int | None): Valor mínimo permitido.
            maximo (int | None): Valor máximo permitido.

        Returns:
            int | None: Número introducido o None si el usuario decide salir.
        """
        while True:
            valor = await self.input_async(prompt)

            if valor.lower() == "salir":
                await self.salir_partida()
                return None

            try:
                numero = int(valor)

                if minimo is not None and numero < minimo:
                    raise ValueError

                if maximo is not None and numero > maximo:
                    raise ValueError

                return numero

            except ValueError:
                if minimo is not None and maximo is not None:
                    self._vista.mostrar_mensaje(
                        f"\nERROR: Introduce un número entre {minimo} y {maximo}"
                    )
                else:
                    self._vista.mostrar_mensaje("\nERROR: Introduce un número válido")


    async def fase_colocacion(self) -> None:
        """
        Gestiona la fase de colocación de barcos del jugador.

        Returns:
            None
        """
        try:
            while True:
                if not self._barcos_disponibles:
                    self._vista.mostrar_mensaje("No hay barcos disponibles.")
                    return

                indices_validos = [b["indice"] for b in self._barcos_disponibles]

                # seleccionar barco
                while True:
                    indice = await self.leer_entero(
                        "\nSelecciona número de barco: "
                    )

                    if indice is None:
                        return

                    if indice in indices_validos:
                        break

                    self._vista.mostrar_mensaje(
                        f"\nERROR: Índice inválido. Opciones: {indices_validos}"
                    )
                
                barco = next(b for b in self._barcos_disponibles if b["indice"] == indice)
                tamanyo = barco["tamanyo"]

                # coordenadas
                x = await self.leer_entero("\nCoordenada X para colocación del barco (0-9): ", 0, 9)
                if x is None:
                    return

                y = await self.leer_entero("\nCoordenada Y para colocación del barco (0-9): ", 0, 9)
                if y is None:
                    return

                # orientación
                while True:
                    orientacion = await self.input_async(
                        "\nHorizontal o Vertical (h/v): "
                    )

                    if orientacion.lower() == "salir":
                        await self.salir_partida()
                        return

                    if orientacion.lower() in ("h", "v"):
                        horizontal = orientacion.lower() == "h"
                        break

                    self._vista.mostrar_mensaje(
                        "\nERROR: Debes introducir 'h' o 'v'"
                    )
                
                if not self.validar_barco_en_tablero(x, y, tamanyo, horizontal):
                    self._vista.mostrar_mensaje(
                        "\nERROR: El barco se sale del tablero. Prueba otra posición."
                    )
                    continue

                # enviar al servidor
                await self._cliente.enviar(
                    crear_mensaje(
                        TipoMensaje.SELECCIONAR_BARCO,
                        indice=indice,
                        x=x,
                        y=y,
                        horizontal=horizontal
                    )
                )
                break
    
        except asyncio.CancelledError:
            return


    async def fase_turno(self) -> None:
        """
        Gestiona el turno de disparo del jugador.

        Returns:
            None
        """
        self._vista.mostrar_mensaje("\nEscribe 'salir' para abandonar.")
        try:
            x = await self.leer_entero(
                "\nCoordenada X del disparo (0-9): ", 0, 9
            )

            if x is None:
                return

            y = await self.leer_entero(
                "\nCoordenada Y del disparo (0-9): ", 0, 9
            )
            if y is None:
                return

            await self._cliente.enviar(
                crear_mensaje(
                    TipoMensaje.DISPARO,
                    x=x,
                    y=y
                )
            )
            
        except asyncio.CancelledError:
            return


    async def _manejar_inicio(self, mensaje: dict) -> None:
        """
        Maneja el inicio de la partida asignando el número de jugador y comenzando la fase de colocación de barcos.
        Muestra al jugador su identificador y un mensaje indicando que puede comenzar a colocar sus barcos.

        Args:
            mensaje (dict): Mensaje recibido del servidor que contiene el número de jugador bajo la clave 'jugador'.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(f"\nEres el jugador {mensaje['jugador']}\n")
        self._colocando = True
        self._vista.mostrar_mensaje("Fase de colocación de barcos iniciada.")
        # if not self._tarea_input or self._tarea_input.done():
        #     self._tarea_input = asyncio.create_task(self.fase_colocacion())


    async def _manejar_lista_barcos(self, mensaje: dict) -> None:
        """
        Maneja la lista de barcos enviada por el servidor.
        Muestra los barcos disponibles y lanza la fase de colocación si corresponde.

        Args:
            mensaje (dict): Mensaje recibido del servidor con la lista de barcos.

        Returns:
            None
        """
        barcos = mensaje["barcos"]
        self._barcos_disponibles = barcos
        self._vista.mostrar_mensaje("\nEscribe 'salir' para abandonar.")
        self._vista.mostrar_mensaje("\nBarcos disponibles:\n")
        for b in barcos:
            self._vista.mostrar_mensaje(f"{b['indice']} - {b['nombre']} ({b['tamanyo']})")
            
        if self._colocando and (not self._tarea_input or self._tarea_input.done()):
            self._tarea_input = asyncio.create_task(self.fase_colocacion())


    async def _manejar_confirmacion(self, mensaje: dict) -> None:
        """
        Muestra un mensaje de confirmación recibido del servidor.

        Args:
            mensaje (dict): Mensaje de confirmación.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(f"\nConfirmación: {mensaje['mensaje']}")


    async def _manejar_espera(self, mensaje: dict) -> None:
        """
        Maneja el estado de espera cuando el jugador no puede actuar.
        Cancela la tarea de colocación si estaba activa.

        Args:
            mensaje (dict): Mensaje recibido del servidor indicando espera.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(mensaje["mensaje"])

        self._colocando = False

        if self._tarea_input:
            self._tarea_input.cancel()
            self._tarea_input = None
            

    async def _manejar_turno(self, mensaje: dict) -> None:
        """
        Gestiona el turno actual, activando o desactivando la entrada de usuario.

        Args:
            mensaje (dict): Mensaje recibido indicando si es el turno del jugador.

        Returns:
            None
        """
        # TERMINAR COLOCACIÓN
        if self._colocando:
            self._colocando = False

            if self._tarea_input:
                self._tarea_input.cancel()
                self._tarea_input = None

        self._mi_turno = mensaje["tu_turno"]

        if self._mi_turno:
            self._vista.mostrar_mensaje("\nEs tu turno.")

            self._tarea_input = asyncio.create_task(self.fase_turno())

        else:
            self._vista.mostrar_mensaje("\nTurno del rival.")


    async def _manejar_resultado(self, mensaje: dict) -> None:
        """
        Muestra el resultado de un disparo realizado por el jugador.

        Args:
            mensaje (dict): Mensaje recibido con las coordenadas y resultado del disparo.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(f"\nDisparo en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}\n")


    async def _manejar_recibido(self, mensaje: dict) -> None:
        """
        Muestra el resultado de un disparo recibido por el jugador.

        Args:
            mensaje (dict): Mensaje recibido con las coordenadas y resultado del disparo.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(f"\nTe dispararon en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}\n")


    async def _manejar_estado_tableros(self, mensaje: dict) -> None:
        """
        Actualiza la visualización de los tableros del jugador y del rival.

        No realiza actualización si el input está activo.

        Args:
            mensaje (dict): Mensaje con los estados de los tableros.

        Returns:
            None
        """
        if self._input_activo:
            return
        
        self._vista.mostrar_tableros(
            mensaje["propio"],
            mensaje["rival"]
        )


    async def _manejar_fin(self, mensaje: dict) -> None:
        """
        Gestiona el final de la partida mostrando el resultado y cerrando la conexión.

        Args:
            mensaje (dict): Mensaje indicando victoria o derrota.

        Returns:
            None
        """
        victoria = mensaje["victoria"]
        self._vista.mostrar_mensaje_final(victoria, True)
        await self.input_async("\nPULSA INTRO PARA CONTINUAR...")
        self._jugando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.desconectar()
        
        
    async def _manejar_abandono(self, mensaje: dict) -> None:
        """
        Gestiona el final de la partida por abandono de un jugador mostrando el resultado y cerrando la conexión.

        Args:
            mensaje (dict): Mensaje indicando abandono del rival.

        Returns:
            None
        """
        abandono = mensaje["abandono"]
        self._vista.mostrar_mensaje_abandono(abandono)
        self._jugando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.desconectar()


    async def _manejar_error(self, mensaje: dict) -> None:
        """
        Maneja un mensaje de error recibido del servidor.
        Si el jugador estaba en fase de colocación, reinicia la tarea de colocación.

        Args:
            mensaje (dict): Mensaje con información de error.

        Returns:
            None
        """
        self._vista.mostrar_mensaje(f"\nError: {mensaje['mensaje']}")
        
        if self._colocando:
            if not self._tarea_input or self._tarea_input.done():
                self._tarea_input = asyncio.create_task(self.fase_colocacion())
                

    def validar_barco_en_tablero(self, x: int, y: int, tamanyo: int, horizontal: bool) -> bool:
        """
        Comprueba si un barco cabe dentro del tablero.

        Args:
            x (int): Coordenada X inicial.
            y (int): Coordenada Y inicial.
            tamanyo (int): Tamaño del barco.
            horizontal (bool): Orientación del barco.

        Returns:
            bool: True si el barco cabe dentro del tablero.
        """
        if horizontal:
            return x + tamanyo <= 10
        else:
            return y + tamanyo <= 10


    async def salir_partida(self) -> None:
        """
        Abandona la partida actual y cierra la conexión con el servidor.

        Returns:
            None
        """
        self._vista.mostrar_mensaje("Saliendo de la partida...")
        self._jugando = False
        self._colocando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.enviar({"tipo": "salir"})
        await self._cliente.desconectar()
