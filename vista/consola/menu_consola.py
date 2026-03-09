from utils.excepciones import SalirDelPrograma
from vista.consola.vista_consola import VistaConsola
from config.constantes import CONSTANTES

class Menu:

    def __init__(self, interfaz: VistaConsola, instrucciones: str) -> None:
        """
        Inicializa un menú con opciones para que el usuario interactúe

        Args:
            interfaz (VistaConsola): Objeto de la clase VistaConsola.
            instrucciones (str): VistaConsola
        """
        self._interfaz = interfaz
        self._instrucciones = instrucciones


    def ejecutar_menu_principal(self) -> int:
        """
        Ejecuta el menú principal del juego.
        El menú se muestra de forma repetida hasta que el usuario
        selecciona iniciar una partida o salir del programa.

        Returns:
            int:
                - 1, 2 o 3 → dificultad seleccionada para modo PVE
                - 4 → iniciar modo PVP

        Raises:
            SalirDelPrograma: Si el usuario selecciona salir.
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

    
    def ejecutar_menu_dificultad(self) -> int:
        """
        Ejecuta el menú de dificultad.

        Returns:
            int: El número correspondiente a la opción.
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

        Returns:
            str: Número introducido por el usuario por teclado.
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
    

    def _menu_dificultad(self) -> str:
        """
        Muestra las dificultades.

        Returns:
            str: Opción introducida por el usuario.
        """
        print("")
        print("Dificultad")
        print("")
        
        for num, dificultad in CONSTANTES["DIFICULTAD"]["PVE"].items():
            print(f"{num}. {dificultad['nombre']}")
        
        print("")
        return input("Introduzca el número correspondiente a la opción deseada: ")