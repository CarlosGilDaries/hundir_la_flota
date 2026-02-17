"""
Interfaz de consola del juego Hundir la Flota.
"""
from utils.excepciones import VolverAlMenu
import os

class InterfazConsola:

    def __init__(self, textos, validador):
        """
        :param textos: Diccionario de textos del juego.
        :type textos: dict
        :param validador: Objeto validador.
        :type validador: Util
        """
        self._textos = textos
        self._validador = validador
    

    def pedir_disparo(self, ancho, alto):
        """
        Solicita al usuario las coordenadas del disparo.
        Permite escribir 'salir' para terminar el juego.

        :param ancho: Ancho del tablero.
        :type ancho: int
        :param alto: Alto del tablero.
        :type alto: int
        :return: El valor para X e Y introducido por el usuario
        :rtype: tuple[int, int]
        """
        x = self._pedir_coordenada("x", ancho - 1)
        y = self._pedir_coordenada("y", alto - 1)
        return x, y


    def _pedir_coordenada(self, eje, limite):
        """
        Solicita una coordenada válida al usuario.
        'Salir' es el valor establecido para terminar el programa.

        :param eje: Eje ('x' o 'y').
        :type eje: str
        :param limite: Valor máximo permitido.
        :type limite: int
        :return: Coordenada válida.
        :rtype: int
        :raises VolverAlMenu: Si el usuario selecciona la opción de salir.
        """
        valido = False
        while not valido:
            valor = input(self._textos[f"TEXTO_POSICION_{eje.upper()}"])
            print("")

            if valor.lower() == "salir":
                raise VolverAlMenu()

            if not self._validador.es_numero_entero(valor):
                print(self._textos["ERROR_NUMERO_ENTERO"])
                print("")
                continue

            if not self._validador.opcion_valida(valor, limite):
                print(self._textos["ERROR_LIMITE_TABLERO"])
                print("")
                continue
            
            valido = True
            return int(valor)


    def opcion_volver_menu(self):
        """
        Muestra el texto con la opción para volver al menú.
        """
        print("")
        print(self._textos["TEXTO_FIN_JUEGO"])
        print("")


    def fin_programa(self):
        """
        Muestra el texto de fin de programa.
        """
        print("")
        print(self._textos["FIN_DE_PROGRAMA"])
        print("")


    def mostrar_resultado(self, resultado):
        """
        Muestra el resultado del disparo.

        :param resultado: Resultado del disparo.
        :type resultado: str
        """
        print("")
        print(self._textos[f"TEXTO_{resultado}"])
        print("")


    def mostrar_tablero(self, tablero):
        """
        Muestra por consola el tablero de juego con índices de filas y columnas.

        El tablero se imprime en formato matricial:
        - La primera línea muestra los índices de las columnas.
        - Cada fila se muestra precedida por su índice correspondiente.

        :param tablero: Objeto tablero.
        :type tablero: Tablero
        """

        encabezado = "   " + " ".join(str(i) for i in range(tablero.ancho))
        print(encabezado)

        for i in range(tablero.alto):
            fila = tablero.obtener_fila(i)
            fila_str = f"{i:<2} " + " ".join(fila)
            print(fila_str)


    def mostrar_balas(self, restantes):
        """
        Muestra las balas restantes.

        :param restantes: Número de disparos restantes.
        :type restantes: int
        """
        print(self._textos["TEXTO_BALAS_RESTANTES"], restantes)


    def mostrar_mensaje_final(self, victoria):
        """
        Muestra el mensaje final del juego.

        :param victoria: Indica si el jugador ha ganado.
        :type victoria: bool
        """
        if victoria:
            print("")
            print(self._textos["TEXTO_VICTORIA"])
        else:
            print("")
            print(self._textos["TEXTO_DERROTA"])

        input(self._textos["PULSAR_ENTER"])


    def borrar_consola(self):
        """
        Borra lo escrito en la consola.
        """
        # \033[2J → limpia toda la pantalla
        # \033[H → mueve el cursor a la posición (0,0)
        print("\033[2J\033[H", end="")
        os.system('cls' if os.name == 'nt' else 'clear')


    def mostrar_instrucciones(self, instrucciones):
        """
        Muestra las instrucciones del juego.

        :param instrucciones: Instrucciones del juego.
        :type instrucciones: str
        """
        self.borrar_consola()
        print(instrucciones)
        input()
        self.borrar_consola()


    def obtener_texto(self, clave):
        """
        Devuelve el texto correspondiente a la clave.

        :param clave: Clave del texto.
        :type clave: str
        :return: Texto asociado.
        :rtype: str
        """
        return self._textos.get(clave, f"[Texto no encontrado: {clave}]")
