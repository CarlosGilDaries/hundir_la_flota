import logging
import os

def configurar_logger(nombre: str = "servidor", archivo: str = "red/servidor/servidor_log.log") -> logging.Logger:
    """
    Configura y devuelve un logger que escribe tanto en consola como en un archivo.

    Args:
        nombre (str): nombre del logger
        archivo (str): ruta del archivo donde se volcará el log

    Returns:
        logging.Logger: logger configurado
    """

    logger = logging.getLogger(nombre)

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Handler para archivo
        os.makedirs(os.path.dirname(archivo) or ".", exist_ok=True)
        file_handler = logging.FileHandler(archivo, encoding="utf-8")
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

