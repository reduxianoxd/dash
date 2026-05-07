"""
Pila de cartas boca abajo desde la que se roba.

Internamente usa una lista que se comporta como pila (Stack):
la "carta superior" es siempre la última agregada.
"""

from __future__ import annotations

import random
from typing import List, TYPE_CHECKING

from .carta import Carta
from .carta_caballo import CartaCaballo
from .carta_diez import CartaDiez
from .carta_doce_especial import CartaDoceEspecial
from .carta_normal import CartaNormal
from .palo import Palo

if TYPE_CHECKING:
    from .descarte import Descarte


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
    # Reciclado: cuando el mazo se queda vacío, el descarte se mezcla
    # de nuevo (menos el tope, que sigue boca arriba sobre la mesa).
    # ------------------------------------------------------------------

    def recargar_desde_descarte(self, descarte: "Descarte") -> int:
        """
        Toma todas las cartas del descarte EXCEPTO el tope (la carta
        boca arriba sobre la mesa), las mezcla y las apila como nuevo
        contenido del mazo. Devuelve cuántas cartas se reciclaron.

        Las cartas que están en las manos de los jugadores no se tocan.
        """
        # Si el descarte tiene 0 o 1 carta, no hay nada que reciclar
        # (con 1 carta, esa única carta es el tope y se queda en su lugar).
        if descarte.tamano() <= 1:
            return 0

        tope = descarte.sacar_tope()  # lo guardamos para devolverlo
        recicladas: List[Carta] = []
        while not descarte.esta_vacio():
            recicladas.append(descarte.sacar_tope())
        descarte.tirar(tope)  # vuelve a su lugar boca arriba

        random.shuffle(recicladas)
        self._cartas.extend(recicladas)
        return len(recicladas)

    # ------------------------------------------------------------------
    # Fábrica
    # ------------------------------------------------------------------

    @staticmethod
    def crear_mazo_espanol() -> "Mazo":
        """
        Crea el mazo de Dash: 48 cartas (variante de baraja española en
        la que SI están el 8 y el 9, además del 1 al 7, 10, 11 y 12) en
        los cuatro palos (oro, copa, basto, espada).

        Reglas de tipos:
          - 11 (Caballo)          -> CartaCaballo (vale 11, efecto especial)
          - 10                     -> CartaDiez    (vale 10, efecto especial)
          - 12 de basto/espada     -> CartaDoceEspecial (vale 0)
          - 12 de oro/copa         -> CartaNormal (vale 12)
          - resto (1..9)           -> CartaNormal (vale su número)
        """
        mazo = Mazo()
        numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

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
