import json
import time

from .constants import JobAnalytics
from .exception import JobAnalyticsError
from .log import logging, setup_custom_logger
import pandas as pd
from src import db, settings
from src import client
from . import sql
from .utils import _raise, get_path_temp_from_report, get_size_file, remove_old_temp_files, chunked_iterable

LOGGER = setup_custom_logger(__name__)

if LOGGER.isEnabledFor(logging.DEBUG):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)


def get_empty_df():
    LOGGER.debug("Obteniendo dataframe vacio")
    raw_data = {'id': []}
    df = pd.DataFrame(raw_data, columns=['id'])
    return df


def get_data_by_sql(_sql, _params=None):
    try:
        if _params is None:
            df = pd.read_sql(_sql, db.get_connection_default(), params=[])
        else:
            df = pd.read_sql(_sql, db.get_connection_default(), params=_params)
    except Exception as ex:
        LOGGER.warning("Error en obtener datos")
        LOGGER.exception(ex)
        df = get_empty_df()
    return df


switcher_post_client = {
    JobAnalytics.COMP_FINANCIERO: client.post_comp_financiero,
    JobAnalytics.PRECIO_UNACEM: client.post_precio_unacem,
    JobAnalytics.COSTO: client.post_costo,
    JobAnalytics.PROYECCION: client.post_proyeccion
}


switcher_sql_register = {
    JobAnalytics.COMP_FINANCIERO: sql.REGISTER_COMP_FINANCIERO,
    JobAnalytics.PRECIO_UNACEM: sql.REGISTER_PRECIO_UNACEM,
    JobAnalytics.COSTO: sql.REGISTER_COSTO,
    JobAnalytics.PROYECCION: sql.REGISTER_PROYECCION
}


def create_process(_task_id, _tipo):
    _params = ('PEN', _task_id, _tipo, )
    return db.query_val(db.get_connection_default(), sql.INSERT_PROCESS, _params)


def update_process(_id_process, _estado, _iddataset=None, _resultado=None, _mensaje=None):
    _params = (_estado, _iddataset, _resultado, _mensaje, _id_process, )
    return db.dml(db.get_connection_default(), sql.UPDATE_PROCESS, _params)


def register_resultados(_tipo, _iddataset, _registros):
    _lote = settings.get_size_batch_register_results(_tipo)
    _cnxn = db.get_connection_default()
    _sql = switcher_sql_register.get(_tipo, None)
    if not _sql:
        raise JobAnalyticsError(f'Incorrecto tipo de registro SQL: {_tipo}')
    for i in chunked_iterable(_registros, _lote):
        _input = [(d['id'], d['mensaje'], d['estado'], d['resultado'], _iddataset) for d in i]
        _input = ["utt_resultados", "rep_analytics", ] + _input
        _params = (_input,)
        _res = db.query_one(_cnxn, _sql, _params=_params)
        LOGGER.info(f"resultado de registro por lote de {_lote}: {_res}")


