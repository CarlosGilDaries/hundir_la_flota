from modelo.partida.partida import Partida
from modelo.resultado import ResultadoDisparo
from modelo.board import Tablero
from modelo.ship import Barco
from typing import Optional

class PartidaPVE(Partida):
    """
    Implementación de una partida contra la máquina (PVE).
    """

    def __init__(self, tablero_maquina: Tablero, disparos_maximos: int, barcos_colocados:Optional[bool] = None) -> None:
        """
        Inicializa una nueva partida PVE.

        Args:
            tablero_maquina (Tablero): Tablero donde se colocan los barcos de la máquina.
            disparos_maximos (int): Número máximo de disparos permitidos.
            bacos_colocados (bool): Bandera opcional para introducir barcos manualmente, sólo para testing.
        """
        self.tablero_maquina = tablero_maquina
        self._disparos_maximos = disparos_maximos
        self._disparos_realizados = 0
        
        if not barcos_colocados:
            self._colocar_barcos_automaticamente()

    
    def disparar(self, x: int, y: int) -> ResultadoDisparo:
        """
        Realiza un disparo sobre el tablero de la máquina.

        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.

        Returns:
            ResultadoDisparo: Resultado del disparo.
        """
        [resultado, _] = self.tablero_maquina.recibir_disparo(x, y)
        if resultado != ResultadoDisparo.REPETIDO and resultado != ResultadoDisparo.INVALIDO:
            self._disparos_realizados += 1

        return resultado
    
    
    def obtener_tablero_propio(self) -> list[list[str]]:
        """
        Devuelve el tablero completo de la máquina.

        Utilizado principalmente para debugging.

        Returns:
            list[list[str]]: Tablero con los barcos visibles.
        """
        return self.tablero_maquina.ver_tablero()

    
    def obtener_tablero_rival(self) -> list[list[str]]:
        """
        Devuelve el tablero visible para el jugador.

        Returns:
            list[list[str]]: Tablero con barcos ocultos.
        """
        return self.tablero_maquina.ver_tablero_rival()
    
    
    def colocar_barco(self, barco: Barco) -> bool:
        """
        Coloca un barco de forma automática en el tablero.

        Args:
            barco (Barco): Barco a colocar.

        Returns:
            bool: True si se pudo colocar, False si no.
        """
        return self.tablero_maquina.colocar_barco_aleatorio(barco)


    def hay_victoria(self) -> bool:
        """
        Comprueba si todos los barcos han sido hundidos.

        Returns:
            bool: True si el jugador ha ganado, False si no.
        """
        return self.tablero_maquina.todos_hundidos()


    def quedan_disparos(self) -> bool:
        """
        Comprueba si quedan disparos disponibles.

        Returns:
            bool: True si aún quedan disparos.
        """
        return self._disparos_realizados < self._disparos_maximos


    def disparos_restantes(self) -> int:
        """
        Calcula el número de disparos restantes.

        Returns:
            int: Número de disparos restantes.
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
        Coloca automáticamente todos los barcos del tablero.

        Raises:
            RuntimeError: Si algún barco no se puede colocar.
        """
        for barco in self.tablero_maquina.barcos:
            colocado = self.colocar_barco(barco)            
            if not colocado:
                raise RuntimeError(f"No se pudo colocar el barco {barco.nombre}.")