import asyncio
from controlador.controlador import Controlador
from red.protocolo.mensajes import TipoMensaje, obtener_tipo, crear_mensaje

class ControladorPVPCliente(Controlador):

    def __init__(self, cliente_socket, vista):
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
            TipoMensaje.ERROR: self._manejar_error
        }


    # =========================
    # Conexión y loop principal
    # =========================
    async def iniciar(self):
        self._vista.mostrar_mensaje("\nConectando al servidor...\n")
        await self._cliente.conectar()
        await self._escuchar_servidor()

    async def _escuchar_servidor(self):
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

    async def _dispatch(self, tipo, mensaje):
        handler = self._handlers.get(tipo)
        if handler:
            await handler(mensaje)
        else:
            self._vista.mostrar_mensaje(f"Mensaje desconocido: {tipo}")

    # =========================
    # Input asíncrono
    # =========================
    async def input_async(self, prompt: str):
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


    async def leer_entero(self, prompt, minimo = None, maximo = None):
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


    # =========================
    # Fase de colocación de barcos
    # =========================
    async def fase_colocacion(self):
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

    # =========================
    # Fase de turnos
    # =========================
    async def fase_turno(self):
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

    # =========================
    # Manejo de mensajes
    # =========================
    async def _manejar_inicio(self, mensaje):
        self._vista.mostrar_mensaje(f"\nEres el jugador {mensaje['jugador']}\n")
        self._colocando = True
        self._vista.mostrar_mensaje("Fase de colocación de barcos iniciada.")
        # if not self._tarea_input or self._tarea_input.done():
        #     self._tarea_input = asyncio.create_task(self.fase_colocacion())

    async def _manejar_lista_barcos(self, mensaje):
        barcos = mensaje["barcos"]
        self._barcos_disponibles = barcos
        self._vista.mostrar_mensaje("\nEscribe 'salir' para abandonar.")
        self._vista.mostrar_mensaje("\nBarcos disponibles:\n")
        for b in barcos:
            self._vista.mostrar_mensaje(f"{b['indice']} - {b['nombre']} ({b['tamanyo']})")
            
        if self._colocando and (not self._tarea_input or self._tarea_input.done()):
            self._tarea_input = asyncio.create_task(self.fase_colocacion())

    async def _manejar_confirmacion(self, mensaje):
        self._vista.mostrar_mensaje(f"\nConfirmación: {mensaje['mensaje']}")

    async def _manejar_espera(self, mensaje):
        self._vista.mostrar_mensaje(mensaje["mensaje"])

        self._colocando = False

        if self._tarea_input:
            self._tarea_input.cancel()
            self._tarea_input = None
            

    async def _manejar_turno(self, mensaje):
        # TERMINAR COLOCACIÓN
        if self._colocando:
            self._colocando = False

            if self._tarea_input:
                self._tarea_input.cancel()
                self._tarea_input = None   # ← CLAVE

        self._mi_turno = mensaje["tu_turno"]

        if self._mi_turno:
            self._vista.mostrar_mensaje("\nEs tu turno.")

            self._tarea_input = asyncio.create_task(self.fase_turno())

        else:
            self._vista.mostrar_mensaje("\nTurno del rival.")


    async def _manejar_resultado(self, mensaje):
        self._vista.mostrar_mensaje(f"\nDisparo en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}\n")

    async def _manejar_recibido(self, mensaje):
        self._vista.mostrar_mensaje(f"\nTe dispararon en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}\n")

    async def _manejar_estado_tableros(self, mensaje):
        if self._input_activo:
            return
        
        self._vista.mostrar_tableros(
            mensaje["propio"],
            mensaje["rival"]
        )

    async def _manejar_fin(self, mensaje):
        victoria = mensaje["victoria"]
        self._vista.mostrar_mensaje_final(victoria)
        self._jugando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.desconectar()

    async def _manejar_error(self, mensaje):
        self._vista.mostrar_mensaje(f"\nError: {mensaje['mensaje']}")
        
        if self._colocando:
            if not self._tarea_input or self._tarea_input.done():
                self._tarea_input = asyncio.create_task(self.fase_colocacion())
                

    def validar_barco_en_tablero(self, x, y, tamanyo, horizontal):
        if horizontal:
            return x + tamanyo <= 10
        else:
            return y + tamanyo <= 10


    # =========================
    # Salir
    # =========================
    async def salir_partida(self):
        self._vista.mostrar_mensaje("Saliendo de la partida...")
        self._jugando = False
        self._colocando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.enviar({"tipo": "salir"})
        await self._cliente.desconectar()