def carga_analytics(_task_id, _sql, _tipo):
    id_process = None
    try:
        LOGGER.info(f"Registrando proceso para carga analytics '{_tipo.name}', _task_id: {_task_id}")
        id_process = create_process(str(_task_id), _tipo.name)

        LOGGER.info(f"Ejecutando SQL para carga analytics '{_tipo.name}', _task_id: {_task_id}, id_process: {id_process}")
        _df = get_data_by_sql(_sql)
        LOGGER.info(f"Dimension del dataframe obtenido por la carga SQL: {_df.shape}")

        if _df.shape[0] == 0:
            _msg = f"No se encontro datos para carga analytics '{_tipo.name}'"
            LOGGER.info(_msg)
            update_process(id_process, 'TER', None, None, _msg)
            return None

        _json = None
        _pathjson = get_path_temp_from_report(_tipo.name, f'{_task_id}-REQUEST.json')
        LOGGER.info(f"Se obtiene el _pathjson: {_pathjson}")
        _df.to_json(_pathjson, orient="records")

        with open(_pathjson) as file:
            _json = json.load(file)

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(f"JSON generado analytics {_tipo.name}, tamaño: {get_size_file(_pathjson)}")

        LOGGER.info("Imprimiendo los primeros 5 registros")
        LOGGER.info(_df.head(5).to_string(index=False))

        LOGGER.info(f"Se procede a invocar al servicio de carga analytics '{_tipo.name}' de Salesforce")
        fn_client = switcher_post_client.get(_tipo, lambda _t: _raise(JobAnalyticsError(f'Incorrecto tipo de client: {_tipo}')))
        res_client = fn_client(_json)
        _pathjson_res = get_path_temp_from_report(_tipo.name, f'{_task_id}-RESPONSE.json')
        LOGGER.info(f"Respuesta de carga analytics {_tipo.name}, response type: {type(res_client)}, path {_pathjson_res}")

        with open(_pathjson_res, 'w', encoding='utf-8') as outfile:
            json.dump(res_client, outfile)

        if not isinstance(res_client, dict):
            raise JobAnalyticsError("Error en respuesta de servicio de Analytics, respuesta no es json")

        _iddataset, _resultado, _mensaje, _registros = res_client.get('idDataset', ''), res_client['resultado'], res_client['mensaje'], res_client['registros']
        _estado = 'TER' if _resultado else 'ERR'
        update_process(id_process, _estado, _iddataset, _resultado, _mensaje)

        if not isinstance(_registros, list):
            raise JobAnalyticsError("Error en respuesta de servicio de Analytics, registros no es lista")

        if len(_registros):
            register_resultados(_tipo, _iddataset, _registros)
            LOGGER.info(f"Se finaliza con la actualizacion de resultados de registros para carga analytics {_tipo.name}")
        else:
            LOGGER.info(f"No se encontro resultados de registros para carga analytics {_tipo.name}")

    except Exception as ex:
        LOGGER.exception(ex)
        if id_process:
            update_process(id_process, 'EXC', _mensaje=str(ex))
        else:
            id_process = -1
    finally:
        LOGGER.info("Se procede a eliminar archivos antiguos")
        remove_old_temp_files(_tipo.name)
        LOGGER.info(f"Finalizacion de proceso de carga analytics {_tipo.name}, id_process: {id_process}")
        return id_process


def carga_analytics_comp_financiero(_task_id):
    return carga_analytics(_task_id, sql.SELECT_ANALYTICS_COMP_FINANCIERO, JobAnalytics.COMP_FINANCIERO)


def carga_analytics_precio_unacem(_task_id):
    return carga_analytics(_task_id, sql.SELECT_ANALYTICS_PRECIO_UNACEM, JobAnalytics.PRECIO_UNACEM)


def carga_analytics_costo(_task_id):
    return carga_analytics(_task_id, sql.SELECT_ANALYTICS_COSTO, JobAnalytics.COSTO)


def carga_analytics_proyeccion(_task_id):
    return carga_analytics(_task_id, sql.SELECT_ANALYTICS_PROYECCION, JobAnalytics.PROYECCION)


def carga_test_mock(_task_id):
    LOGGER.info("START CARGA MOCK DE PRUEBA")
    time.sleep(1)
    LOGGER.info("Se procede a eliminar archivos antiguos")
    remove_old_temp_files(JobAnalytics.TEST.name)
    LOGGER.info("FINISH CARGA MOCK DE PRUEBA")
    return 0


switcher_task = {
    JobAnalytics.COMP_FINANCIERO: carga_analytics_comp_financiero,
    JobAnalytics.PRECIO_UNACEM: carga_analytics_precio_unacem,
    JobAnalytics.COSTO: carga_analytics_costo,
    JobAnalytics.PROYECCION: carga_analytics_proyeccion,
    JobAnalytics.TEST: carga_test_mock,
}
