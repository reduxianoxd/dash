"""
Paquete dash_py: migración a Python del proyecto Java `dash`.

Mantiene la misma estructura (un archivo por clase) y los mismos nombres
en español que la versión original.
"""

from .palo import Palo
from .carta import Carta
from .carta_normal import CartaNormal
from .carta_especial import CartaEspecial
from .carta_caballo import CartaCaballo
from .carta_diez import CartaDiez
from .carta_doce_especial import CartaDoceEspecial
from .mano import Mano
from .mazo import Mazo
from .descarte import Descarte
from .jugador import Jugador
from .decisor import Decisor, DecisorSimulador, DecisorMixto
from .decisor_consola import DecisorConsola
from .ronda import Ronda
from .partida import Partida

__all__ = [
    "Palo",
    "Carta",
    "CartaNormal",
    "CartaEspecial",
    "CartaCaballo",
    "CartaDiez",
    "CartaDoceEspecial",
    "Mano",
    "Mazo",
    "Descarte",
    "Jugador",
    "Decisor",
    "DecisorSimulador",
    "DecisorMixto",
    "DecisorConsola",
    "Ronda",
    "Partida",
]
