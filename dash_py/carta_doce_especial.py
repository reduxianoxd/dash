"""
El 12 de basto y el 12 de espada valen 0 puntos.
Son las cartas más valiosas del juego (cuanto menos puntos, mejor).

No tiene efecto al descartarse: su "especialidad" es solo el valor.

Importante: solo se puede instanciar con palo BASTO o ESPADA.
Si se intenta con ORO o COPA, lanza ValueError.
"""

from .carta_especial import CartaEspecial
from .palo import Palo


class CartaDoceEspecial(CartaEspecial):

    def __init__(self, palo: Palo) -> None:
        if palo is not Palo.BASTO and palo is not Palo.ESPADA:
            raise ValueError(
                f"CartaDoceEspecial solo se permite en BASTO o ESPADA. Recibido: {palo}"
            )
        super().__init__(12, palo)

    def get_valor(self) -> int:
        return 0

    def __str__(self) -> str:
        return f"{self._numero} de {self._palo} (especial, vale 0)"
