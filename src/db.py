import pyodbc as pyodbc
from decouple import config

from src.constants import Marca
from src.exception import JobAnalyticsError
from .log import logging, setup_custom_logger

LOGGER = setup_custom_logger(__name__)

# Credenciales de base de datos
DB_SERVER = config('DEFAULT_DB_SERVER', default='localhost', cast=str)
DB_PORT = config('DEFAULT_DB_PORT', default='', cast=str)
DB_NAME = config('DEFAULT_DB_NAME', default='dbname', cast=str)
DB_USER = config('DEFAULT_DB_USER', default='username', cast=str)
DB_PASSWORD = config('DEFAULT_DB_PASSWORD', default='password', cast=str)

# The timeout for the connection attempt, in seconds.
DB_CONNECTION_TIMEOUT = config('DB_CONNECTION_TIMEOUT', default=6, cast=int)

# The timeout value, in seconds, for SQL queries (note, not database connections). Use zero, the default, to disable.
DB_STATEMENT_TIMEOUT = config('DB_STATEMENT_TIMEOUT', default=300, cast=int)


if DB_PORT:
    CONN_STR_DEFAULT = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                       f'SERVER={DB_SERVER},{DB_PORT};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};'
else:
    CONN_STR_DEFAULT = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                       f'SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};'


def __get_connection(_autocommit=False, _conn_str=CONN_STR_DEFAULT):
    try:
        _cnxn = pyodbc.connect(_conn_str, autocommit=_autocommit, timeout=DB_CONNECTION_TIMEOUT)
        _cnxn.timeout = DB_STATEMENT_TIMEOUT
        return _cnxn
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def __get_conn_str_default():
    db_server = config('DEFAULT_DB_SERVER', default='', cast=str)
    db_port = config('DEFAULT_DB_PORT', default='', cast=str)
    db_name = config('DEFAULT_DB_NAME', default='', cast=str)
    db_user = config('DEFAULT_DB_USER', default='', cast=str)
    db_password = config('DEFAULT_DB_PASSWORD', default='', cast=str)
    if not db_server or not db_name or not db_user or not db_password:
        raise JobAnalyticsError(f"Credenciales incorrectas para conexion a base de datos tipo: 'DEFAULT', verificar valores en archivo '.env'")

    if db_port:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server},{db_port};DATABASE={db_name};UID={db_user};PWD={db_password};'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_password};'
    return conn_str


def __get_conn_str_general(_enviroment):
    db_server = config(f'{_enviroment}_DB_SERVER', default='', cast=str)
    db_port = config(f'{_enviroment}_DB_PORT', default='', cast=str)
    db_name = config(f'{_enviroment}_DB_NAME', default='', cast=str)
    db_user = config(f'{_enviroment}_DB_USER', default='', cast=str)
    db_password = config(f'{_enviroment}_DB_PASSWORD', default='', cast=str)
    if not db_server or not db_name or not db_user or not db_password:
        raise JobAnalyticsError(f"Credenciales incorrectas para conexion a base de datos tipo: 'GENERAL' con entorno: '{_enviroment}', verificar valores en archivo '.env'")

    if db_port:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server},{db_port};DATABASE={db_name};UID={db_user};PWD={db_password};'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_password};'
    return conn_str


def __get_conn_str_unicon(_marca, _type):
    db_server = config(f'{_marca.value}_{_type}_DB_SERVER', default='', cast=str)
    db_port = config(f'{_marca.value}_{_type}_DB_PORT', default='', cast=str)
    db_name = config(f'{_marca.value}_{_type}_DB_NAME', default='', cast=str)
    db_user = config(f'{_marca.value}_{_type}_DB_USER', default='', cast=str)
    db_password = config(f'{_marca.value}_{_type}_DB_PASSWORD', default='', cast=str)
    if not db_server or not db_name or not db_user or not db_password:
        raise JobAnalyticsError(f"Credenciales incorrectas para conexion a base de datos tipo: '{_type}' con marca: '{_marca.name}', verificar valores en archivo '.env'")

    if db_port:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server},{db_port};DATABASE={db_name};UID={db_user};PWD={db_password};'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};' \
                   f'SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_password};'

    return conn_str


def __get_conn_str_sdc(_marca):
    return __get_conn_str_unicon(_marca, "SDC")


