import random
from dominio.barco import Barco

class Tablero:

    def __init__(self, ancho, alto, barcos, caracter_vacio, caracter_tocado, caracter_agua):
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
        :param caracter_tocado: Carácter que representa un disparo acertado.
        :type caracter_tocado: str
        :param caracter_agua: Carácter que representa un disparo fallado.
        :type caracter_agua: str
        """
        self.ancho = ancho
        self.alto = alto
        self.barcos = barcos
        self._caracter_vacio = caracter_vacio
        self._caracter_tocado = caracter_tocado
        self._caracter_agua = caracter_agua
        
        self.__casillas = [
            [None for _ in range(ancho)]
            for _ in range(alto)
        ]


    def ver_tablero(self):
        """
        Devuelve el tablero.

        :return: Array que representa el tablero
        :rtype: list
        """
        vista = []

        for fila in self.__casillas:
            nueva_fila = []
            for celda in fila:
                if celda is None:
                    nueva_fila.append(self._caracter_vacio)
                elif isinstance(celda, Barco):
                    nueva_fila.append(celda.caracter)
                else:
                    nueva_fila.append(celda)

            vista.append(nueva_fila)

        return vista

    
    def ver_tablero_rival(self):
        """
        Devuelve el tablero rival.

        :return: Array que representa el tablero rival con los barcos ocultos.
        :rtype: list
        """
        vista = []
        
        for fila in self.__casillas:
            nueva_fila = []
            for celda in fila:
                if celda == self._caracter_tocado or celda == self._caracter_agua:
                    nueva_fila.append(celda)
                else:
                    nueva_fila.append(self._caracter_vacio)

            vista.append(nueva_fila)

        return vista


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

        El proceso se repite hasta introducir el barco,
        comprobando que no se solapen entre sí.

        :param barco: Barco que se va a colocar en el tablero.
        :type barco: Barco
        """
        intentos_maximos = 1000
        intentos = 0
        colocado = False

        while not colocado and intentos < intentos_maximos:
            intentos += 1
            barco.set_horizontal()

            max_x = barco.calcular_maximo(self.ancho)
            max_y = barco.calcular_maximo(self.alto)

            posicion_x = random.randint(0, max_x)
            posicion_y = random.randint(0, max_y)

            if self._puede_colocarse(barco, posicion_x, posicion_y):
                self._rellenar_tablero(barco, posicion_x, posicion_y)
                colocado = True
            
        if not colocado:
            raise RuntimeError(f"No se pudo colocar el barco {barco.nombre} después de {intentos_maximos} intentos")
        
        
    def colocar_barco_manual(self, barco, x, y):
        """
        Coloca un barco en el tablero según la posición y orientación indicadas por el usuario.

        :param barco: Barco que se va a colocar en el tablero.
        :type barco: Barco
        :param x: Coordenada inicial en el eje X.
        :type x: int
        :param y: Coordenada inicial en el eje Y.
        :type y: int
        :return: True si se coloca el barco y False si había barco en posición o la posición no es válida.
        :rtype: bool
        """
        if not self._puede_colocarse(barco, x, y):
            return False

        self._rellenar_tablero(barco, x, y)
        return True


    def disparo_repetido(self, x, y):
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
        return self.__casillas[y][x] == self._caracter_tocado or self.__casillas[y][x] == self._caracter_agua
    

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
        celda = self.__casillas[y][x]
        return isinstance(celda, Barco) 


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
        if barco.get_horizontal():
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco
                x = x + 1
        else:
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco
                y = y + 1
    

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
        celda = self.__casillas[y][x]
        if isinstance(celda, Barco):
            return celda
        return None
            

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


    def recibir_disparo(self, x, y):
        """
        Realiza un disparo sobre el tablero.

        :param x: Coordenada X.
        :type x: int
        :param y: Coordenada Y.
        :type y: int
        :return: Resultado del disparo.
        :rtype: str
        """
        # Validación centralizada aquí
        if not self._coordenadas_validas(x, y):
            raise ValueError("Coordenadas fuera del tablero")
        
        celda = self.__casillas[y][x]
        if celda == self._caracter_tocado or celda == self._caracter_agua:
            return "REPETIDO"

        if isinstance(celda, Barco):
            barco = celda
            barco.recibir_impacto()
            self.__casillas[y][x] = self._caracter_tocado

            if barco.hundido():
                return "TOCADO_Y_HUNDIDO"
            else:
                return "TOCADO"

        else:
            self.__casillas[y][x] = self._caracter_agua
            return "AGUA"
        
        
    def todos_hundidos(self):
        """
        Comprueba si quedan barcos en el tablero.

        :return: True si no quedan barcos, False si quedan.
        :rtype: bool
        """
        return all(barco.hundido() for barco in self.barcos)


    def _coordenadas_validas(self, x, y):
        return (
            isinstance(x, int) and
            isinstance(y, int) and
            0 <= x < self.ancho and
            0 <= y < self.alto
        )
        
    
    def _puede_colocarse(self, barco, x, y):
        """
        Comprueba si un barco puede colocarse en la posición indicada,
        validando límites y solapamientos en un único recorrido.
        
        :param barco: Barco que se pretende colocar en el tablero.
        :type barco: Barco
        :param x: Coordenada X.
        :type x: int
        :param y: Coordenada Y.
        :type y: int
        :return: True si puede colocarse y False si no.
        :rtype: bool
        """
        # Coordenada inicial válida
        if not self._coordenadas_validas(x, y):
            return False

        for i in range(barco.tamanyo):
            if barco.get_horizontal():
                nx = x + i
                ny = y
            else:
                nx = x
                ny = y + i

            # Validar límites
            if not self._coordenadas_validas(nx, ny):
                return False

            # Validar solapamiento
            if self.__casillas[ny][nx] is not None:
                return False

        return True
