class Util:
    """
    Clase utilitaria que agrupa funciones auxiliares
    para validación de datos introducidos por el usuario.
    """
    @staticmethod
    def opcion_valida(valor: str, opcion_maxima: int) -> bool:
        """
        Comprueba si un valor introducido es un número entero dentro de un rango válido.

        Args:
            valor (str): Valor introducido por el usuario.
            opcion_maxima (int): Valor máximo permitido.

        Returns:
            bool: True si el valor es un entero dentro del rango permitido,
            False en caso contrario.
        """
        return valor.isdigit() and 0 <= int(valor) <= opcion_maxima


    @staticmethod
    def es_numero_entero(valor: str) -> bool:
        """
        Comprueba si un valor puede convertirse a número entero.

        Args:
            valor (str): Valor a comprobar.

        Returns:
            bool: True si el valor es un entero válido, False en caso contrario.
        """
        try:
            int(valor)
            return True
        except ValueError:
            return False