from enum import Enum
from typing import Any

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
