import sys
import argparse
from src.constants import JobAnalytics
from src.log import setup_custom_logger

LOGGER = setup_custom_logger(__name__)

if __name__ == '__main__':
    LOGGER.info(f'START APP, argv: {sys.argv[1:]}')
    parser = argparse.ArgumentParser(description='Informacion de tipo de JOB')
    parser.add_argument('--tipo', dest='tipo', metavar='tipo', type=str, help='Tipo de JOB',
                        required=True, choices=[i.name for i in JobAnalytics])
    args = parser.parse_args()
    try:
        LOGGER.info(f"Tipo de job: {args.tipo}")
    except Exception as ex:
        LOGGER.exception(ex)
    except KeyboardInterrupt as key:
        LOGGER.warning("Se finaliza ejecucion de proceso.")
        input("Press Enter to close...")
