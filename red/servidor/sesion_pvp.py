from modelo.partida.partida_pvp import EstadoPartida
from modelo.resultado import ResultadoDisparo
from config.textos import TRADUCCION
from red.protocolo.mensajes import TipoMensaje, crear_mensaje, obtener_tipo
from config.constantes import CONSTANTES
from servicios.partida_service import PartidaService
import asyncio
import json


class SesionPVP:

    def __init__(self, writer1, writer2, id1, id2, addr1, addr2, partida_id, logger, jugador_partida):

        self.partida_id = partida_id

        self._writers = {
            1: writer1,
            2: writer2
        }

        self._jugadores = {
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

        self._service = PartidaService(
            CONSTANTES["DIFICULTAD"]["PVP"],
            CONSTANTES["CARACTERES"]
        )

        self.jugador_partida = jugador_partida
        jugador_partida[writer1] = self
        jugador_partida[writer2] = self
        self.logger = logger

        self.logger.info(
            f"MATCH_SESSION_CREATED match={self.partida_id} "
            f"player1={id1}@{addr1} player2={id2}@{addr2}"
        )


    async def iniciar(self):

        self.logger.info(f"MATCH_START match={self.partida_id}")

        for jugador, writer in self._writers.items():

            await self._enviar(writer, crear_mensaje(
                TipoMensaje.INICIO,
                jugador=jugador,
                estado=self._service.estado().value
            ))

            await self._enviar_barcos(jugador)


    async def recibir_mensaje(self, writer, mensaje):

        jugador = self._jugadores[writer]

        tipo = obtener_tipo(mensaje)

        estado = self._service.estado()

        if estado == EstadoPartida.COLOCACION:
            await self._fase_colocacion(jugador, mensaje, tipo)

        elif estado == EstadoPartida.JUGANDO:
            await self._fase_turno(jugador, mensaje, tipo)


    async def _fase_colocacion(self, jugador, mensaje, tipo):

        if tipo != TipoMensaje.SELECCIONAR_BARCO:
            return

        writer = self._writers[jugador]

        try:

            colocado = self._service.colocar_barco(
                jugador,
                mensaje["indice"],
                mensaje["x"],
                mensaje["y"],
                mensaje["horizontal"]
            )

            if colocado:

                await self._enviar(writer,
                    crear_mensaje(
                        TipoMensaje.CONFIRMACION,
                        mensaje="Barco colocado correctamente"
                    )
                )

            else:

                await self._enviar(writer,
                    crear_mensaje(
                        TipoMensaje.ERROR,
                        mensaje="Posición inválida"
                    )
                )

                return

            await self._enviar_estado(jugador)

            pendientes = self._service.barcos_pendientes(jugador)

            if pendientes:

                await self._enviar_barcos(jugador)

            else:

                await self._enviar(writer,
                    crear_mensaje(
                        TipoMensaje.ESPERA,
                        mensaje="Esperando al rival..."
                    )
                )

            if self._service.estado() == EstadoPartida.JUGANDO:

                await self._actualizar_turnos()

        except Exception as e:

            await self._enviar(writer,
                crear_mensaje(
                    TipoMensaje.ERROR,
                    mensaje=str(e)
                )
            )


    async def _fase_turno(self, jugador, mensaje, tipo):

        if tipo != TipoMensaje.DISPARO:
            return

        writer = self._writers[jugador]

        try:

            resultado = self._service.disparar(
                jugador,
                mensaje["x"],
                mensaje["y"]
            )

            resultado_str = TRADUCCION[resultado]

            rival = 2 if jugador == 1 else 1
            writer_rival = self._writers[rival]

            await self._enviar(writer,
                crear_mensaje(
                    TipoMensaje.RESULTADO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
                )
            )

            await self._enviar(writer_rival,
                crear_mensaje(
                    TipoMensaje.RECIBIDO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
                )
            )

            await self._enviar_estado(jugador)
            await self._enviar_estado(rival)

            if self._service.hay_victoria():

                await self._finalizar_partida()

            else:

                await self._actualizar_turnos()

        except Exception as e:

            await self._enviar(writer,
                crear_mensaje(
                    TipoMensaje.ERROR,
                    mensaje=str(e)
                )
            )


    async def _actualizar_turnos(self):

        turno = self._service.turno()

        for jugador, writer in self._writers.items():

            await self._enviar(writer,
                crear_mensaje(
                    TipoMensaje.TURNO,
                    tu_turno=jugador == turno
                )
            )


    async def _finalizar_partida(self):

        ganador = self._service.ganador()

        for jugador, writer in self._writers.items():

            await self._enviar(writer,
                crear_mensaje(
                    TipoMensaje.FIN,
                    victoria=jugador == ganador
                )
            )


    async def _enviar_estado(self, jugador):

        writer = self._writers[jugador]

        estado = self._service.estado_tableros(jugador)

        await self._enviar(writer,
            crear_mensaje(
                TipoMensaje.ESTADO_TABLEROS,
                propio=estado["propio"],
                rival=estado["rival"]
            )
        )


    async def _enviar_barcos(self, jugador):

        writer = self._writers[jugador]

        lista = self._service.barcos_pendientes(jugador)

        await self._enviar(writer,
            crear_mensaje(
                TipoMensaje.LISTA_BARCOS,
                barcos=lista
            )
        )

    async def _enviar(self, writer: asyncio.StreamWriter, data: dict) -> None:
        """
        Envía un mensaje JSON a un cliente a través de su writer.
        
        Serializa los datos a formato JSON, añade un salto de línea como
        delimitador de mensaje, codifica a bytes y escribe en el stream.
        El salto de línea añadido sirve como marcador de fin de mensaje,
        permitiendo al cliente leer línea por línea con reader.readline().
        Finaliza asegurando que los datos se envían completamente (drain).

        Args:
            writer (asyncio.StreamWriter): Writer del cliente destinatario.
            data (dict): Datos a enviar (JSON).
        """
        mensaje = json.dumps(data) + "\n"
        # print("SERVIDOR -> CLIENTE:", mensaje.strip())
        writer.write(mensaje.encode())
        await writer.drain()