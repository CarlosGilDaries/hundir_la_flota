import asyncio
from red.globales import enviar, jugador_partida
from dominio.tablero import Tablero
from dominio.barco import Barco
from config.constantes import CARACTER_AGUA, CARACTER_VACIO, CARACTER_TOCADO, DIFICULTAD

class Partida:

    ESPERANDO_COLOCACION = "esperando_colocacion"
    JUGANDO = "jugando"
    FINALIZADA = "finalizada"
    ANCHO_TABLEROS = DIFICULTAD["PVP"]["ancho"]
    ALTO_TABLEROS = DIFICULTAD["PVP"]["alto"]

    def __init__(self, jugador1, jugador2):
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        self.turno = self.jugador1
        
        barcos = [
            Barco(longitud, cantidad, identificador)
            for longitud, cantidad, identificador in DIFICULTAD["PVP"]["barcos"]
        ]
        
        self.tableros = {
            self.jugador1: Tablero(self.ANCHO_TABLEROS, self.ALTO_TABLEROS, barcos, CARACTER_VACIO, CARACTER_TOCADO, CARACTER_AGUA),
            self.jugador2: Tablero(self.ANCHO_TABLEROS, self.ALTO_TABLEROS, barcos, CARACTER_VACIO, CARACTER_TOCADO, CARACTER_AGUA)
        }

        self.barcos_pendientes = {
            self.jugador1: list(barcos),
            self.jugador2: list(barcos)
        }

        self.estado = self.ESPERANDO_COLOCACION

        self.jugadores_listos = set()

        print("Nueva partida creada")

        jugador_partida[jugador1] = self
        jugador_partida[jugador2] = self

        asyncio.create_task(self.iniciar())
        
        
    async def iniciar(self):
        await enviar(self.jugador1, {
            "tipo": "inicio",
            "jugador": 1,
            "estado": self.estado
        })

        await enviar(self.jugador2, {
            "tipo": "inicio",
            "jugador": 2,
            "estado": self.estado
        })


    async def recibir_mensaje(self, writer, mensaje):
        if self.estado == self.ESPERANDO_COLOCACION:
            await self.procesar_colocacion(writer, mensaje)

        elif self.estado == self.JUGANDO:
            await self.procesar_juego(writer, mensaje)


    async def procesar_colocacion(self, writer, mensaje):

        if mensaje.get("tipo") != "colocar":
            return

        caracter = mensaje.get("caracter")
        x = mensaje.get("x")
        y = mensaje.get("y")
        horizontal = mensaje.get("horizontal")
        tamanyo = mensaje.get("tamanyo")
        barco_nombre = mensaje.get("barco_nombre")

        pendientes = self.barcos_pendientes[writer]

        barco_info = next((b for b in pendientes if b.caracter == caracter), None)

        if not barco_info:
            await enviar(writer, {
                "tipo": "error",
                "mensaje": "Barco no disponible"
            })
            return

        tablero = self.tableros[writer]

        try:
            barco = Barco(tamanyo, 1, caracter, horizontal)
            barco_colocado = tablero.colocar_barco_manual(barco, x, y)
            if not barco_colocado:
                await enviar(writer, {
                "tipo": "error",
                "mensaje": "Ya hay un barco en esa posición"
            })
                return

        except Exception as e:
            await enviar(writer, {
                "tipo": "error",
                "mensaje": str(e)
            })
            return

        pendientes.remove(barco_info)

        await enviar(writer, {
            "tipo": "confirmacion",
            "mensaje": f"{barco_nombre} colocado correctamente"
        })

        if not pendientes:
            self.jugadores_listos.add(writer)

            await enviar(writer, {
                "tipo": "espera",
                "mensaje": "Esperando al otro jugador..."
            })

            if len(self.jugadores_listos) == 2:
                self.estado = self.JUGANDO
                await self.comenzar_juego()

                

    async def procesar_juego(self, writer, mensaje):
        if mensaje.get("tipo") != "disparo":
            return

        if writer != self.turno:
            await enviar(writer, {
                "tipo": "error",
                "mensaje": "No es tu turno"
            })
            return

        x = mensaje.get("x")
        y = mensaje.get("y")

        defensor = self.oponente(writer)
        tablero_defensor = self.tableros[defensor]

        try:
            resultado = tablero_defensor.recibir_disparo(x, y)

            await enviar(writer, {
                "tipo": "resultado",
                "resultado": resultado,
                "x": x,
                "y": y
            })

            await enviar(defensor, {
                "tipo": "recibido",
                "resultado": resultado,
                "x": x,
                "y": y
            })

            if tablero_defensor.todos_hundidos():
                self.estado = self.FINALIZADA

                await enviar(writer, {
                    "tipo": "fin",
                    "victoria": True
                })

                await enviar(defensor, {
                    "tipo": "fin",
                    "victoria": False
                })

                print("Partida finalizada")
                return

            else:
                self.turno = defensor
                await enviar(self.turno, {
                    "tipo": "turno",
                    "tu_turno": True
                })

                await enviar(self.oponente(self.turno), {
                    "tipo": "turno",
                    "tu_turno": False
                })

        except Exception as e:
            await enviar(writer, {
                "tipo": "error",
                "mensaje": str(e)
            })
            return


    async def comenzar_juego(self):
        self.turno = self.jugador1

        await enviar(self.jugador1, {
            "tipo": "turno",
            "tu_turno": True
        })

        await enviar(self.jugador2, {
            "tipo": "turno",
            "tu_turno": False
        })

        print("Turno inicial asignado")


    async def enviar_a_ambos(self, data):
        await enviar(self.jugador1, data)
        await enviar(self.jugador2, data)
        
        
    def oponente(self, writer):
        return self.jugador2 if writer == self.jugador1 else self.jugador1

