class VolverAlMenu(Exception):
    """Se lanza cuando el usuario decide terminar el juego."""
    pass

class SalirDelPrograma(Exception):
    """Se lanza cuando el usuario decide terminar el programa."""
    pass

class YaHayBarcoEnPosicion(Exception):
    """Se lanza cuando el usuario intenta colocar un barco en una posición ya ocupada."""
    pass