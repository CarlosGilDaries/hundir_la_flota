import random

class Barco:

    def __init__(self, nombre,  tamanyo, caracter, horizontal = None):
        """
        Inicializa un barco con un tamaño y una orientación aleatoria.
        La vida restante es igual al tamaño y se va reduciendo en 1
        con cada disparo recibido (método recibir_impacto).

        :param nombre: Nombre del barco.
        :type nombre: str
        :param tamanyo: Tamaño del barco.
        :type tamanyo: int
        :param caracter: Carácter que representa al barco.
        :type caracter: str
        :param horizontal: Booleano que indica si es horizontal (True) o vertical (False). Si no se introduce, se genera aleatorio.
        :type caracter: bool
        """
        self.nombre = nombre
        self.tamanyo = tamanyo
        self.caracter = caracter
        self._vida_restante = tamanyo
        if horizontal is not None: 
            self._horizontal = horizontal
        else: 
            self._horizontal = self.set_horizontal()


    def set_horizontal(self, horizontal = None):
        """
        Determina si la orientación del barco es horizontal o vertical.
        Para el pve lo determina aleatoriamente y para pvp el jugador lo elige introduciendo parámetro.

        :param horizontal: Si el usuario lo introduce, elige orientación del barco.
        :type horizontal: bool
        """
        if horizontal is not None:
            self._horizontal = horizontal
        else:
            self._horizontal = random.choice([True, False])
        
    
    def get_horizontal(self):
        """
        Getter del atributo _horizontal

        Returns:
            bool: Atributo horizontal del barco
        """
        return self._horizontal
    

    def calcular_maximo(self, alto_o_ancho):
        """
        Calcula el límite máximo para colocar un barco en un eje determinado.

        :param alto_o_ancho: Dimensión total del eje.
        :type alto_o_ancho: int
        :return: Posición máxima permitida.
        :rtype: int
        """
        return alto_o_ancho - self.tamanyo
    

    def recibir_impacto(self):
        """
        Resta un punto de vida al barco.
        """
        self._vida_restante -= 1


    def hundido(self):
        """
        Comprueba si el barco ha sido hundido (vida restante es igual a 0).
        
        :return: True si ha sido hundido, False si no.
        :rtype: bool
        """
        return self._vida_restante == 0