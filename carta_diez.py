"""
El Diez (10) tiene efecto al descartarse:
permite al jugador mirar una de sus propias cartas que aún no conoce.
Su valor en puntos es 10.
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .carta_especial import CartaEspecial
from .palo import Palo

if TYPE_CHECKING:
    from .decisor import Decisor


class CartaDiez(CartaEspecial):

    def __init__(self, palo: Palo) -> None:
        super().__init__(10, palo)

    def get_valor(self) -> int:
        return 10

    def aplicar_efecto(
        self,
        ronda: Any,
        jugador: Any,
        decisor: Optional["Decisor"] = None,
    ) -> Optional[str]:
        if jugador is None:
            return "[Efecto Diez] (sin jugador) — no se aplica"
        if decisor is None:
            return "[Efecto Diez] (sin decisor) — el jugador podria mirar una carta propia"

        pos = decisor.elegir_pos_para_diez(jugador)
        if pos is None:
            return f"[Efecto Diez] {jugador.get_nombre()} elige no mirar (o ya vio todas)"

        # ver_carta agrega la carta al set de vistas del jugador y la devuelve
        carta_vista = jugador.ver_carta(pos)
        return (
            f"[Efecto Diez] {jugador.get_nombre()} mira su pos {pos}: "
            f"{carta_vista}"
        )
