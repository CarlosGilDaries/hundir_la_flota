from modelo.partida.partida import Partida
from modelo.resultado import ResultadoDisparo
from modelo.tablero import Tablero
from modelo.barco import Barco

class PartidaPVE(Partida):

    def __init__(self, tablero_maquina: Tablero, disparos_maximos: int) -> None:
        """
        Inicializa una nueva partida PVE.

        :param tablero_maquina: Objeto tablero interno.
        :type tablero_maquina: Tablero
        :param disparos_maximos: Número máximo de disparos permitidos.
        :type disparos_maximos: int
        """
        self.tablero_maquina = tablero_maquina
        self._disparos_maximos = disparos_maximos
        self._disparos_realizados = 0  
        
        self._colocar_barcos_automaticamente()

    
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
            self._disparos_realizados += 1

        return resultado
    
    
    def obtener_tablero_propio(self) -> list:
        """
        Obtiene el tablero de la máquina con barcos (para Debugging).

        Returns:
            list: Array que representa el tablero de la máquina.
        """
        return self.tablero_maquina.ver_tablero()

    
    def obtener_tablero_rival(self) -> list:
        """
        Devuelve el tablero que debe ver el jugador.
        
        Retunrns:
            list: Array que representa el tablero de la máquina con los barcos ocultos.
        """
        return self.tablero_maquina.ver_tablero_rival()
    
    
    def colocar_barco(self, barco: Barco) -> bool:
        """_summary_

        Args:
            barco (_type_): _description_

        Returns:
            bool: _description_
        """
        return self.tablero_maquina.colocar_barco_aleatorio(barco)


    def hay_victoria(self) -> bool:
        """
        Comprueba si quedan barcos en el tablero interno.

        :return: True si no quedan barcos, False si quedan.
        :rtype: bool
        """
        return self.tablero_maquina.todos_hundidos()


    def quedan_disparos(self) -> bool:
        """
        Indica si aún quedan disparos disponibles.

        :return: True si quedan disparos, False en caso contrario.
        :rtype: bool
        """
        return self._disparos_realizados < self._disparos_maximos


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
    
    
    def _colocar_barcos_automaticamente(self):
        """
        Coloca los barcos automáticamente en el tablero.

        Raises:
            RuntimeError: En caso de que un barco no se pueda colocar.
        """
        for barco in self.tablero_maquina.barcos:
            colocado = self.colocar_barco(barco)            
            if not colocado:
                raise RuntimeError(f"No se pudo colocar el barco {barco.nombre}.")