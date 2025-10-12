"""Tax regime configurations for all countries."""

from .czechia import CZECHIA_FREELANCER, CZECHIA_SALARIED
from .germany import GERMANY_SALARIED
from .israel import ISRAEL_SALARIED

__all__ = [
    "GERMANY_SALARIED",
    "CZECHIA_SALARIED",
    "CZECHIA_FREELANCER",
    "ISRAEL_SALARIED",
]
