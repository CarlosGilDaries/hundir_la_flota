import asyncio
import json
from globales import jugador_partida, enviar

# jugador_partida = {}

class Partida:

    ESPERANDO_COLOCACION = "esperando_colocacion"
    JUGANDO = "jugando"
    FINALIZADA = "finalizada"

    def __init__(self, jugador1, jugador2):
        self.jugador1 = jugador1
        self.jugador2 = jugador2

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
        if mensaje.get("tipo") == "listo":

            self.jugadores_listos.add(writer)

            await enviar(writer, {
                "tipo": "confirmacion",
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
