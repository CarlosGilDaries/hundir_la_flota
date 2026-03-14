import random
from typing import Optional

class Barco:

    def __init__(self, nombre: str, tamanyo: int, caracter: str, horizontal: Optional[bool] = None) -> None:
        """
        Inicializa un barco con un tamaño y una orientación aleatoria.
        La vida restante es igual al tamaño y se va reduciendo en 1 con cada disparo recibido.

        Args:
            nombre (str): Nombre del barco.
            tamanyo (int): Tamaño del barco.
            caracter (str): Carácter que representa al barco.
            horizontal (Optional[bool], optional): Indica si es horizontal (True) o vertical (False).
                Si no se introduce, se genera aleatorio. Defaults to None.

        Returns:
            None
        """
        self.nombre = nombre
        self.tamanyo = tamanyo
        self.caracter = caracter
        self._vida_restante = tamanyo
        if horizontal is not None: 
            self._horizontal = horizontal
        else: 
            self.set_horizontal()


    def set_horizontal(self, horizontal: Optional[bool] = None) -> None:
        """
        Determina si la orientación del barco es horizontal o vertical.
        Para PvE lo determina aleatoriamente; para PvP, se puede especificar manualmente.

        Args:
            horizontal (Optional[bool], optional): Orientación elegida por el usuario. Defaults to None.

        Returns:
            None
        """
        if horizontal is not None:
            self._horizontal = horizontal
        else:
            self._horizontal = random.choice([True, False])
        
    
    def get_horizontal(self) -> bool:
        """
        Devuelve la orientación del barco.

        Returns:
            bool: True si el barco es horizontal, False si es vertical.
        """
        return self._horizontal
    

    def calcular_maximo(self, alto_o_ancho: int) -> int:
        """
        Calcula la posición máxima para colocar un barco en un eje determinado.

        Args:
            alto_o_ancho (int): Dimensión total del eje.

        Returns:
            int: Posición máxima permitida para el barco.
        """
        return alto_o_ancho - self.tamanyo
    

    def recibir_impacto(self) -> None:
        """
        Resta un punto de vida al barco.
        """
        self._vida_restante -= 1


    def hundido(self) -> bool:
        """
        Comprueba si el barco ha sido hundido.

        Returns:
            bool: True si el barco no tiene vida restante, False en caso contrario.
        """
        return self._vida_restante == 0