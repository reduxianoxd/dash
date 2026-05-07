"""
Carta común sin efecto especial.
Su valor es simplemente su número.
"""

from .carta import Carta
from .palo import Palo


class CartaNormal(Carta):

    def __init__(self, numero: int, palo: Palo) -> None:
        super().__init__(numero, palo)

    def get_valor(self) -> int:
        return self._numero