def __get_conn_str_cmd(_marca):
    return __get_conn_str_unicon(_marca, "CMD")


def get_connection_default(_autocommit=False):
    return __get_connection(_autocommit, __get_conn_str_default())


def get_connection_general(_enviroment, _autocommit=False):
    return __get_connection(_autocommit, __get_conn_str_general(_enviroment))


def get_connection_unicon(_marca, _type, _autocommit=False):
    return __get_connection(_autocommit, __get_conn_str_unicon(_marca, _type))


def get_connection_sdc(_marca, _autocommit=False):
    return __get_connection(_autocommit, __get_conn_str_sdc(_marca))


def get_connection_cmd(_marca, _autocommit=False):
    return __get_connection(_autocommit, __get_conn_str_cmd(_marca))


def check_conection_default(_cnxn=None, _autocommit=False):
    LOGGER.debug("Check conexion a base de datos tipo: 'DEFAULT'.")
    if not _cnxn:
        _cnxn = get_connection_default(_autocommit)
    try:
        with _cnxn.cursor() as _cur:
            _cur.execute("SELECT 1;")
        return True
    except pyodbc.DatabaseError as err:
        LOGGER.exception(err)
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def check_conection_general(_enviroment, _cnxn=None, _autocommit=False):
    LOGGER.info(f"Check conexion a base de datos tipo: 'GENERAL' con entorno: '{_enviroment}'.")
    if not _cnxn:
        _cnxn = get_connection_general(_enviroment, _autocommit)
    try:
        with _cnxn.cursor() as _cur:
            _cur.execute("SELECT 1;")
        return True
    except pyodbc.DatabaseError as err:
        LOGGER.exception(err)
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def check_conection_unicon(_marca, _type, _cnxn=None, _autocommit=False):
    LOGGER.info(f"Check conexion a base de datos tipo: '{_type}' con marca: '{_marca.name}'.")
    if not _cnxn:
        _cnxn = get_connection_unicon(_marca, _type, _autocommit)
    try:
        with _cnxn.cursor() as _cur:
            _cur.execute("SELECT 1;")
        return True
    except pyodbc.DatabaseError as err:
        LOGGER.exception(err)
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def check_conection_sdc(_marca, _cnxn=None, _autocommit=False):
    return check_conection_unicon(_marca, "SDC", _cnxn, _autocommit)


def check_conection_cmd(_marca, _cnxn=None, _autocommit=False):
    return check_conection_unicon(_marca, "CMD", _cnxn, _autocommit)


def __query(_type, _cur, _sql, _params=None, _size=None):
    if _params is None:
        _cur.execute(_sql)
    else:
        _cur.execute(_sql, _params)

    if _size is None:
        _res = _cur.fetchall()
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(f"fetchall{_type} -> type response: {type(_res)}, length response: '{len(_res)}', sql: [{_sql}]")
    elif _size > 0:
        _res = _cur.fetchmany(_size)
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(f"fetchmany{_type} -> type response: {type(_res)}, length response: '{len(_res)}', size request: '{_size}'', sql: [{_sql}]")
    else:
        raise JobAnalyticsError(f"Incorrecto valor para _size: {_size}, tiene que ser mayor a cero.")
    return _res


def __query_val(_type, _cur, _sql, _params=None):
    if _params is None:
        _cur.execute(_sql)
    else:
        _cur.execute(_sql, _params)

    _res = _cur.fetchval()
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"fetchval{_type} -> type response: {type(_res)}, sql: [{_sql}]")
    return _res


def __query_one(_type, _cur, _sql, _params=None):
    if _params is None:
        _cur.execute(_sql)
    else:
        _cur.execute(_sql, _params)

    _res = _cur.fetchone()
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"fetchone{_type} -> type response: {type(_res)}, sql: [{_sql}]")
    return _res


def __dml(_type, _cur, _sql, _params=None):
    if _params is None:
        _cur.execute(_sql)
    else:
        _cur.execute(_sql, _params)

    _res = _cur.rowcount
    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug(f"rowcount{_type} -> type response: {type(_res)}, value: '{_res}', sql: [{_sql}]")
    return _res


