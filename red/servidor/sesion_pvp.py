from modelo.partida.partida_pvp import EstadoPartida
from config.textos import TRADUCCION
from config.eventos_log import (
    SESION_CREADA, SESION_INICIADA, SESION_TERMINADA,
    BARCO_COLOCADO, ERROR_COLOCACION, PRIMER_TURNO,
    CAMBIO_TURNO, DISPARO, ERROR_DISPARO, GANADOR, JUGADOR_DESCONECTADO
)
from red.protocolo.mensajes import TipoMensaje, crear_mensaje, obtener_tipo
from red.helpers.enviar import enviar
from config.constantes import CONSTANTES
from servicios.partida_service import PartidaService
from utils.log_decorator import log_async
from typing import Dict, Any
from asyncio import StreamWriter

class SesionPVP:
    """
    Representa una sesión de partida PVP entre dos jugadores conectados.

    Gestiona:
    - flujo de mensajes cliente-servidor
    - fases de la partida
    - turnos
    - sincronización de tableros
    """
    def __init__(self, writer1: StreamWriter, writer2: StreamWriter, id1: int, id2: int, addr1, addr2, partida_id: int, logger, jugador_partida: Dict[StreamWriter, "SesionPVP"]) -> None:
        self._terminada: bool = False
        self.partida_id: int = partida_id
        self._writers: Dict[int, StreamWriter] = {
            1: writer1,
            2: writer2
        }
        self._jugadores: Dict[StreamWriter, int] = {
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

    def _log_evento(self, evento: str, **kwargs) -> None:
        """
        Helper para registrar eventos de manera consistente.
        
        Args:
            evento (str): Nombre del evento (desde config.eventos_log)
            **kwargs: Parámetros adicionales para el log (ej: player=1, x=5, y=3)
        
        Returns:
            None
        """
        params = f"match={self.partida_id}"
        for key, value in kwargs.items():
            params += f" {key}={value}"
        self.logger.info(f"{evento} {params}")


    @log_async
    async def iniciar(self) -> None:
        """
        Inicia la sesión de partida enviando los mensajes iniciales.

        Returns:
            None
        """
        self._log_evento(SESION_INICIADA)

        for jugador, writer in self._writers.items():

            await enviar(writer, crear_mensaje(
                TipoMensaje.INICIO,
                jugador=jugador,
                estado=self._service.estado().value
            ))

            await self._enviar_barcos(jugador)


    async def recibir_mensaje(self, writer: StreamWriter, mensaje: dict) -> None:
        """
        Procesa un mensaje recibido desde un cliente.

        Args:
            writer (StreamWriter): Socket del cliente.
            mensaje (dict): Mensaje recibido.

        Returns:
            None
        """
        jugador = self._jugadores[writer]
        tipo = obtener_tipo(mensaje)
        estado = self._service.estado()
        if estado == EstadoPartida.COLOCACION:
            await self._fase_colocacion(jugador, mensaje, tipo)

        elif estado == EstadoPartida.JUGANDO:
            await self._fase_turno(jugador, mensaje, tipo)


    async def _fase_colocacion(self, jugador: int, mensaje: dict[str, Any], tipo) -> None:    
        """
        Gestiona la fase de colocación de barcos de un jugador.
        Procesa el mensaje recibido del cliente para intentar colocar
        un barco en el tablero del jugador. Si la colocación es válida,
        se actualiza el estado del tablero y se envía confirmación al
        cliente. Si es inválida, se notifica el error.

        Args:
            jugador (int): Identificador del jugador (1 o 2).
            mensaje (dict[str, Any]): Mensaje recibido del cliente con
                los datos de colocación del barco.
                Contiene:
                    - indice (int): índice del barco
                    - x (int): coordenada horizontal
                    - y (int): coordenada vertical
                    - horizontal (bool): orientación del barco
            tipo (TipoMensaje): Tipo de mensaje recibido.

        Returns:
            None
        """
        if tipo != TipoMensaje.SELECCIONAR_BARCO:
            return

        writer = self._writers[jugador]
        player_id = self._player_ids[jugador]

        try:
            colocado = self._service.colocar_barco(
                jugador,
                mensaje["indice"],
                mensaje["x"],
                mensaje["y"],
                mensaje["horizontal"]
            )

            if colocado:
                await enviar(writer,
                    crear_mensaje(
                        TipoMensaje.CONFIRMACION,
                        mensaje="Barco colocado correctamente"
                    )
                )
                
                self._log_evento(
                    BARCO_COLOCADO,
                    player=player_id,
                    boat=mensaje.get("nombre", f"boat_{mensaje['indice']}"),
                    x=mensaje["x"],
                    y=mensaje["y"],
                    horizontal=mensaje["horizontal"]
                )

            else:
                await enviar(writer,
                    crear_mensaje(
                        TipoMensaje.ERROR,
                        mensaje="Posición inválida"
                    )
                )
                
                self._log_evento(
                    ERROR_COLOCACION,
                    player=player_id,
                    boat=mensaje.get("nombre", f"boat_{mensaje['indice']}"),
                    reason="invalid_position"
                )

                return

            await self._enviar_estado(jugador)
            pendientes = self._service.barcos_pendientes(jugador)
            
            if pendientes:
                await self._enviar_barcos(jugador)

            else:
                await enviar(writer,
                    crear_mensaje(
                        TipoMensaje.ESPERA,
                        mensaje="Esperando al rival..."
                    )
                )

            if self._service.estado() == EstadoPartida.JUGANDO:
                
                await self._actualizar_turnos()
                self._log_evento(PRIMER_TURNO, player=self._player_ids[self._service.turno()])

        except Exception as e:
            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.ERROR,
                    mensaje=str(e)
                )
            )
            
            self._log_evento(
                ERROR_COLOCACION,
                player=player_id,
                boat=mensaje.get("nombre", f"boat_{mensaje.get('indice', '?')}"),
                reason=str(e)
            )


    @log_async
    async def _fase_turno(self, jugador: int, mensaje: dict[str, Any], tipo: TipoMensaje) -> None:
        """
        Gestiona la fase de disparo durante el turno de un jugador.
        Recibe las coordenadas del disparo, ejecuta la acción en el
        servicio de juego y envía el resultado tanto al jugador que
        dispara como a su rival.

        Args:
            jugador (int): Identificador del jugador que dispara.
            mensaje (dict[str, Any]): Mensaje recibido con las coordenadas
                del disparo.
                Contiene:
                    - x (int): coordenada horizontal
                    - y (int): coordenada vertical
            tipo (TipoMensaje): Tipo de mensaje recibido.

        Returns:
            None
        """
        if tipo != TipoMensaje.DISPARO:
            return

        writer = self._writers[jugador]
        player_id = self._player_ids[jugador]

        try:
            resultado = self._service.disparar(
                jugador,
                mensaje["x"],
                mensaje["y"]
            )
            resultado_str = TRADUCCION[resultado]
            rival = 2 if jugador == 1 else 1
            writer_rival = self._writers[rival]

            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.RESULTADO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
                )
            )
            await enviar(writer_rival,
                crear_mensaje(
                    TipoMensaje.RECIBIDO,
                    resultado=resultado_str,
                    x=mensaje["x"],
                    y=mensaje["y"]
                )
            )
            
            self._log_evento(
                DISPARO,
                player=player_id,
                x=mensaje["x"],
                y=mensaje["y"],
                result=resultado_str
            )
            
            await self._enviar_estado(jugador)
            await self._enviar_estado(rival)

            if self._service.hay_victoria():
                self._log_evento(GANADOR, player=f"{player_id} addr={self._addrs[jugador]}")
                await self._finalizar_partida()
                self._terminada = True
                self._log_evento(SESION_TERMINADA)

            else:
                await self._actualizar_turnos()

        except Exception as e:
            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.ERROR,
                    mensaje=str(e)
                )
            )
            
            self._log_evento(
                ERROR_DISPARO,
                player=player_id,
                x=mensaje.get("x", "?"),
                y=mensaje.get("y", "?"),
                reason=str(e)
            )


    async def _actualizar_turnos(self) -> None:
        """
        Notifica a ambos jugadores de quién tiene el turno actual.
        Envía un mensaje indicando si el turno pertenece o no a
        cada jugador conectado.

        Returns:
            None
        """
        turno = self._service.turno()
        
        self._log_evento(CAMBIO_TURNO, player=self._player_ids[turno])

        for jugador, writer in self._writers.items():
            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.TURNO,
                    tu_turno=jugador == turno
                )
            )


    async def _finalizar_partida(self) -> None:
        """
        Finaliza la partida y notifica el resultado a ambos jugadores.
        Determina el ganador a través del servicio de juego y envía
        un mensaje indicando victoria o derrota a cada cliente.

        Returns:
            None
        """
        ganador = self._service.ganador()
        
        for jugador, writer in self._writers.items():
            await enviar(writer,
                crear_mensaje(
                    TipoMensaje.FIN,
                    victoria=jugador == ganador
                )
            )


    async def _enviar_estado(self, jugador: int) -> None:
        """
        Envía al jugador el estado actual de los tableros.
        Incluye tanto el tablero propio como la información visible
        del tablero del rival.

        Args:
            jugador (int): Identificador del jugador destinatario.

        Returns:
            None
        """
        writer = self._writers[jugador]
        estado = self._service.estado_tableros(jugador)

        await enviar(writer,
            crear_mensaje(
                TipoMensaje.ESTADO_TABLEROS,
                propio=estado["propio"],
                rival=estado["rival"]
            )
        )


    async def _enviar_barcos(self, jugador: int) -> None:
        """
        Envía al jugador la lista de barcos que todavía debe colocar.
        Este mensaje se utiliza durante la fase inicial de preparación
        de la partida.

        Args:
            jugador (int): Identificador del jugador.

        Returns:
            None
        """
        writer = self._writers[jugador]
        lista = self._service.barcos_pendientes(jugador)

        await enviar(writer,
            crear_mensaje(
                TipoMensaje.LISTA_BARCOS,
                barcos=lista
            )
        )
        
        
    @log_async
    async def jugador_desconectado(self, writer: StreamWriter, es_abandono: bool = False) -> None:
        """
        Maneja la desconexión de un jugador durante una partida.
        Finaliza la partida automáticamente otorgando la victoria
        al jugador restante si fue una desconexión voluntaria.

        Args:
            writer (StreamWriter): Conexión del jugador desconectado.
            es_abandono (bool): True si fue salida voluntaria (escribió 'salir'),
                              False si fue desconexión/cierre del servidor.

        Returns:
            None
        """
        if self._terminada:
            return

        self._terminada = True
        if writer not in self._jugadores:
            return

        jugador = self._jugadores[writer]
        rival = 2 if jugador == 1 else 1
        writer_rival = self._writers.get(rival)
        
        self._log_evento(
            JUGADOR_DESCONECTADO,
            player=self._player_ids[jugador]
        )
        
        # Solo registrar ganador si fue abandono voluntario
        if es_abandono:
            self._log_evento(GANADOR, player=f"{self._player_ids[rival]} addr={self._addrs[rival]}")
        else:
            self._log_evento("SERVER_SHUTDOWN", player=f"{self._player_ids[jugador]} addr={self._addrs[jugador]}")

        # Avisar al rival con el mensaje apropiado
        if writer_rival:
            try:
                if es_abandono:
                    # Jugador abandonó voluntariamente → Victoria por abandono
                    tipo_mensaje = TipoMensaje.ABANDONO
                    datos = {"abandono": True}
                else:
                    # Cierre del servidor → Conexión cerrada
                    tipo_mensaje = TipoMensaje.CIERRE_CONEXION
                    datos = {"razon": "cierre_servidor"}
                
                await enviar(writer_rival,
                    crear_mensaje(tipo_mensaje, **datos)
                )
            except:
                pass

        # limpiar referencias
        if writer in self.jugador_partida:
            del self.jugador_partida[writer]

        if writer_rival and writer_rival in self.jugador_partida:
            del self.jugador_partida[writer_rival]

        # cerrar writers si siguen abiertos
        for w in self._writers.values():
            try:
                w.close()
                await w.wait_closed()
            except:
                pass

        self._log_evento(SESION_TERMINADA)
