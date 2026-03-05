import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = "logs/servidor.log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger = logging.getLogger("servidor")
logger.setLevel(logging.INFO)

formato = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# archivo con rotación (máx 1MB, guarda 5)
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,
    backupCount=5,
    encoding="utf-8"
)

file_handler.setFormatter(formato)

# también mostrar en consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formato)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
