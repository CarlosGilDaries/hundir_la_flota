from servidor.globales import enviar, jugador_partida
from controlador.controlador_pvp import ControladorPVP
from modelo.partida.partida_pvp import EstadoPartida
from modelo.resultado import ResultadoDisparo
from config.mensajes import TRADUCCION
from config.protocolo import TipoMensaje, crear_mensaje, obtener_tipo
from config.constantes import CONSTANTES
from servidor.log import logger
import asyncio


class SesionPVP:

    def __init__(self, writer1: asyncio.StreamWriter, writer2: asyncio.StreamWriter, partida_id: int):
        """
        Inicializa una sesión de juego PVP entre dos clientes conectados.
        
        Configura el controlador de la partida, registra a los jugadores
        en el diccionario global y establece las relaciones entre writers
        y números de jugador.

        Args:
            writer1 (asyncio.StreamWriter): Writer del primer jugador.
            writer2 (asyncio.StreamWriter): Writer del segundo jugador.
        """
        self._writers = {1: writer1, 2: writer2}
        self._jugadores = {writer1: 1, writer2: 2}
        self.partida_id = partida_id

        self._controlador = ControladorPVP(CONSTANTES)

        jugador_partida[writer1] = self
        jugador_partida[writer2] = self
        
        logger.info(f"[PARTIDA {self.partida_id}] Sesión creada entre J1 y J2")


    async def iniciar(self) -> None:
        """
        Inicia la partida notificando a los jugadores y enviando la configuración inicial.
        
        Envía mensajes de inicio a ambos jugadores indicando su número y el estado actual,
        seguido de la lista de barcos pendientes para colocar.
        """
        for jugador, writer in self._writers.items():
            await enviar(writer, crear_mensaje(
                TipoMensaje.INICIO,
                jugador=jugador,
                estado=self._controlador.estado().value
            ))
            await self._enviar_barcos(jugador)
        logger.info(f"[PARTIDA {self.partida_id}] Mensajes de inicio enviados a ambos jugadores")


    async def recibir_mensaje(self, writer: asyncio.StreamWriter, mensaje: dict) -> None:
        """
        Procesa un mensaje recibido de un jugador durante la partida.
        
        Según el estado actual de la partida (colocación o juego),
        redirige el mensaje al método de procesamiento correspondiente.

        Args:
            writer (asyncio.StreamWriter): Writer del jugador que envía el mensaje.
            mensaje (dict): Mensaje parseado recibido del cliente.
        """
        jugador = self._jugadores[writer]
        estado = self._controlador.estado()

        if estado == EstadoPartida.COLOCACION:
            await self._procesar_colocacion(jugador, mensaje)

        elif estado == EstadoPartida.JUGANDO:
            await self._procesar_juego(jugador, mensaje)


    async def _procesar_colocacion(self, jugador: int, mensaje: dict) -> None:
        """
        Procesa un mensaje de colocación de barcos durante la fase de preparación.
        
        Intenta colocar un barco en la posición especificada, notifica el resultado
        y gestiona la transición a la fase de juego cuando ambos jugadores han
        colocado todos sus barcos.

        Args:
            jugador (int): Número del jugador (1 o 2).
            mensaje (dict): Mensaje con los datos de colocación del barco.
        """
        if obtener_tipo(mensaje) != TipoMensaje.SELECCIONAR_BARCO:
            return

        writer = self._writers[jugador]

        try:
            colocado = self._controlador.colocar_barco(
                jugador,
                mensaje["indice"],
                mensaje["x"],
                mensaje["y"],
                mensaje["horizontal"]
            )

            if colocado:
                logger.info(f"[PARTIDA {self.partida_id}] J{jugador} colocó barco índice {mensaje['indice']} en ({mensaje['x']},{mensaje['y']}) {'H' if mensaje['horizontal'] else 'V'}")
                await enviar(writer, crear_mensaje(TipoMensaje.CONFIRMACION, mensaje="Barco colocado correctamente"))
            else:
                logger.warning(f"[PARTIDA {self.partida_id}] J{jugador} intento colocar barco inválido en ({mensaje['x']},{mensaje['y']})")
                await enviar(writer, crear_mensaje(TipoMensaje.ERROR, mensaje="Posición inválida"))
                return

            await self._enviar_estado(jugador)

            pendientes = self._controlador.obtener_barcos_pendientes(jugador)
            if pendientes:
                await self._enviar_barcos(jugador)
            else:
                await enviar(writer, crear_mensaje(TipoMensaje.ESPERA, mensaje="Esperando al otro jugador..."))

            if self._controlador.estado() == EstadoPartida.JUGANDO:
                await self._iniciar_turnos()

        except Exception as e:
            logger.error(f"[PARTIDA {self.partida_id}] Error en colocación de J{jugador}: {e}")
            await enviar(writer, crear_mensaje(TipoMensaje.ERROR, mensaje=str(e)))
            

    async def _procesar_juego(self, jugador: int, mensaje: dict) -> None:
        """
        Procesa un mensaje de disparo durante la fase de juego.
        
        Ejecuta el disparo del jugador, notifica el resultado a ambos jugadores,
        actualiza los estados de los tableros y verifica condiciones de victoria.

        Args:
            jugador (int): Número del jugador que dispara (1 o 2).
            mensaje (dict): Mensaje con las coordenadas del disparo.
        """
        if obtener_tipo(mensaje) != TipoMensaje.DISPARO:
            return

        writer = self._writers[jugador]

        try:
            resultado = self._controlador.disparar(
                jugador,
                mensaje["x"],
                mensaje["y"]
            )

            resultado_str = TRADUCCION[resultado]

            rival = 2 if jugador == 1 else 1
            writer_rival = self._writers[rival]

            # jugador que dispara
            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.RESULTADO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
            ))

            # jugador que recibe
            await enviar(writer_rival,
                crear_mensaje(
                    TipoMensaje.RECIBIDO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
            ))
            
            logger.info(f"[PARTIDA {self.partida_id}] J{jugador} dispara a ({mensaje['x']},{mensaje['y']}) → {resultado_str}")

            await self._enviar_estado(jugador)
            await self._enviar_estado(rival)
            
            if resultado == ResultadoDisparo.INVALIDO:
                return

            if self._controlador.hay_victoria():
                await self._finalizar_partida()
            else:
                await self._actualizar_turnos()

        except Exception as e:
            logger.error(f"[PARTIDA {self.partida_id}] Error en disparo de J{jugador}: {e}")
            await enviar(
                writer, 
                crear_mensaje(
                    TipoMensaje.ERROR,
                    mensaje = str(e)
                )
            )


    async def _iniciar_turnos(self) -> None:
        """
        Inicia la gestión de turnos al comenzar la fase de juego.
        """
        turno = self._controlador.turno_actual()
        logger.info(f"[PARTIDA {self.partida_id}] Turnos iniciados. Turno de J{turno}")
        await self._actualizar_turnos()


    async def _actualizar_turnos(self) -> None:
        """
        Notifica a ambos jugadores sobre el estado del turno actual.
        """
        turno = self._controlador.turno_actual()

        for jugador, writer in self._writers.items():
            await enviar(
                writer,
                crear_mensaje(
                    TipoMensaje.TURNO,
                    tu_turno=jugador == turno
                )
            )
        logger.info(f"[PARTIDA {self.partida_id}] Turno actualizado: J{turno} juega ahora")


    async def _finalizar_partida(self) -> None:
        """
        Finaliza la partida notificando el resultado a ambos jugadores.
        """
        ganador = self._controlador.jugador_ganador()

        for jugador, writer in self._writers.items():
            await enviar(writer, 
                crear_mensaje(
                    TipoMensaje.FIN,
                    victoria = jugador == ganador
                )
            )
        logger.info(f"[PARTIDA {self.partida_id}] Partida finalizada. Ganador: J{ganador}")


    async def _enviar_estado(self, jugador: int) -> None:
        """
        Envía a un jugador el estado visual de ambos tableros.
        
        Args:
            jugador (int): Número del jugador que recibirá el estado (1 o 2).
        """
        writer = self._writers[jugador]

        estado = self._controlador.obtener_estado_tableros(jugador)

        await enviar(writer, 
            crear_mensaje(
                TipoMensaje.ESTADO_TABLEROS,
                propio = estado["propio"],
                rival = estado["rival"]
            )
        )


    async def _enviar_barcos(self, jugador: int) -> None:
        """
        Envía a un jugador la lista de barcos pendientes de colocar.
        
        Args:
            jugador (int): Número del jugador que recibirá la lista (1 o 2).
        """
        writer = self._writers[jugador]

        lista = self._controlador.obtener_barcos_pendientes(jugador)

        await enviar(writer, 
            crear_mensaje(
                TipoMensaje.LISTA_BARCOS,
                barcos = lista
            )
        )
        
        
    async def jugador_desconectado(self, writer: asyncio.StreamWriter):
            """
            Maneja la desconexión de un jugador durante la partida.
            Notifica al rival que ha ganado por abandono y limpia los datos.
            """
            jugador = self._jugadores.get(writer)
            if not jugador:
                return

            rival = 2 if jugador == 1 else 1
            writer_rival = self._writers.get(rival)
            
            logger.warning(f"[PARTIDA {self.partida_id}] J{jugador} se desconectó")

            if writer_rival:
                await enviar(writer_rival, 
                    crear_mensaje(
                        TipoMensaje.FIN,
                        victoria=True,
                        mensaje="Tu rival se ha desconectado. Has ganado la partida."
                    )
                )

            # Limpiar referencias internas
            if writer in self._writers.values():
                del self._writers[jugador]
            if writer in self._jugadores:
                del self._jugadores[writer]
            if writer in jugador_partida:
                del jugador_partida[writer]