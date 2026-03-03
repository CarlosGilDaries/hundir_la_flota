from modelo.partida_base import PartidaBase
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero

class PartidaPVE(PartidaBase):

    def __init__(self, tablero_usuario: Tablero, tablero_maquina: Tablero, disparos_maximos: int):
        """
        Inicializa una nueva partida PVE.

        :param tablero_usuario: Objeto tablero para el usuario.
        :type tablero_usuario: Tablero
        :param tablero_maquina: Objeto tablero interno.
        :type tablero_maquina: Tablero
        :param disparos_maximos: Número máximo de disparos permitidos.
        :type disparos_maximos: int
        """
        self.tablero_usuario = tablero_usuario
        self.tablero_maquina = tablero_maquina
        self._disparos_maximos = disparos_maximos
        self._disparos_realizados = 0
        
        # Inicialización
        for barco in self.tablero_maquina.barcos:
            self.tablero_maquina.generar_barcos(barco)

        
    def disparar(self, x: int, y: int) -> ResultadoDisparo:
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


    def quedan_disparos(self) -> bool:
        """
        Indica si aún quedan disparos disponibles.

        :return: True si quedan disparos, False en caso contrario.
        :rtype: bool
        """
        return self._disparos_realizados < self._disparos_maximos


    def hay_victoria(self) -> bool:
        """
        Comprueba si quedan barcos en el tablero interno.

        :return: True si no quedan barcos, False si quedan.
        :rtype: bool
        """
        return self.tablero_maquina.todos_hundidos()


    def disparos_restantes(self) -> int:
        """
        Calcula las balas restantes

        :return: Balas restantes.
        :rtype: int
        """
        return self._disparos_maximos - self._disparos_realizados
    
    
    def obtener_dimensiones_tablero(self) -> tuple[int, int]:
        """
        Devuelve las dimensiones del tablero.

        Returns:
            tuple[int, int]: Ancho y alto del tablero.
        """
        return self.tablero_maquina.ancho, self.tablero_maquina.alto
    
    
    def obtener_tablero_rival(self) -> list:
        """
        Devuelve el tablero que debe ver el jugador.
        
        Retunrns:
            list: Array que representa el tablero.
        """
        return self.tablero_usuario.ver_tablero_rival()