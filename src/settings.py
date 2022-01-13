from decouple import config

from src.constants import FrecuenciaUnidad
from src.exception import JobAnalyticsError


def get_formato_fecha(_tipo=None):
    if _tipo is None:
        return config(f'JOB_FORMATO_FECHA', default='%Y-%m-%d', cast=str)
    else:
        return config(f'JOB_FORMATO_FECHA_{_tipo.name}', default='%Y-%m-%d', cast=str)


def get_formato_hora(_tipo=None):
    if _tipo is None:
        return config(f'JOB_FORMATO_HORA', default='%H:%M:%S', cast=str)
    else:
        return config(f'JOB_FORMATO_HORA_{_tipo.name}', default='%H:%M:%S', cast=str)


def get_formato_fechahora(_tipo=None):
    if _tipo is None:
        return config(f'JOB_FORMATO_FECHAHORA', default='%Y-%m-%d %H:%M:%S', cast=str)
    else:
        return config(f'JOB_FORMATO_FECHAHORA_{_tipo.name}', default='%Y-%m-%d %H:%M:%S', cast=str)


def get_size_batch_register_results(_tipo=None):
    if _tipo is None:
        return config(f'BATCH_SIZE_REGISTER_RESULTS', default=500, cast=int)
    else:
        return config(f'BATCH_SIZE_REGISTER_RESULTS_{_tipo.name}', default=500, cast=int)


def get_hora_inicio(_tipo):
    return config(f'{_tipo.name}_HORA_INICIO', default='', cast=str)


def get_hora_fin(_tipo):
    return config(f'{_tipo.name}_HORA_FIN', default='', cast=str)


def get_run_immediate(_tipo):
    return config(f'{_tipo.name}_INICIAR_INMEDIATO', default=False, cast=bool)


def get_frecuencia_unidad(_tipo):
    return config(f'{_tipo.name}_FRECUENCIA_UNIDAD', default='', cast=str)


def get_frecuencia_valor(_tipo):
    return config(f'{_tipo.name}_FRECUENCIA_VALOR', default=0, cast=float)


switcher_factor = {
    FrecuenciaUnidad.SEGUNDOS.value: 1,
    FrecuenciaUnidad.MINUTOS.value: 60,
    FrecuenciaUnidad.HORAS.value: 3600
}


def get_interval_seconds(_tipo):
    _unidad = get_frecuencia_unidad(_tipo)
    _valor = get_frecuencia_valor(_tipo)
    _factor = switcher_factor.get(_unidad, 0)
    if _factor == 0:
        raise JobAnalyticsError(f"Incorrecto valor de unidad frecuencia: '{_unidad}' para JOB '{_tipo}', "
                                f"valores permitidos: {tuple([i.value for i in FrecuenciaUnidad])}")
    _interval = _valor * _factor
    if _interval <= 0:
        raise JobAnalyticsError(f"Incorrecto valor de frecuencia: '{_valor}' para JOB '{_tipo}', "
                                f"debe ser mayor a cero.")
    return _interval


def get_frecuencia_texto(_tipo):
    _unidad = get_frecuencia_unidad(_tipo)
    _valor = get_frecuencia_valor(_tipo)
    return f"{_valor} {FrecuenciaUnidad(_unidad).name.lower()}"


def get_text_by_seconds(_tipo, _segundos):
    _unidad = get_frecuencia_unidad(_tipo)
    _factor = switcher_factor.get(_unidad, 0)
    if _factor == 0:
        raise JobAnalyticsError(f"Incorrecto valor de unidad frecuencia: '{_unidad}' para JOB '{_tipo}', "
                                f"valores permitidos: {tuple([i.value for i in FrecuenciaUnidad])}")
    return f"{_segundos / _factor} {FrecuenciaUnidad(_unidad).name.lower()}"


def get_next_interval_texto(_tipo):
    _segundos = get_interval_seconds(_tipo)
    return get_text_by_seconds(_tipo, _segundos)
