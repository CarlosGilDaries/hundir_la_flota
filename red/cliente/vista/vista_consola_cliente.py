class VistaConsola:

    def mostrar_mensaje(self, mensaje: str) -> None:
        print(mensaje)

    def mostrar_tablero(self, tablero: list) -> None:
        for fila in tablero:
            print(" ".join(fila))
        print()

    def pedir_coordenadas(self) -> tuple[int, int]:
        x = int(input("X: "))
        y = int(input("Y: "))
        return x, y


