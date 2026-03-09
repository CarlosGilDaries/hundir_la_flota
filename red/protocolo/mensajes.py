from enum import Enum
from typing import Any, TypedDict, TypeAlias

class TipoMensaje(str, Enum):
    """
    Enumeración de los tipos de mensajes del protocolo cliente-servidor.
    Cada valor representa una acción o evento dentro del flujo de la partida.
    """
    ESPERA = "espera"
    INICIO = "inicio"
    LISTA_BARCOS = "lista_barcos"
    SELECCIONAR_BARCO = "seleccionar_barco"
    DISPARO = "disparo"
    RESULTADO = "resultado"
    RECIBIDO = "recibido"
    ESTADO_TABLEROS = "estado_tableros"
    TURNO = "turno"
    CONFIRMACION = "confirmacion"
    ERROR = "error"
    FIN = "fin"
    SALIR = "salir"
    

class MensajeBase(TypedDict):
    """
    Tipo base de todos los mensajes del protocolo.

    Todos los mensajes deben incluir el campo `tipo`.
    """
    tipo: str


class MensajeInicio(MensajeBase):
    """
    Mensaje enviado por el servidor al iniciar la partida.

    Attributes:
        tipo (str): Tipo del mensaje ("inicio").
        jugador (int): Identificador del jugador asignado (1 o 2).
    """
    jugador: int


class MensajeListaBarcos(MensajeBase):
    """
    Mensaje que contiene la lista de barcos pendientes de colocar.

    Attributes:
        barcos (list[dict[str, Any]]): Lista de barcos disponibles.
    """
    barcos: list[dict[str, Any]]


class MensajeSeleccionBarco(MensajeBase):
    """
    Mensaje enviado por el cliente para colocar un barco.

    Attributes:
        indice (int): Índice del barco seleccionado.
        x (int): Coordenada horizontal.
        y (int): Coordenada vertical.
        horizontal (bool): Orientación del barco.
    """
    indice: int
    x: int
    y: int
    horizontal: bool


class MensajeDisparo(MensajeBase):
    """
    Mensaje enviado por el cliente para disparar.

    Attributes:
        x (int): Coordenada horizontal del disparo.
        y (int): Coordenada vertical del disparo.
    """
    x: int
    y: int


class MensajeResultado(MensajeBase):
    """
    Resultado de un disparo enviado al jugador atacante.

    Attributes:
        resultado (str): Resultado del disparo.
        x (int): Coordenada horizontal.
        y (int): Coordenada vertical.
    """
    resultado: str
    x: int
    y: int


class MensajeRecibido(MensajeBase):
    """
    Mensaje enviado al rival cuando recibe un disparo.

    Attributes:
        resultado (str): Resultado del disparo.
        x (int): Coordenada horizontal.
        y (int): Coordenada vertical.
    """
    resultado: str
    x: int
    y: int


class MensajeTurno(MensajeBase):
    """
    Mensaje que indica si es el turno del jugador.

    Attributes:
        tu_turno (bool): Indica si el jugador puede disparar.
    """
    tu_turno: bool


class MensajeEstadoTableros(MensajeBase):
    """
    Mensaje que contiene el estado de los tableros.

    Attributes:
        propio (Any): Estado del tablero del jugador.
        rival (Any): Estado visible del tablero rival.
    """
    propio: Any
    rival: Any


class MensajeConfirmacion(MensajeBase):
    """
    Mensaje de confirmación de una acción.

    Attributes:
        mensaje (str): Texto informativo.
    """
    mensaje: str


class MensajeError(MensajeBase):
    """
    Mensaje de error enviado por el servidor.

    Attributes:
        mensaje (str): Descripción del error.
    """
    mensaje: str


class MensajeFin(MensajeBase):
    """
    Mensaje enviado al finalizar la partida.

    Attributes:
        victoria (bool): Indica si el jugador ha ganado.
    """
    victoria: bool
    
    
MensajeProtocolo: TypeAlias = (
    MensajeInicio
    | MensajeListaBarcos
    | MensajeSeleccionBarco
    | MensajeDisparo
    | MensajeResultado
    | MensajeRecibido
    | MensajeTurno
    | MensajeEstadoTableros
    | MensajeConfirmacion
    | MensajeError
    | MensajeFin
)


def crear_mensaje(tipo: TipoMensaje, **datos: Any) -> dict[str, Any]:
    """
    Construye un mensaje del protocolo.
    El mensaje siempre contiene el campo `tipo` y puede incluir
    cualquier otro dato adicional necesario para el evento.

    Args:
        tipo (TipoMensaje): Tipo de mensaje.
        **datos (Any): Datos adicionales del mensaje.

    Returns:
        dict[str, Any]: Diccionario listo para serializar como JSON.
    """
    mensaje = {"tipo": tipo.value}
    mensaje.update(datos)
    return mensaje


def obtener_tipo(mensaje: dict[str, Any]) -> TipoMensaje:
    """
    Convierte el campo `tipo` recibido en su valor Enum.

    Args:
        mensaje (dict[str, Any]): Mensaje recibido del cliente o servidor.

    Returns:
        TipoMensaje: Tipo del mensaje.
    """
    return TipoMensaje(mensaje["tipo"])
