from utils.utils import Util
from utils.excepciones import VolverAlMenu
from modelo.resultado import ResultadoDisparo
from config.textos import TRADUCCION
from vista.vista import Vista
import os

class VistaConsola(Vista):

    def __init__(self, textos: dict, validador: Util) -> None:
        """
        :param textos: Diccionario de textos del juego.
        :type textos: dict
        :param validador: Objeto validador.
        :type validador: Util
        """
        self._textos = textos
        self._validador = validador


    def pedir_disparo(self, ancho: int, alto: int) -> tuple[int, int]:
        """
        Solicita al usuario las coordenadas del disparo.
        Permite escribir 'salir' para terminar el juego.

        :param ancho: Ancho del tablero.
        :type ancho: int
        :param alto: Alto del tablero.
        :type alto: int
        :return: El valor para X e Y introducido por el usuario.
        :rtype: tuple[int, int]
        """
        x = self.pedir_coordenada("x", ancho - 1)
        y = self.pedir_coordenada("y", alto - 1)
        return x, y


    def pedir_coordenada(self, eje: str, limite: int) -> int:
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
            valor = input(self._textos[f"POSICION_{eje.upper()}"])
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


    def opcion_volver_menu(self) -> None:
        """
        Muestra el texto con la opción para volver al menú.
        """
        print("")
        print(self._textos["FIN_JUEGO"])
        print("")


    def mostrar_resultado(self, resultado_enum: ResultadoDisparo) -> None:
        """
        Muestra el resultado del disparo.

        :param resultado_enum: Resultado del disparo.
        :type resultado_enum: ResultadoDisparo
        """
        print("")
        resultado = self.adaptar_resultado_a_string(resultado_enum)
        print(self._textos[f"{resultado}"])
        print("")


    def mostrar_tablero(self, tablero: list) -> None:
        """
        Muestra por consola el tablero de juego con índices de filas y columnas.

        El tablero se imprime en formato matricial:
        - La primera línea muestra los índices de las columnas.
        - Cada fila se muestra precedida por su índice correspondiente.

        :param tablero: Lista de listas con los caracteres del tablero.
        :type tablero: list
        """

        alto = len(tablero) 
        ancho = len(tablero[0])

        # Mostrar encabezado con coordenadas X
        encabezado = "   " + " ".join(str(i) for i in range(ancho))
        print(encabezado)

        # Mostrar cada fila con su coordenada Y
        for i in range(alto):
            fila = tablero[i]
            fila_str = f"{i:<2} " + " ".join(fila)
            print(fila_str)
        
    
    def mostrar_mensaje_final(self, victoria: bool) -> None:
        """
        Muestra el mensaje final del juego.

        :param victoria: Indica si el jugador ha ganado.
        :type victoria: bool
        """
        if victoria:
            print("")
            print(self._textos["VICTORIA"])
        else:
            print("")
            print(self._textos["DERROTA"])

        input(self._textos["PULSAR_ENTER"])


    def fin_programa(self) -> None:
        """
        Muestra el texto de fin de programa.
        """
        print("")
        print(self._textos["FIN_DE_PROGRAMA"])
        print("")


    def mostrar_balas(self, restantes: int) -> None:
        """
        Muestra las balas restantes.

        :param restantes: Número de disparos restantes.
        :type restantes: int
        """
        print("")
        print(self._textos["BALAS_RESTANTES"], restantes)
        
        
    def obtener_texto(self, clave: str) -> str:
        """
        Devuelve el texto correspondiente a la clave.

        :param clave: Clave del texto.
        :type clave: str
        :return: Texto asociado.
        :rtype: str
        """
        return self._textos.get(clave, f"[Texto no encontrado: {clave}]")
    
    
    def mostrar_mensaje(self, mensaje: str) -> None:
        """
        Muestra el mensaje introducido como parámetro.

        :param mensaje: Mensaje a mostrar.
        :type mensaje: str
        """
        print(mensaje)


    def mostrar_instrucciones(self, instrucciones: str) -> None:
        """
        Muestra las instrucciones del juego.

        :param instrucciones: Instrucciones del juego.
        :type instrucciones: str
        """
        self.borrar_consola()
        print(instrucciones)
        input()
        self.borrar_consola()
        
    
    def borrar_consola(self) -> None:
        """
        Borra lo escrito en la consola.
        """
        # \033[2J → limpia toda la pantalla
        # \033[H → mueve el cursor a la posición (0,0)
        print("\033[2J\033[H", end="")
        os.system('cls' if os.name == 'nt' else 'clear')


    def mostrar_tableros(self, propio, rival):
        ancho = 25
        print()
        print("Tu tablero".ljust(ancho) + "Tablero rival")

        for fila1, fila2 in zip(propio, rival):
            linea1 = " ".join(fila1)
            linea2 = " ".join(fila2)
            print(linea1.ljust(ancho) + linea2)
