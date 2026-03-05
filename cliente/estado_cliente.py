class EstadoCliente:

    def __init__(self):
        self.tablero_propio = None
        self.tablero_rival = None
        self.tu_turno = False
        self.partida_terminada = False
        self.ganador = None

    def actualizar(self, datos: dict) -> None:
        self.turno = datos.get("turno")
        self.estado_partida = datos.get("estado")
        self.tablero_propio = datos.get("propio")
        self.tablero_rival = datos.get("rival")
        self.ganador = datos.get("ganador")