class JuegoPVE():
    def __init__(self, tablero_usuario, tablero_barco, disparos_maximos, caracter_vacio, caracter_tocado, caracter_agua):
        """
        Inicializa una nueva partida PVE.

        :param tablero_usuario: Objeto tablero para el usuario.
        :type tablero_usuario: Tablero
        :param tablero_barco: Objeto tablero interno.
        :type tablero_barco: Tablero
        :param disparos_maximos: Número máximo de disparos permitidos.
        :type disparos_maximos: int
        :param caracter_vacio: Carácter para casillas vacías.
        :type caracter_vacio: str
        :param caracter_tocado: Carácter para disparos acertados.
        :type caracter_tocado: str
        :param caracter_agua: Carácter para disparos fallidos.
        :type caracter_agua: str
        """
        self._caracter_vacio = caracter_vacio
        self._caracter_tocado = caracter_tocado
        self._caracter_agua = caracter_agua
        self.tablero_usuario = tablero_usuario
        self.tablero_barco = tablero_barco
        self._disparos_maximos = disparos_maximos
        self._disparos_realizados = 0

        # Inicialización
        for barco in self.tablero_barco.barcos:
            self.tablero_barco.generar_barcos(barco)


    def disparar(self, x, y):
        """
        Realiza un disparo sobre el tablero.

        :param x: Coordenada X.
        :type x: int
        :param y: Coordenada Y.
        :type y: int
        :return: Resultado del disparo.
        :rtype: str
        """
        if self.tablero_barco.disparo_repetido(
            x, y
        ):
            return "REPETIDO"

        self._disparos_realizados += 1

        if self.tablero_barco.comprobar_acierto(x, y):

            barco = self.tablero_barco.obtener_barco_en_posicion(x, y)
            barco.recibir_impacto()

            self.tablero_barco.marcar_disparo(x, y, self._caracter_tocado)
            self.tablero_usuario.marcar_disparo(x, y, self._caracter_tocado)

            if barco.hundido():
                return "TOCADO_Y_HUNDIDO"
            else:
                return "TOCADO"

        else:
            self.tablero_usuario.marcar_disparo(
                x,
                y,
                self._caracter_agua
            )
            return "AGUA"


    def quedan_disparos(self):
        """
        Indica si aún quedan disparos disponibles.

        :return: True si quedan disparos, False en caso contrario.
        :rtype: bool
        """
        return self._disparos_realizados < self._disparos_maximos


    def hay_victoria(self):
        """
        Comprueba si quedan barcos en el tablero interno.

        :return: True si no quedan barcos.
        :rtype: bool
        """
        return self.tablero_barco.todos_hundidos()


    def disparos_restantes(self):
        """
        Calcula las balas restantes

        :return: Balas restantes.
        :rtype: int
        """
        return self._disparos_maximos - self._disparos_realizados