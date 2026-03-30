import random
from modelo.ship import Barco
from modelo.resultado import ResultadoDisparo
import copy

class Tablero:

    def __init__(self, ancho: int, alto: int, barcos: list[Barco], caracter_vacio: str, caracter_tocado: str, caracter_agua: str) -> None:
        """
        Inicializa un tablero bidimensional.

        Args:
            ancho (int): Número de columnas.
            alto (int): Número de filas.
            barcos (list[Barco]): Lista de objetos tipo Barco.
            caracter_vacio (str): Carácter que representa un espacio vacío.
            caracter_tocado (str): Carácter que representa un disparo acertado.
            caracter_agua (str): Carácter que representa un disparo fallado.

        Returns:
            None
        """
        self.ancho = ancho
        self.alto = alto
        self.barcos = barcos
        self._caracter_vacio = caracter_vacio
        self._caracter_tocado = caracter_tocado
        self._caracter_agua = caracter_agua
        self._barcos_colocados = 0
        
        self.__casillas = [
            [None for _ in range(ancho)]
            for _ in range(alto)
        ]
        

    def get_todas_las_casillas(self) -> list[list[Barco|str|None]]:
        """
        Devuelve una copia del atributo privado casillas.

        Returns:
            list[list[Barco|str|None]]: Casillas del tablero.
        """
        return copy.deepcopy(self.__casillas)
    
    
    def get_una_casilla(self, x: int, y: int) -> Barco|str|None:
        """
        Devuelve la copia de una casilla concreta.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            Barco|str|None: Contenido de la casilla.
        """
        return copy.deepcopy(self.__casillas[y][x])


    def ver_tablero(self) -> list[list[str]]:
        """
        Devuelve una vista del tablero con los barcos visibles.

        Returns:
            list[list[str]]: Matriz representando el tablero.
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

    
    def ver_tablero_rival(self) -> list[list[str]]:
        """
        Devuelve el tablero ocultando los barcos, solo mostrando disparos.

        Returns:
            list[list[str]]: Matriz representando el tablero rival.
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
    

    def marcar_disparo(self, x: int, y: int, caracter: str) -> None:
        """
        Marca un disparo en la posición indicada del tablero.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            caracter (str): Carácter que representa el resultado del disparo.

        Returns:
            None
        """
        self.__casillas[y][x] = caracter
    

    def colocar_barco_aleatorio(self, barco: Barco) -> bool:
        """
        Coloca un barco aleatoriamente en el tablero sin solapamientos.

        Args:
            barco (Barco): Barco a colocar.

        Returns:
            bool: True si se colocó correctamente, False si no se pudo colocar.
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
                self._introducir_barco_en_tablero(barco, posicion_x, posicion_y)
                colocado = True
                self._barcos_colocados += 1
            
        return colocado
        
        
    def colocar_barco_manual(self, barco: Barco, x: int, y: int) -> bool:
        """
        Coloca un barco en la posición indicada manualmente.

        Args:
            barco (Barco): Barco a colocar.
            x (int): Coordenada X inicial.
            y (int): Coordenada Y inicial.

        Returns:
            bool: True si se colocó correctamente, False si hay conflicto.
        """
        if not self._puede_colocarse(barco, x, y):
            return False

        self._introducir_barco_en_tablero(barco, x, y)
        self._barcos_colocados += 1
        return True


    def _introducir_barco_en_tablero(self, barco: Barco, x: int, y: int) -> None:
        """
        Introduce un barco en el tablero según su orientación.

        Args:
            barco (Barco): Barco a colocar.
            x (int): Coordenada X inicial.
            y (int): Coordenada Y inicial.

        Returns:
            None
        """
        if barco.get_horizontal():
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco
                x = x + 1
        else:
            for i in range(barco.tamanyo):
                self.__casillas[y][x] = barco
                y = y + 1


    def recibir_disparo(self, x: int, y: int) -> tuple[ResultadoDisparo, str]:
        """
        Procesa un disparo en la posición indicada.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            tuple[ResultadoDisparo, str]: Resultado del disparo y contenido de la celda.
        """
        if not self._coordenadas_validas(x, y):
            return [ResultadoDisparo.INVALIDO, ""]

        celda = self.__casillas[y][x]

        # Ya disparado
        if celda == self._caracter_tocado or celda == self._caracter_agua:
            return [ResultadoDisparo.REPETIDO, celda]

        # Impacto en barco
        if isinstance(celda, Barco):
            barco = celda
            barco.recibir_impacto()
            self.__casillas[y][x] = self._caracter_tocado

            if barco.hundido():
                return [ResultadoDisparo.HUNDIDO, self._caracter_tocado]
            else:
                return [ResultadoDisparo.TOCADO, self._caracter_tocado]

        # Agua
        self.__casillas[y][x] = self._caracter_agua
        return [ResultadoDisparo.AGUA, self._caracter_agua]
        
        
    def todos_hundidos(self) -> bool:
        """
        Comprueba si todos los barcos del tablero han sido hundidos.

        Returns:
            bool: True si todos los barcos están hundidos, False si queda alguno.
        """
        return all(barco.hundido() for barco in self.barcos)


    def _coordenadas_validas(self, x: int, y: int) -> bool:
        """
        Valida si las coordenadas están dentro del tablero y son de tipo entero.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            bool: True si las coordenadas son válidas, False si no.
        """
        return (
            isinstance(x, int) and
            isinstance(y, int) and
            0 <= x < self.ancho and
            0 <= y < self.alto
        )
        
    
    def _puede_colocarse(self, barco: Barco, x: int, y: int) -> bool:
        """
        Comprueba si un barco puede colocarse en la posición indicada.

        Args:
            barco (Barco): Barco a colocar.
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            bool: True si se puede colocar, False si hay conflicto o límite.
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
    
    
    def todos_colocados(self) -> bool:
        """
        Comprueba si todos los barcos han sido colocados.

        Returns:
            bool: True si todos han sido colocados y False si no
        """
        return self._barcos_colocados == len(self.barcos)