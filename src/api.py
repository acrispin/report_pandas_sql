import uuid

from flask import Flask, request, jsonify, make_response
from decouple import config

from src import db
from src.constants import JobAnalytics
from src.exception import JobAnalyticsError
from src.tasks import switcher_task
from src.utils import _raise
from .log import logging, setup_custom_logger

LOGGER = setup_custom_logger(__name__)

DEBUG = config('DEBUG', default=False, cast=bool)
FLASK_HOST = config('FLASK_HOST', default='0.0.0.0', cast=str)
FLASK_PORT = config('FLASK_PORT', default='5000', cast=str)

app = Flask(__name__)


@app.route('/')
def hello_world():
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"method: '{request.method}', path: '{request.path}', ip: '{request.remote_addr}'")
    return jsonify({'message': 'Hello, World!'})


@app.route('/job/carga/analytics/')
def process_carga_analytics():
    try:
        t = request.args.get('t')
        LOGGER.info(f"method: '{request.method}', path: '{request.path}', ip: '{request.remote_addr}', t: '{t}'")
        if not t:
            raise JobAnalyticsError("Error en parametros")
        _id = uuid.uuid1()
        _tipo = JobAnalytics[t.upper()]
        LOGGER.info(f"TASK, INICIO DE EJECUCION, task_id: {_id}, _tipo: {_tipo}")
        fn_task = switcher_task.get(_tipo, lambda _t: _raise(JobAnalyticsError(f'Incorrecto tipo de task: {_tipo}')))
        _id_process = fn_task(_id)
        LOGGER.info(f"TASK, FIN DE EJECUCION, task_id: {_id}, _tipo: {_tipo}, _id_process: {_id_process}")
        return jsonify({'message': 'OK', 'id': _id, 'tipo': _tipo.name, 'process': _id_process})
    except Exception as ex:
        LOGGER.exception(ex)
        return make_response(jsonify({'message': str(ex), 'code': 500, 'status': 'FAIL'}), 500)


if __name__ == '__main__':
    db.test_connection_default()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG, use_reloader=False)
