"""
Clase abstracta marcadora para cartas con tratamiento especial.

Sirve para que el resto del código pueda preguntar:
    if isinstance(carta, CartaEspecial):
        ...
sin tener que enumerar las tres subclases especiales.

También nos permite agregar comportamiento común si más adelante
hace falta (animaciones, mensajes en UI, etc.).
"""

from abc import ABC

from .carta import Carta
from .palo import Palo


class CartaEspecial(Carta, ABC):

    def __init__(self, numero: int, palo: Palo) -> None:
        super().__init__(numero, palo)
