from utils.excepciones import SalirDelPrograma

class Menu:

    def __init__(self, interfaz, instrucciones):
        """
        Inicializa un menú con opciones para que el usuario interactúe

        :param interfaz: Objeto de la clase InterfazConsola.
        :type interfaz: InterfazConsola
        :param instrucciones: Instrucciones del juego.
        :type instrucciones: str
        """
        self._interfaz = interfaz
        self._instrucciones = instrucciones


    def ejecutar_menu_principal(self):
        """
        Ejecuta el menú principal mostrando las opciones hasta que el usuario inicie el juego o decida salir.
        
        :return: El valor devuelto por el menú de dificultad cuando el usuario selecciona jugar.
        :rtype: str
        :raises SalirDelPrograma: Si el usuario selecciona la opción de salir.
        """
        self._interfaz.borrar_consola()
        while True:
            opcion = self._menu_principal()

            match opcion:
                case "1":
                    return self.ejecutar_menu_dificultad()
                case "2":
                    return 4
                case "3":
                    self._interfaz.mostrar_instrucciones(self._instrucciones)
                case "4":
                    raise SalirDelPrograma()
                case _:
                    self._interfaz.borrar_consola()
                    print(self._interfaz.obtener_texto("ERROR_MENU"))

    
    def ejecutar_menu_dificultad(self):
        """
        Ejecuta el menú de dificultad.
        
        :return: El número correspondiente a la opción.
        :rtype: int
        """
        self._interfaz.borrar_consola()
        while True:
            opcion = self._menu_dificultad()

            match opcion:
                case "1":
                    return 1
                case "2":
                    return 2
                case "3":
                    return 3
                case _:
                    self._interfaz.borrar_consola()
                    print(self._interfaz.obtener_texto("ERROR_MENU"))


    def _menu_principal(self):
        """
        Muestra las opciones del menú principal y solicita una opción al usuario.
        
        :return: Opción introducida por el usuario.
        :rtype: str
        """
        print("")
        print("HUNDIR LA FLOTA")
        print("")
        print("1. Jugar contra la Máquina (PVE)")
        print("2. Jugar contra otro/a Jugador/a (PVP)")
        print("3. Instrucciones")
        print("4. Salir")
        print("")
        return input("Introduzca el número correspondiente a la opción deseada: ")
    

    def _menu_dificultad(self):
        """
        Muestra las dificultades.
        
        :return: Opción introducida por el usuario.
        :rtype: str
        """
        print("")
        print("Dificultad")
        print("")
        print("1. Fácil")
        print("2. Media")
        print("3. Difícil")
        print("")
        return input("Introduzca el número correspondiente a la opción deseada: ")