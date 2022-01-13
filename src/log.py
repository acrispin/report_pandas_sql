import os
from decouple import config

import logging
from logging.handlers import RotatingFileHandler

LOGFILE_PATH = config('LOGFILE_PATH', default='', cast=str)
LOGFILE_SIZE = config('LOGFILE_SIZE', default=25, cast=float)
LOGFILE_COUNT = config('LOGFILE_COUNT', default=10, cast=int)
LOGFILE_DIR = config('LOGFILE_DIR', default='logs', cast=str)
LOGFILE_NAME = config('LOGFILE_NAME', default='', cast=str)

""" Ejemplo configuracion en archivo .env
# LOGFILE_PATH, ruta de archivos logs, esta debe tener permisos de lectura y escritura
# LOGFILE_PATH, si se especifica el valor de LOGFILE_DIR queda sin efecto
# LOGFILE_PATH, si no se especifica la aplicacion crea una ruta por defecto en la carpeta raiz de las fuentes
# ejm windows: LOGFILE_PATH=D:/logs/app
# ejm linux: LOGFILE_PATH=/DATA/logs/app
# LOGFILE_SIZE, tamño de archivo log en MB, por defecto 25MB
# LOGFILE_COUNT, numero maximo de archivo logs para rollover, por defecto 10 logs
# LOGFILE_DIR, si no se especifica la aplicacion le asigna por defecto el valor de 'logs'
# LOGFILE_NAME, si no se especifica la aplicacion toma el nombre base de la carpeta raiz de las fuentes
LOGFILE_PATH=D:/logs/app
LOGFILE_SIZE=4
LOGFILE_COUNT=10
LOGFILE_DIR=logs
LOGFILE_NAME=app.log
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_LOGS = os.path.join(BASE_DIR, LOGFILE_DIR if LOGFILE_DIR else 'logs')
FILE_LOG = LOGFILE_NAME if LOGFILE_NAME else os.path.basename(BASE_DIR) + ".log"
MAX_BYTES = int(LOGFILE_SIZE * 1024 * 1024)
BACKUP_COUNT = LOGFILE_COUNT
DEBUG = config('DEBUG', default=False, cast=bool)
LOGGER_LEVEL = logging.DEBUG if DEBUG else logging.INFO
FORMAT_LOGGER_TEXT = '%(levelname)s [%(asctime)s] [%(name)s.%(funcName)s:%(lineno)d] >>> %(message)s'

_message_path = ''
if LOGFILE_PATH:
    _message_path += f"Se encuentra path personalizado '{LOGFILE_PATH}', "
    _message_path += f"Se reemplaza path base '{DIR_LOGS}', "
    from pathlib import Path

    DIR_LOGS = Path(LOGFILE_PATH)
    _message_path += f"Nuevo path de logs '{DIR_LOGS}'"

if not os.path.isdir(DIR_LOGS):
    os.mkdir(DIR_LOGS)

logging.basicConfig(
    level=LOGGER_LEVEL,
    format=FORMAT_LOGGER_TEXT
)

path_log_final = os.path.join(DIR_LOGS, FILE_LOG)
formatter = logging.Formatter(FORMAT_LOGGER_TEXT)
fileHandler = RotatingFileHandler(
    # filename=f'{DIR_LOGS}/{FILE_LOG}',
    filename=path_log_final,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT)
fileHandler.setLevel(LOGGER_LEVEL)
fileHandler.setFormatter(formatter)

logging = logging


def setup_custom_logger(_name):
    _logger = logging.getLogger(_name)
    _logger.addHandler(fileHandler)
    return _logger


LOGGER = setup_custom_logger(__name__)
LOGGER.info(f"Se configura logs modo: '{logging.getLevelName(LOGGER_LEVEL)}'")
LOGGER.info(f"Se configura logs ruta: '{path_log_final}'")
LOGGER.info(f"Se configura logs size: '{LOGFILE_SIZE} MB' y count: '{LOGFILE_COUNT} logs'")
LOGGER.info(f"Se configura logs directorio: '{DIR_LOGS}' y file: '{FILE_LOG}'")

if LOGGER.isEnabledFor(logging.DEBUG) and _message_path:
    LOGGER.debug(f"Detalle de ruta logs personalizado: {_message_path}")

SENTRY_DSN = config('SENTRY_DSN', default='', cast=str)
if SENTRY_DSN:
    LOGGER.info(f"SENTRY, Se encuentra cadena dsn: {SENTRY_DSN}")
    import sentry_sdk

    if not sentry_sdk.Hub.current.client:
        try:
            sentry_sdk.init(SENTRY_DSN)
            LOGGER.info("SENTRY, Se inicializa correctamente.")
        except Exception as ex:
            LOGGER.warning("SENTRY, Excepcion en configuracion")
            LOGGER.exception(ex)
else:
    LOGGER.info("SENTRY, no se configuro cadena dsn.")
