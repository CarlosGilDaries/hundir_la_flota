import asyncio
from controlador.controlador import Controlador
from config.protocolo import TipoMensaje, obtener_tipo


class ControladorPVPCliente(Controlador):

    def __init__(self, cliente_socket, vista):
        self._cliente = cliente_socket
        self._vista = vista
        self._estado = None
        self._jugando = True
        self._colocando = False
        self._mi_turno = False
        self._tarea_input = None

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
        self._vista.mostrar_mensaje("Conectando al servidor...")
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
        return await loop.run_in_executor(None, input, prompt)

    async def leer_entero(self, prompt: str):
        while True:
            valor = await self.input_async(prompt)
            if valor.lower() == "salir":
                await self.salir_partida()
                return None
            try:
                return int(valor)
            except ValueError:
                self._vista.mostrar_mensaje("Debes introducir un número válido.")

    # =========================
    # Fase de colocación de barcos
    # =========================
    async def fase_colocacion(self):
        try:
            while self._colocando and self._jugando:
                indice = await self.leer_entero("Selecciona número de barco: ")
                if indice is None:
                    return

                x = await self.leer_entero("Coordenada X: ")
                if x is None:
                    return

                y = await self.leer_entero("Coordenada Y: ")
                if y is None:
                    return

                while True:
                    orientacion = await self.input_async("Horizontal o Vertical (h/v): ")
                    if orientacion.lower() == "salir":
                        await self.salir_partida()
                        return
                    if orientacion.lower() in ("h", "v"):
                        horizontal = orientacion.lower() == "h"
                        break
                    self._vista.mostrar_mensaje("Debes introducir 'h' o 'v'.")

                await self._cliente.enviar({
                    "tipo": "seleccionar_barco",
                    "indice": indice,
                    "x": x,
                    "y": y,
                    "horizontal": horizontal
                })
        except asyncio.CancelledError:
            return

    # =========================
    # Fase de turnos
    # =========================
    async def fase_turno(self):
        try:
            print("ENTRANDO EN FASE TURNO.")
            if not self._mi_turno or not self._jugando:
                return

            x = await self.leer_entero("Coordenada X del disparo: ")
            if x is None:
                return

            y = await self.leer_entero("Coordenada Y del disparo: ")
            if y is None:
                return

            await self._cliente.enviar({
                "tipo": "disparo",
                "x": x,
                "y": y
            })
        except asyncio.CancelledError:
            return

    # =========================
    # Manejo de mensajes
    # =========================
    async def _manejar_inicio(self, mensaje):
        self._vista.mostrar_mensaje(f"Eres el jugador {mensaje['jugador']}")
        self._colocando = True
        self._vista.mostrar_mensaje("Fase de colocación de barcos iniciada. Escribe 'salir' para abandonar.")
        if not self._tarea_input or self._tarea_input.done():
            self._tarea_input = asyncio.create_task(self.fase_colocacion())

    async def _manejar_lista_barcos(self, mensaje):
        barcos = mensaje["barcos"]
        self._vista.mostrar_mensaje("Barcos disponibles:")
        for b in barcos:
            self._vista.mostrar_mensaje(f"{b['indice']} - {b['nombre']} ({b['tamanyo']})")

    async def _manejar_confirmacion(self, mensaje):
        self._vista.mostrar_mensaje(f"Confirmación: {mensaje['mensaje']}")

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
            self._vista.mostrar_mensaje("Es tu turno.")

            self._tarea_input = asyncio.create_task(self.fase_turno())

        else:
            self._vista.mostrar_mensaje("Turno del rival.")


    async def _manejar_resultado(self, mensaje):
        self._vista.mostrar_mensaje(f"Disparo en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}")

    async def _manejar_recibido(self, mensaje):
        self._vista.mostrar_mensaje(f"Te dispararon en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}")

    async def _manejar_estado_tableros(self, mensaje):
        self._vista.mostrar_tablero(mensaje["propio"])
        self._vista.mostrar_tablero(mensaje["rival"])

    async def _manejar_fin(self, mensaje):
        victoria = mensaje["victoria"]
        self._vista.mostrar_mensaje_final(victoria)
        self._jugando = False
        if self._tarea_input and not self._tarea_input.done():
            self._tarea_input.cancel()
        await self._cliente.desconectar()

    async def _manejar_error(self, mensaje):
        self._vista.mostrar_mensaje(f"Error: {mensaje['mensaje']}")

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
