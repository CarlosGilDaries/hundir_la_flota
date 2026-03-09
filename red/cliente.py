from red.globales import enviar
import asyncio
import json


class ClientePVP:

    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.jugador_num = None
        self.estado = None
        self.mi_turno = False
        self.colocando = False
        self.activo = True
        self.tarea_input = None


    async def conectar(self):
        print("Conectando al servidor...")
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port
        )
        print("Conectado correctamente.")


    async def escuchar_servidor(self):
        try:
            while self.activo:
                data = await self.reader.readline()
                if not data:
                    print("Servidor cerró la conexión.")
                    break

                mensaje = json.loads(data.decode().strip())
                await self.procesar_mensaje(mensaje)

        except Exception as e:
            print("Error escuchando servidor:", e)


    async def procesar_mensaje(self, mensaje):
        tipo = mensaje.get("tipo")

        if tipo == "espera":
            print(mensaje["mensaje"])

        elif tipo == "inicio":
            self.jugador_num = mensaje["jugador"]
            self.estado = mensaje["estado"]

            print(f"Eres jugador {self.jugador_num}")
            print("Fase de colocación iniciada.")
            print("Escribe 'salir' en cualquier momento para abandonar la partida.")

            self.colocando = True

            if not self.tarea_input or self.tarea_input.done():
                self.tarea_input = asyncio.create_task(self.fase_colocacion())


        elif tipo == "confirmacion":
            print(mensaje["mensaje"])

        elif tipo == "error":
            print("Error:", mensaje["mensaje"])
            # Si estoy jugando y es mi turno, volver a pedir disparo
            if self.estado == "jugando" and self.mi_turno:
                if self.tarea_input and not self.tarea_input.done():
                    self.tarea_input.cancel()
                    self.tarea_input = asyncio.create_task(self.fase_turno())

        elif tipo == "turno":
            self.estado = "jugando"
            self.colocando = False
            self.mi_turno = mensaje["tu_turno"]

            # CANCELAR tarea anterior si sigue viva
            if self.tarea_input and not self.tarea_input.done():
                self.tarea_input.cancel()

            if self.mi_turno:
                print("Es tu turno.")
                self.tarea_input = asyncio.create_task(self.fase_turno())
            else:
                print("Turno del rival.")

        elif tipo == "resultado":
            print(f"Disparo en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}")

        elif tipo == "recibido":
            print(f"Te dispararon en ({mensaje['x']},{mensaje['y']}): {mensaje['resultado']}")

        elif tipo == "fin":
            if mensaje.get("victoria"):
                print("Has ganado.")
            else:
                print("Has perdido.")

            if "motivo" in mensaje:
                print("Motivo:", mensaje["motivo"])

            print("Partida finalizada.")
            self.activo = False
            self.writer.close()
            await self.writer.wait_closed()
        
        elif tipo == "lista_barcos":
            print("\nBarcos disponibles:")
            for barco in mensaje["barcos"]:
                print(f"{barco['indice']}. {barco['nombre']} (tamaño {barco['tamanyo']})")

        elif tipo == "estado_tableros":
            self.mostrar_estado(
                mensaje["propio"],
                mensaje["rival"]
            )


    async def input_async(self, mensaje):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, mensaje)


    async def leer_entero(self, mensaje):
        while True:
            valor = await self.input_async(mensaje)

            if valor.lower() == "salir":
                await self.salir_partida()
                return None

            try:
                return int(valor)
            except ValueError:
                print("Debes introducir un número válido.")


    async def fase_colocacion(self):
        try:
            while self.colocando and self.activo:
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

                    print("Debes introducir 'h' o 'v'.")

                await enviar(self.writer, {
                    "tipo": "seleccionar_barco",
                    "indice": indice,
                    "x": x,
                    "y": y,
                    "horizontal": horizontal
                })
                
        except asyncio.CancelledError:
            return


    async def fase_turno(self):
        try:
            await asyncio.sleep(0)  # fuerza cambio de contexto
            if not self.mi_turno or not self.activo:
                return

            x = await self.leer_entero("Coordenada X del disparo: ")
            if x is None:
                return

            y = await self.leer_entero("Coordenada Y del disparo: ")
            if y is None:
                return

            await enviar(self.writer, {
                "tipo": "disparo",
                "x": x,
                "y": y
            })
            
        except asyncio.CancelledError:
            return


    async def salir_partida(self):
        print("Saliendo de la partida...")
        self.activo = False

        await enviar(self.writer, {
            "tipo": "salir"
        })

        self.writer.close()
        await self.writer.wait_closed()
        
    
    def mostrar_estado(self, propio, rival):
        print("\n=== ESTADO DE LA PARTIDA ===\n")

        ancho = len(propio[0])

        encabezado = "   " + " ".join(str(i) for i in range(ancho))
        print("TU TABLERO".ljust(25) + "TABLERO RIVAL")
        print(encabezado.ljust(25) + encabezado)

        for i in range(len(propio)):
            fila_propia = " ".join(propio[i])
            fila_rival = " ".join(rival[i])

            print(
                f"{i:2} {fila_propia}".ljust(25) +
                f"{i:2} {fila_rival}"
            )

        print()


    async def ejecutar(self):
        await self.conectar()
        await self.escuchar_servidor()


if __name__ == "__main__":
    cliente = ClientePVP()
    asyncio.run(cliente.ejecutar())
