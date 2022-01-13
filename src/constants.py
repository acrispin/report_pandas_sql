from enum import Enum


class JobAnalytics(Enum):
    COMP_FINANCIERO = 1
    PRECIO_UNACEM = 2
    COSTO = 3
    PROYECCION = 4
    TEST = -1


class FrecuenciaUnidad(Enum):
    SEGUNDOS = "s"
    MINUTOS = "m"
    HORAS = "h"


class Marca(Enum):
    UNICON = 1
    CONCREMAX = 2
