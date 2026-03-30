from utils.utils import Util
from utils.excepciones import VolverAlMenu
from modelo.result import ResultadoDisparo
from config.textos import TRADUCCION
from vista.vista import Vista
import os

class VistaConsola(Vista):

    def __init__(self, textos: dict, validador: Util) -> None:
        """
        Inicializa la vista utilizada en consola.

        Args:
            textos (dict): Textos guardados como clave valor en config/textos.
            validador (Util): Validador de la clase Util.
        """
        self._textos = textos
        self._validador = validador


    def pedir_disparo(self, ancho: int, alto: int) -> tuple[int, int]:
        """
        Solicita al usuario las coordenadas del disparo.
        Permite escribir 'salir' para terminar el juego.

        Args:
            ancho (int): Entero que representa el ancho del tablero.
            alto (int): Entero que representa el alto del tablero.

        Returns:
            tuple[int, int]: El valor de X e Y que introduce el usuario.
        """
        x = self.pedir_coordenada("x", ancho - 1)
        y = self.pedir_coordenada("y", alto - 1)
        return x, y


    def pedir_coordenada(self, eje: str, limite: int) -> int:
        """
        Solicita una coordenada válida al usuario.
        'Salir' es el valor establecido para terminar el programa.

        Args:
            eje (str): Eje ('x' o 'y').
            limite (int): Valor máximo permitido.
        Raises:
            VolverAlMenu: Si el usuario selecciona la opción de salir.

        Returns:
            int: Coordenada válida.
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

        Args:
            resultado_enum (ResultadoDisparo): Resultado del disparo
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

        Args:
            tablero (list): Lista de listas con los caracteres del tablero.
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
        
    
    def mostrar_mensaje_final(self, victoria: bool, pvp: bool) -> None:
        """
        Muestra el mensaje final del juego.

        Args:
            victoria (bool): Indica si el jugador ha ganado.
            pvp (bool): Indica si la partida es pve (False) o pvp (True).
        """
        if victoria:
            print("")
            print(self._textos["VICTORIA"])
        else:
            print("")
            print(self._textos["DERROTA"])

        if not pvp:
            input(self._textos["PULSAR_ENTER"])
    
    
    def mostrar_mensaje_abandono(self, abandono: bool) -> None:
        """
        Muestra el mensaje final si el rival ha abandonado.

        Args:
            abandono (bool): Indica si el jugador rival ha abandonado.
        """
        if abandono:
            print("")
            print(self._textos["ABANDONO_PVP"])


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

        Args:
            restantes (int): Número de disparos restantes.
        """
        print("")
        print(self._textos["BALAS_RESTANTES"], restantes)
        
        
    def obtener_texto(self, clave: str) -> str:
        """
        Devuelve el texto correspondiente a la clave.

        Args:
            clave (str): Clave del texto.

        Returns:
            str: Texto asociado.
        """
        return self._textos.get(clave, f"[Texto no encontrado: {clave}]")
    
    
    def mostrar_mensaje(self, mensaje: str) -> None:
        """
        Muestra el mensaje introducido como parámetro.

        Args:
            mensaje (str): Mensaje a mostrar.
        """
        print(mensaje)


    def mostrar_instrucciones(self, instrucciones: str) -> None:
        """
        Muestra las instrucciones del juego.

        Args:
            instrucciones (str): Instrucciones del juego.
        """
        self.borrar_consola()
        print(instrucciones)
        input()
        self.borrar_consola()
        
    
    def borrar_consola(self) -> None:
        """
        Limpia la pantalla de la consola.

        Utiliza secuencias ANSI y el comando del sistema operativo
        correspondiente para garantizar compatibilidad entre sistemas.
        """
        # \033[2J → limpia toda la pantalla
        # \033[H → mueve el cursor a la posición (0,0)
        print("\033[2J\033[H", end="")
        os.system('cls' if os.name == 'nt' else 'clear')


    def mostrar_tableros(self, propio: list[list[str]], rival: list[list[str]]) -> None:
        """
        Muestra simultáneamente el tablero del jugador y el del rival,
        incluyendo coordenadas X e Y como encabezados.

        Args:
            propio (list[list[str]]): Tablero del jugador.
            rival (list[list[str]]): Tablero visible del rival.
        """
        alto = len(propio)
        ancho = len(propio[0])
        
        # Calcular el ancho de cada tablero impreso
        # Formato: "Y " (3 caracteres) + números con espacios
        ancho_tablero_impreso = 3 + (ancho * 2 - 1)
        espaciador = 5
        
        print()
        
        # Mostrar títulos centrados sobre los tableros
        titulo_propio = "Tu tablero"
        titulo_rival = "Tablero rival"
        linea_titulo = titulo_propio.ljust(ancho_tablero_impreso) + (" " * espaciador) + titulo_rival
        print(f"{linea_titulo}\n")
        
        # Mostrar encabezados X
        encabezado = "   " + " ".join(str(i) for i in range(ancho))
        linea_encabezado = encabezado.ljust(ancho_tablero_impreso) + (" " * espaciador) + encabezado
        print(linea_encabezado)
        
        # Mostrar filas con índices Y
        for i in range(alto):
            fila1 = propio[i]
            fila2 = rival[i]
            
            fila_str1 = f"{i:<2} " + " ".join(fila1)
            fila_str2 = f"{i:<2} " + " ".join(fila2)
            
            linea = fila_str1.ljust(ancho_tablero_impreso) + (" " * espaciador) + fila_str2
            print(linea)
