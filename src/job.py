from datetime import datetime, timedelta
import uuid

import schedule
import time

from src.constants import JobAnalytics
from src.exception import JobAnalyticsError
from src.tasks import switcher_task
from src.utils import _raise
from .log import logging, setup_custom_logger
from . import db as db, settings

LOGGER = setup_custom_logger(__name__)


def get_date_by_number(_days):
    if _days >= 0:
        d = datetime.today() + timedelta(days=abs(_days))
    else:
        d = datetime.today() - timedelta(days=abs(_days))
    return d.strftime(settings.get_formato_fecha())


def get_time_ini(_tipo):
    return datetime.strptime(settings.get_hora_inicio(_tipo), settings.get_formato_hora(_tipo)).time()


def get_time_fin(_tipo):
    return datetime.strptime(settings.get_hora_fin(_tipo), settings.get_formato_hora(_tipo)).time()


def calculate_hora_fin_raw(_tipo):
    kwargs = {'microsecond': 0,
              'second': get_time_fin(_tipo).second,
              'minute': get_time_fin(_tipo).minute,
              'hour': get_time_fin(_tipo).hour}
    _now = datetime.now()
    _fin = _now.replace(**kwargs)
    return _fin


def calculate_hora_ini(_tipo):
    kwargs = {'microsecond': 0,
              'second': get_time_ini(_tipo).second,
              'minute': get_time_ini(_tipo).minute,
              'hour': get_time_ini(_tipo).hour}
    _now = datetime.now()
    _ini = _now.replace(**kwargs)
    if _now > _ini and _now > calculate_hora_fin_raw(_tipo):
        _ini += timedelta(days=1)
    return _ini


def calculate_hora_fin(_tipo):
    _fin = calculate_hora_fin_raw(_tipo)
    _ini = calculate_hora_ini(_tipo)
    if _ini >= _fin:
        _fin += timedelta(days=(_ini - _fin).days + 1)
    return _fin


def run(_tipo, _ejecucion_inmediata=False):
    _id = uuid.uuid1()
    LOGGER.info(f"TASK, se crea task_id: {_id}, _tipo: {_tipo}")
    try:
        _ini = calculate_hora_ini(_tipo)
        _fin = calculate_hora_fin(_tipo)
        _now = datetime.now()
        LOGGER.info(f"TASK, fecha/hora antes _ini: '{_ini}', _fin: '{_fin}', _now: '{_now}'")
        if not (_ini < _now < _fin) and not _ejecucion_inmediata:
            LOGGER.warning(f"TASK, STOP DE EJECUCION por fecha actual no se encuentra dentro del rango de ejcucion.")
            return None
        LOGGER.info(f"TASK, INICIO DE EJECUCION, task_id: {_id}, _tipo: {_tipo}")
        fn_task = switcher_task.get(_tipo, lambda _t: _raise(JobAnalyticsError(f'Incorrecto tipo de task: {_tipo}')))
        fn_task(_id)
    except Exception as ex:
        LOGGER.warning(f"TASK, ejecucion con excepcion, task_id: {_id}")
        LOGGER.exception(ex)
    else:
        LOGGER.info(f"TASK, FIN DE EJECUCION, task_id: {_id}")
    finally:
        _ini = calculate_hora_ini(_tipo)
        _fin = calculate_hora_fin(_tipo)
        _now = datetime.now()
        _next = _now + timedelta(seconds=settings.get_interval_seconds(_tipo))
        LOGGER.info(f"TASK, fecha/hora despues _ini: '{_ini}', _fin: '{_fin}', _now: '{_now}', _next: '{_next}'")
        if not (_ini < _now < _fin and _next < _fin) or _ejecucion_inmediata:
            LOGGER.info(f"TASK, ingresando a cancelar tarea, task_id: {_id}")
            if _ejecucion_inmediata:
                _diff_date = _ini - _now \
                    if _ini > _now \
                    else _ini + timedelta(days=1) - _now
                _total_seg = _diff_date.total_seconds() if not (_ini < _now < _fin) else settings.get_interval_seconds(_tipo)
                LOGGER.info(f"TASK, se cancela tarea por ejecucion inmediata, task_id: {_id}, "
                            f"siguiente ejecucion en {settings.get_text_by_seconds(_tipo, _total_seg)}.")
            else:
                _jobs = [_job for _job in schedule.jobs if wrap_run.__name__ in _job.tags]
                _total_seg = (_jobs[0].next_run - _now).total_seconds() if len(_jobs) > 0 else -1
                _total_seg = _total_seg if _total_seg > 0 else settings.get_interval_seconds(_tipo)
                LOGGER.info(f"TASK, se cancela tarea por rango horario, task_id: {_id}, "
                            f"siguiente ejecucion en {settings.get_text_by_seconds(_tipo, _total_seg)}.")
            return schedule.CancelJob
        LOGGER.info(f"TASK, no se cancela tarea, task_id: {_id}, "
                    f"siguiente ejecucion en {settings.get_next_interval_texto(_tipo)}.")
        return None


