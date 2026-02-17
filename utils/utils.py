class Util:

    @staticmethod
    def opcion_valida(valor, opcion_maxima):
        """
        Comprueba si un valor introducido es un número entero dentro de un rango válido.

        :param valor: Valor introducido por el usuario.
        :type valor: str
        :param opcion_maxima: Valor máximo permitido.
        :type opcion_maxima: int
        :return: True si el valor es válido, False en caso contrario.
        :rtype: bool
        """
        return valor.isdigit() and 0 <= int(valor) <= opcion_maxima


    @staticmethod
    def es_numero_entero(valor):
        """
        Comprueba si un valor puede convertirse a número entero.

        :param valor: Valor a comprobar.
        :type valor: str
        :return: True si el valor es un entero válido, False en caso contrario.
        :rtype: bool
        """
        try:
            int(valor)
            return True
        except ValueError:
            return False