def query(_cnxn, _sql, _params=None, _size=None):
    try:
        with _cnxn.cursor() as _cur:
            return __query('', _cur, _sql, _params, _size)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def query_val(_cnxn, _sql, _params=None):
    try:
        with _cnxn.cursor() as _cur:
            return __query_val('', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def query_one(_cnxn, _sql, _params=None):
    try:
        with _cnxn.cursor() as _cur:
            return __query_one('', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def dml(_cnxn, _sql, _params=None):
    try:
        with _cnxn.cursor() as _cur:
            return __dml('', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def query_tran(_cur, _sql, _params=None, _size=None):
    try:
        return __query('_tran', _cur, _sql, _params, _size)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def query_val_tran(_cur, _sql, _params=None):
    try:
        return __query_val('_tran', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def query_one_tran(_cur, _sql, _params=None):
    try:
        return __query_one('_tran', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def dml_tran(_cur, _sql, _params=None):
    try:
        return __dml('_tran', _cur, _sql, _params)
    except pyodbc.DatabaseError as err:
        LOGGER.warning(err)
        raise err
    except Exception as _ex:
        LOGGER.warning(_ex)
        raise _ex


def __get_info_basic_conn(cnxn):
    servername = query_val(cnxn, "SELECT @@SERVERNAME;")
    username = query_val(cnxn, "SELECT SUSER_SNAME();")
    databasename = query_val(cnxn, "SELECT DB_NAME();")
    spid = query_val(cnxn, "SELECT @@SPID;")
    version = query_val(cnxn, "SELECT @@VERSION;")
    return f"servername: '{servername}', username: '{username}', databasename: '{databasename}', sessionId: '{spid}', version: '{version}'"


def info_connection_default(_autocommit=False):
    LOGGER.info("Obteniendo informacion de conexion a base de datos tipo: 'DEFAULT'.")
    cnxn = get_connection_default(_autocommit)
    return __get_info_basic_conn(cnxn)


def info_connection_general(_enviroment, _autocommit=False):
    LOGGER.info(f"Obteniendo informacion de conexion a base de datos tipo: 'GENERAL' con entorno: '{_enviroment}'.")
    cnxn = get_connection_general(_enviroment, _autocommit)
    return __get_info_basic_conn(cnxn)


def info_connection_unicon(_marca, _type, _autocommit=False):
    LOGGER.info(f"Obteniendo informacion de conexion a base de datos tipo: '{_type}' con marca: '{_marca.name}'.")
    cnxn = get_connection_unicon(_marca, _type, _autocommit)
    return __get_info_basic_conn(cnxn)


def info_connection_sdc(_marca, _autocommit=False):
    return info_connection_unicon(_marca, "SDC", _autocommit)


def info_connection_cmd(_marca, _autocommit=False):
    return info_connection_unicon(_marca, "CMD", _autocommit)


def test_connection_default(_autocommit=False):
    try:
        LOGGER.info(f"Test finalizado, resultado de conexion a base de datos tipo: 'DEFAULT' -> \n{info_connection_default(_autocommit)}")
        return True
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def test_connection_general(_enviroment, _autocommit=False):
    try:
        LOGGER.info(f"Test finalizado, resultado de conexion a base de datos tipo: 'GENERAL' con entorno: '{_enviroment}' -> \n"
                    f"{info_connection_general(_enviroment, _autocommit)}")
        return True
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def test_connection_unicon(_marca, _type, _autocommit=False):
    try:
        LOGGER.info(f"Test finalizado, resultado de conexion a base de datos tipo: '{_type}' con marca: '{_marca.name}' -> \n"
                    f"{info_connection_unicon(_marca, _type, _autocommit)}")
        return True
    except Exception as _ex:
        LOGGER.exception(_ex)
    return False


def test_connection_sdc(_marca, _autocommit=False):
    return test_connection_unicon(_marca, "SDC", _autocommit)


def test_connection_cmd(_marca, _autocommit=False):
    return test_connection_unicon(_marca, "CMD", _autocommit)


def test_connection_all():
    test_connection_default()
    test_connection_general('VMX')
    for marca in [i for i in Marca]:
        test_connection_sdc(marca)
        test_connection_cmd(marca)


if __name__ == '__main__':
    LOGGER.info("Iniciando Test de conexion a base de datos.")
    try:
        test_connection_all()
    except Exception as ex:
        LOGGER.warning("Error Test de conexion a base de datos.")
        LOGGER.exception(ex)
    finally:
        LOGGER.info("Finalizando Test de conexion a base de datos.")
