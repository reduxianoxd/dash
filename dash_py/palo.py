"""
Los cuatro palos de la baraja española.
Usar Enum nos garantiza que es imposible escribir un palo "mal".
"""

from enum import Enum


class Palo(Enum):
    ORO = "oro"
    COPA = "copa"
    BASTO = "basto"
    ESPADA = "espada"

    def __str__(self) -> str:
        # Devuelve "oro", "copa", etc. para que se imprima lindo
        return self.value