def wrap_run(_tipo):
    _ini = calculate_hora_ini(_tipo)
    _fin = calculate_hora_fin(_tipo)
    LOGGER.info(f"Inicio task wrapper con frecuencia de '{settings.get_frecuencia_texto(_tipo)}' y "
                f"entre las [{_ini} - {_fin}] horas.")

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"Calculando fecha/hora inicial: {_ini}")
        LOGGER.debug(f"Calculando fecha/hora final: {_fin}")

    run(_tipo)
    schedule.every(settings.get_interval_seconds(_tipo)).seconds.do(run, _tipo)
    LOGGER.info(f"Se finaliza ejecucion de wrap.")


def wrap_config(_tipo):
    _ini = calculate_hora_ini(_tipo)
    _fin = calculate_hora_fin(_tipo)
    _now = datetime.now()
    _next = _now + timedelta(seconds=settings.get_interval_seconds(_tipo))
    _next_str = _next.strftime(settings.get_formato_fechahora(_tipo))
    _is_continue = False
    if _ini < _now < _fin and _next < _fin:
        LOGGER.info(f"Hora actual y proxima ejecucion: '{_next_str}' "
                    f"esta dentro del rango de ejecucion del JOB, "
                    f"se procede a configurar wrapper de continuacion.")
        _next_str_hour = _next.strftime(settings.get_formato_hora(_tipo))
        schedule.every().day.at(_next_str_hour).until(_fin).do(wrap_run, _tipo).tag(wrap_run.__name__)
        LOGGER.info(f"Se configura wrapper de continuacion con hora de inicio: '{_next_str}' hasta las '{_fin}', "
                    f"siguiente ejecucion en {settings.get_next_interval_texto(_tipo)}.")
        _is_continue = True

    schedule.every().day.at(settings.get_hora_inicio(_tipo)).do(wrap_run, _tipo).tag(wrap_run.__name__)

    if _is_continue:
        LOGGER.info(f"Se configura wrapper diario, con hora de inicio diaria: '{settings.get_hora_inicio(_tipo)}'")
    else:
        LOGGER.info(f"Se configura wrapper diario, con hora de inicio diaria: '{settings.get_hora_inicio(_tipo)}', "
                    f"siguiente ejecucion en {settings.get_text_by_seconds(_tipo, schedule.idle_seconds())}.")


def check_config_dates(_tipo, _ini, _fin, _interval):
    _next = _ini + timedelta(seconds=_interval)
    if _next > _fin:
        raise JobAnalyticsError(f"Incorrecta configuracion de JOB '{_tipo.name}' con fecha inicio y fin, "
                                f"siguiente ejecucion '{_next}' no puede ser mayor "
                                f"que la fecha fin configurada '{_fin}'")


def check_config_values(_tipo):
    _config_hora_inicio = settings.get_hora_inicio(_tipo)
    _config_hora_fin = settings.get_hora_fin(_tipo)
    _config_frecuencia_unidad = settings.get_frecuencia_unidad(_tipo)
    _config_frecuencia_valor = settings.get_frecuencia_valor(_tipo)
    if not _config_hora_inicio or not _config_hora_fin or not _config_frecuencia_unidad or _config_frecuencia_valor <= 0:
        raise JobAnalyticsError(f"Incorrecta configuracion de JOB '{_tipo.name}', verificar valores en archivo '.env'")
    if not db.test_connection_default():
        LOGGER.warning("Error en test de conexion a base de datos, verificar!!!")


def ini(_tipo):
    check_config_values(_tipo)
    _ini = calculate_hora_ini(_tipo)
    _fin = calculate_hora_fin(_tipo)
    _interval = settings.get_interval_seconds(_tipo)
    LOGGER.info(f"Inicio Servicio JOB '{_tipo.name}' con rango horario de: [{_ini.time()} - {_fin.time()}] diariamente "
                f"y con frecuencia de '{settings.get_frecuencia_texto(_tipo)}'.")

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"Calculando fecha/hora inicial: {_ini}")
        LOGGER.debug(f"Calculando fecha/hora final: {_fin}")
        LOGGER.debug(f"Diferencia de rango horario: {settings.get_text_by_seconds(_tipo, (_fin - _ini).total_seconds())}")

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug("Log DEBUG habilitado en proceso JOB.")

    check_config_dates(_tipo, _ini, _fin, _interval)

    if settings.get_run_immediate(_tipo):
        LOGGER.info("Ejecucion inmediata de tarea para proceso JOB.")
        # schedule.every().seconds.do(run, _tipo, True)
        run(_tipo, True)
    else:
        LOGGER.info("No se ha configurado ejecucion inmediata de JOB.")

    wrap_config(_tipo)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    ini(JobAnalytics.TEST)
