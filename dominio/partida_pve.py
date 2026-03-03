from dominio.partida_base import PartidaBase
from dominio.resultado import ResultadoDisparo

class PartidaPVE(PartidaBase):

    def __init__(self, tablero_usuario, tablero_maquina, disparos_maximos, caracter_vacio, caracter_tocado, caracter_agua):
        """
        Inicializa una nueva partida PVE.

        :param tablero_usuario: Objeto tablero para el usuario.
        :type tablero_usuario: Tablero
        :param tablero_maquina: Objeto tablero interno.
        :type tablero_maquina: Tablero
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
        self.tablero_maquina = tablero_maquina
        self._disparos_maximos = disparos_maximos
        self._disparos_realizados = 0
        
        # Inicialización
        for barco in self.tablero_maquina.barcos:
            self.tablero_maquina.generar_barcos(barco)

        
    def disparar(self, x, y):
        """
        Realiza un disparo sobre los tableros.

        :param x: Coordenada X.
        :type x: int
        :param y: Coordenada Y.
        :type y: int
        :return: Resultado del disparo.
        :rtype: ResultadoDisparo
        """
        [resultado, caracter] = self.tablero_maquina.recibir_disparo(x, y)
        if resultado != ResultadoDisparo.REPETIDO and resultado != ResultadoDisparo.INVALIDO:
            self.tablero_usuario.marcar_disparo(x, y, caracter)
            self._disparos_realizados += 1

        return resultado


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

        :return: True si no quedan barcos, False si quedan.
        :rtype: bool
        """
        return self.tablero_maquina.todos_hundidos()


    def disparos_restantes(self):
        """
        Calcula las balas restantes

        :return: Balas restantes.
        :rtype: int
        """
        return self._disparos_maximos - self._disparos_realizados
    
    
    def obtener_dimensiones_tablero(self):
        return self.tablero_maquina.ancho, self.tablero_maquina.alto