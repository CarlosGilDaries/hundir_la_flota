import asyncio
from red.globales import enviar, jugador_partida
from dominio.tablero import Tablero
from dominio.barco import Barco
from config.constantes import CARACTER_AGUA, CARACTER_VACIO, CARACTER_TOCADO, DIFICULTAD

class Partida:

    ESPERANDO_COLOCACION = "esperando_colocacion"
    JUGANDO = "jugando"
    FINALIZADA = "finalizada"

    def __init__(self, jugador1, jugador2):
        self.jugador1 = jugador1
        self.jugador2 = jugador2
        # self.barcos_config = [
        #     ("PORTAAVIONES", 5),
        #     ("ACORAZADO", 4),
        #     ("DESTRUCTOR", 3),
        #     ("SUBMARINO", 3),
        #     ("LANCHA", 2),
        # ]
        
        barcos = [
            Barco(longitud, cantidad, identificador)
            for longitud, cantidad, identificador in DIFICULTAD["PVP"]["barcos"]
        ]
        
        self.tableros = {
            self.jugador1: Tablero(DIFICULTAD["PVP"]["ancho"], DIFICULTAD["PVP"]["alto"], barcos, CARACTER_VACIO),
            self.jugador2: Tablero(DIFICULTAD["PVP"]["ancho"], DIFICULTAD["PVP"]["alto"], barcos, CARACTER_VACIO)
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
            await self.enviar(writer, {
                "tipo": "error",
                "mensaje": "Barco no disponible"
            })
            return

        tablero = self.tableros[writer]

        try:
            barco = Barco(tamanyo, 1, caracter, horizontal)
            barco_colocado = tablero.colocar_barco_manual(barco, x, y)
            if barco_colocado:
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

        await self.enviar(writer, {
            "tipo": "confirmacion",
            "mensaje": f"{barco_nombre} colocado correctamente"
        })

        if not pendientes:
            self.jugadores_listos.add(writer)

            await self.enviar(writer, {
                "tipo": "espera",
                "mensaje": "Esperando al otro jugador..."
            })

            if len(self.jugadores_listos) == 2:
                self.estado = self.JUGANDO
                await self.comenzar_juego()

                

    async def procesar_juego(self, writer, mensaje):
        await enviar(writer, {
            "tipo": "info",
            "mensaje": "Fase de juego aún no implementada"
        })


    async def comenzar_juego(self):
        await self.enviar_a_ambos({
            "tipo": "comenzar",
            "estado": self.estado
        })

        print("La partida ahora está en estado JUGANDO")


    async def enviar_a_ambos(self, data):
        await enviar(self.jugador1, data)
        await enviar(self.jugador2, data)
