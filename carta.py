"""
Clase base abstracta para cualquier carta del juego.
Permite que en el futuro se puedan agregar otros juegos (ej. CartaTruco)
compartiendo la misma estructura.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from .palo import Palo

if TYPE_CHECKING:
    from .decisor import Decisor


class Carta(ABC):

    def __init__(self, numero: int, palo: Palo) -> None:
        self._numero = numero
        self._palo = palo

    # --- Getters (equivalentes a getNumero / getPalo) -----------------

    def get_numero(self) -> int:
        return self._numero

    def get_palo(self) -> Palo:
        return self._palo

    # Propiedades de solo lectura para uso pythónico
    @property
    def numero(self) -> int:
        return self._numero

    @property
    def palo(self) -> Palo:
        return self._palo

    # --- Comportamiento polimórfico -----------------------------------

    @abstractmethod
    def get_valor(self) -> int:
        """Cada subclase decide cuántos puntos vale al final de la ronda."""
        ...

    def aplicar_efecto(
        self,
        ronda: Any,
        jugador: Any,
        decisor: Optional["Decisor"] = None,
    ) -> Optional[str]:
        """
        Efecto que se dispara al descartar la carta.

        Devuelve un string con un log human-readable del efecto, o None si
        la carta no tiene efecto. El que llame se encarga de imprimirlo
        (esto evita que los prints se cuelen en orden raro entre fases).

        Por defecto no hace nada — las subclases especiales lo sobrescriben.
        """
        return None

    # --- Representación -----------------------------------------------

    def __str__(self) -> str:
        return f"{self._numero} de {self._palo}"

    def __repr__(self) -> str:
        return self.__str__()
