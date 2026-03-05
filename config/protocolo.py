from enum import Enum


class TipoMensaje(str, Enum):
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
    VICTORIA = "victoria"


def crear_mensaje(tipo: TipoMensaje, **datos) -> dict:
    """
    Crea un mensaje del protocolo.
    """
    mensaje = {"tipo": tipo.value}
    mensaje.update(datos)
    return mensaje


def obtener_tipo(mensaje: dict) -> TipoMensaje:
    """
    Convierte el campo tipo recibido en Enum.
    """
    return TipoMensaje(mensaje["tipo"])
