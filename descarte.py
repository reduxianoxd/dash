"""
Pila de descarte (cementerio): cartas que ya se jugaron, boca arriba.

La carta visible en la mesa es siempre la última que se tiró: el "tope".
El resto queda apilado debajo y normalmente no se mira, pero lo guardamos
por si más adelante hace falta para alguna regla (por ejemplo, mostrar
un historial de la ronda).
"""

from typing import List, Optional

from .carta import Carta


class Descarte:

    def __init__(self) -> None:
        self._cartas: List[Carta] = []

    def tirar(self, carta: Carta) -> None:
        """Apila una carta en el tope del descarte."""
        self._cartas.append(carta)

    def ver_tope(self) -> Optional[Carta]:
        """Devuelve la carta de arriba sin sacarla. None si está vacío."""
        if not self._cartas:
            return None
        return self._cartas[-1]

    def sacar_tope(self) -> Carta:
        """Saca y devuelve la carta de arriba. Raise si está vacío."""
        if not self._cartas:
            raise RuntimeError("El descarte esta vacio")
        return self._cartas.pop()

    def esta_vacio(self) -> bool:
        return len(self._cartas) == 0

    def tamano(self) -> int:
        return len(self._cartas)

    def __len__(self) -> int:
        return len(self._cartas)

    def __str__(self) -> str:
        tope = self.ver_tope()
        if tope is None:
            return "Descarte vacio"
        return f"Descarte (tope: {tope}, total: {self.tamano()})"

    def __repr__(self) -> str:
        return self.__str__()
