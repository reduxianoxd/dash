"""
La mano de un jugador: las cartas que tiene en juego.
Normalmente son 4, pero puede tener más por la penalización de pares mal cantados.
"""

from typing import List

from .carta import Carta


class Mano:

    def __init__(self) -> None:
        self._cartas: List[Carta] = []

    def agregar(self, carta: Carta) -> None:
        self._cartas.append(carta)

    def reemplazar(self, posicion: int, nueva: Carta) -> Carta:
        """
        Reemplaza la carta en la posición dada por una nueva.
        Devuelve la carta vieja (la que se va al descarte).
        """
        vieja = self._cartas[posicion]
        self._cartas[posicion] = nueva
        return vieja

    def obtener(self, posicion: int) -> Carta:
        return self._cartas[posicion]

    def remover(self, posicion: int) -> Carta:
        return self._cartas.pop(posicion)

    def tamano(self) -> int:
        return len(self._cartas)

    def esta_vacia(self) -> bool:
        return len(self._cartas) == 0

    def calcular_puntaje(self) -> int:
        """
        Suma los valores de todas las cartas en la mano.
        Se usa al final de la ronda para calcular el puntaje.
        """
        return sum(c.get_valor() for c in self._cartas)

    def get_cartas(self) -> List[Carta]:
        """Devuelve una copia de las cartas (para evitar que se modifiquen desde afuera)."""
        return list(self._cartas)

    # Soporte pythónico: len(mano), for c in mano, etc.
    def __len__(self) -> int:
        return len(self._cartas)

    def __iter__(self):
        return iter(list(self._cartas))

    def __str__(self) -> str:
        return "[" + ", ".join(str(c) for c in self._cartas) + "]"

    def __repr__(self) -> str:
        return self.__str__()
