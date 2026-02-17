import random

class Tablero:

    def __init__(self, ancho, alto, barcos, caracter_vacio):
        """
        Inicializa un tablero bidimensional.
        
        :param ancho: número de columnas.
        :type ancho: int
        :param alto: número de filas.
        :type alto: int
        :param barcos: Array de objetos tipo barco.
        :type barcos: list
        :param caracter_vacio: Carácter que representa un espacio vacío.
        :type caracter_vacio: str
        """
        self.ancho = ancho
        self.alto = alto
        self.barcos = barcos

        self._caracteres_barcos = [barco.caracter for barco in barcos]
        self.__casillas = [
            [caracter_vacio for _ in range(ancho)]
            for _ in range(alto)
        ]


    def ver_tablero(self):
        """
        Devuelve el tablero.

        :return: Array que representa el tablero
        :rtype: list
        """
        return self.__casillas


    def quedan_barcos(self):
        """
        Comprueba si quedan barcos sin hundir en el tablero.

        :return: True si quedan barcos, False si no.
        :rtype: bool
        """
        for i in range(self.alto):
            for j in range(self.ancho):
                if self.__casillas[i][j] in self._caracteres_barcos:
                    return True
        return False
    

    def marcar_disparo(self, x, y, caracter):
        """
        Marca un disparo en el tablero.

        :param x: Coordenada inicial en el eje X.
        :type x: int
        :param y: Coordenada inicial en el eje Y.
        :type y: int
        :param caracter: Carácter que representa el resultado del disparo.
        :type caracter: str
        """
        self.__casillas[y][x] = caracter
    

    def generar_barcos(self, barco):
        """
        Genera y coloca barcos aleatoriamente en el tablero.

        El proceso se repite hasta introducir el número de barcos 
        indicado en el atributo cantidad del objeto barco,
        comprobando que no se solapen entre sí.

        :param barco: Barco que se va a colocar en el tablero.
        :type barco: Barco
        """
        contador = 0
        intentos_maximos = 1000
        intentos = 0

        while contador < barco.cantidad and intentos < intentos_maximos:
            intentos += 1
            barco.horizontal = barco.es_horizontal()

            max_x = barco.calcular_maximo(self.ancho)
            max_y = barco.calcular_maximo(self.alto)

            posicion_x = random.randint(0, max_x)
            posicion_y = random.randint(0, max_y)

            if not self._ya_hay_barco_en_posicion(barco, posicion_x, posicion_y):
                self._rellenar_tablero(barco, posicion_x, posicion_y)
                contador = contador + 1
        
        if intentos == intentos_maximos:
            raise RuntimeError("No se pudieron colocar todos los barcos")


    def disparo_repetido(self, x, y, caracter_tocado, caracter_agua):
        """
        Comprueba si el disparo se ha realizado sobre una casilla ya descubierta.

        :param x: Coordenada x que introduce el usuario por teclado
        :type x: int
        :param y: Coordenada y que introduce el usuario por teclado
        :type y: int
        :param caracter_tocado: Carácter que representa un disparo acertado.
        :type caracter_tocado: str
        :param caracter_agua: Carácter que representa un disparo fallido.
        :type caracter_agua: str
        :return: True si el disparo es repetido, False en caso contrario.
        :rtype: bool
        """
        return self.__casillas[y][x] == caracter_tocado or self.__casillas[y][x] == caracter_agua
    

    def comprobar_acierto(self, x, y):
        """
        Determina si el disparo impacta en un barco.

        :param x: Coordenada x que introduce el usuario por teclado
        :type x: int
        :param y: Coordenada y que introduce el usuario por teclado
        :type y: int
        :return: True si el disparo ha sido acertado, False en caso contrario.
        :rtype: bool
        """

        return self.__casillas[y][x] in self._caracteres_barcos


    def _rellenar_tablero(self, barco, x, y):
        """
        Introduce un barco en el tablero según la orientación indicada.

        El barco se coloca a partir de la posición (x, y) y ocupa tantas
        posiciones como indique su tamaño.

        :param barco: Barco que se va a colocar en el tablero.
        :type barco: Barco
        :param x: Coordenada inicial en el eje X.
        :type x: int
        :param y: Coordenada inicial en el eje Y.
        :type y: int
        """
        if barco.horizontal:
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco.caracter
                x = x + 1
        else:
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco.caracter
                y = y + 1


    def _ya_hay_barco_en_posicion(self, barco, x, y):
        """
        Comprueba si ya existe un barco en las posiciones donde se pretende colocar otro.

        :param barco: Barco que se pretende colocar en el tablero.
        :type barco: Barco
        :param x: Coordenada inicial en el eje X.
        :type x: int
        :param y: Coordenada inicial en el eje Y.
        :type y: int
        :return: True si hay un barco en alguna posición, False en caso contrario.
        :rtype: bool
        """
        if barco.horizontal:
            for i in range(barco.tamanyo):
                if self.__casillas[y][x] in self._caracteres_barcos:
                    return True
                x = x + 1
        else:
            for i in range(barco.tamanyo):
                if self.__casillas[y][x] in self._caracteres_barcos:
                    return True
                y = y + 1

        return False
    

    def obtener_barco_en_posicion(self, x, y):
        """
        Obtiene el barco en la posición introducida
        
        :param x: Coordenada x.
        :type x: int
        :param y: Coordenada y.
        :type y: int
        :return: Barco en la posición introducida.
        :rtype: Barco
        """
        caracter_barco = self.__casillas[y][x]
        for barco in self.barcos:
            if barco.caracter == caracter_barco:
                return barco
            

    def obtener_casilla(self, x, y):
        """
        Devuelve el contenido de una casilla concreta.

        :param x: Coordenada X.
        :type x: int
        :param y: Coordenada Y.
        :type y: int
        :return: Contenido de la casilla.
        :rtype: str
        """
        return self.__casillas[y][x]
    

    def obtener_fila(self, y):
        """
        Devuelve una fila del tablero.

        :param y: Índice de fila.
        :type y: int
        :return: Lista con el contenido de la fila.
        :rtype: list
        """
        return list(self.__casillas[y])

