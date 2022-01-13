import requests
from decouple import config
# import json
from .log import setup_custom_logger



LOGGER = setup_custom_logger(__name__)

URL_SERVIDOR_BASE = config('MULESOFT_URL_SERVIDOR_BASE', default='')
AUTH_USERNAME = config('MULESOFT_ACCESS_AUTH_USERNAME', default='')
AUTH_PASSWORD = config('MULESOFT_ACCESS_AUTH_PASSWORD', default='')
REQUEST_TIMEOUT = config('MULESOFT_REQUEST_TIMEOUT', default=30, cast=int)

PATH_COMP_FINANCIERO = config('MULESOFT_PATH_COMP_FINANCIERO', default='')
PATH_PRECIO_UNACEM = config('MULESOFT_PATH_PRECIO_UNACEM', default='')
PATH_COSTO = config('MULESOFT_PATH_COSTO', default='')
PATH_PROYECCION = config('MULESOFT_PATH_PROYECCION', default='')

BASIC_HEADERS = {
    'Content-Type': 'application/json'
}


def post_common(_json, _url):
    res = None
    try:
        res = requests.request(
            "POST",
            _url,
            auth=(AUTH_USERNAME, AUTH_PASSWORD),
            headers=BASIC_HEADERS,
            # data=_json.encode(),
            # data=_json,
            json=_json,
            timeout=REQUEST_TIMEOUT)
        LOGGER.info(f"status_code: {res.status_code}, total_seconds: '{res.elapsed.total_seconds()}', headers: {res.headers}")
        # res.raise_for_status()
        # return json.loads(res.text)
        return res.json()
    except Exception as ex:
        LOGGER.exception(ex)
        return res.text


def post_comp_financiero(_json):
    _url = f"{URL_SERVIDOR_BASE}{PATH_COMP_FINANCIERO}"
    LOGGER.info(f"post_comp_financiero url: {_url}")
    return post_common(_json, _url)


def post_precio_unacem(_json):
    _url = f"{URL_SERVIDOR_BASE}{PATH_PRECIO_UNACEM}"
    LOGGER.info(f"post_precio_unacem url: {_url}")
    return post_common(_json, _url)


def post_costo(_json):
    _url = f"{URL_SERVIDOR_BASE}{PATH_COSTO}"
    LOGGER.info(f"post_costo url: {_url}")
    return post_common(_json, _url)


def post_proyeccion(_json):
    _url = f"{URL_SERVIDOR_BASE}{PATH_PROYECCION}"
    LOGGER.info(f"post_proyeccion url: {_url}")
    return post_common(_json, _url)
