"""
Pila de cartas boca abajo desde la que se roba.

Internamente usa una lista que se comporta como pila (Stack):
la "carta superior" es siempre la última agregada.
"""

from __future__ import annotations

import random
from typing import List

from .carta import Carta
from .carta_caballo import CartaCaballo
from .carta_diez import CartaDiez
from .carta_doce_especial import CartaDoceEspecial
from .carta_normal import CartaNormal
from .palo import Palo


class Mazo:

    def __init__(self) -> None:
        self._cartas: List[Carta] = []

    def mezclar(self) -> None:
        random.shuffle(self._cartas)

    def robar(self) -> Carta:
        if not self._cartas:
            raise RuntimeError("El mazo esta vacio")
        return self._cartas.pop()

    def esta_vacio(self) -> bool:
        return len(self._cartas) == 0

    def tamano(self) -> int:
        return len(self._cartas)

    def __len__(self) -> int:
        return len(self._cartas)

    # ------------------------------------------------------------------
    # Fábrica
    # ------------------------------------------------------------------

    @staticmethod
    def crear_mazo_espanol() -> "Mazo":
        """
        Crea un mazo espanol completo (40 cartas) con las subclases
        correctas de Carta segun el numero y el palo.

        La baraja espanola tiene 40 cartas: numeros 1, 2, 3, 4, 5, 6, 7, 10, 11 y 12
        en los 4 palos (no hay 8 ni 9).

        Reglas:
          - 11 (Caballo)         -> CartaCaballo
          - 10                    -> CartaDiez
          - 12 de basto/espada    -> CartaDoceEspecial (vale 0)
          - 12 de oro/copa        -> CartaNormal (vale 12)
          - resto (1..7)          -> CartaNormal
        """
        mazo = Mazo()
        numeros = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

        for palo in Palo:
            for numero in numeros:
                if numero == 11:
                    carta: Carta = CartaCaballo(palo)
                elif numero == 10:
                    carta = CartaDiez(palo)
                elif numero == 12 and (palo is Palo.BASTO or palo is Palo.ESPADA):
                    carta = CartaDoceEspecial(palo)
                else:
                    carta = CartaNormal(numero, palo)
                mazo._cartas.append(carta)
        return mazo
