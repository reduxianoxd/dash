"""
El Caballo (11) tiene efecto al descartarse:
permite intercambiar una carta del jugador con la de cualquier otro jugador.
Su valor en puntos es 11 (igual a su número).
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .carta_especial import CartaEspecial
from .palo import Palo

if TYPE_CHECKING:
    from .decisor import Decisor


class CartaCaballo(CartaEspecial):

    def __init__(self, palo: Palo) -> None:
        super().__init__(11, palo)

    def get_valor(self) -> int:
        return 11

    def aplicar_efecto(
        self,
        ronda: Any,
        jugador: Any,
        decisor: Optional["Decisor"] = None,
    ) -> Optional[str]:
        if jugador is None or ronda is None:
            return "[Efecto Caballo] (sin contexto) — no se puede aplicar"
        if decisor is None:
            return (
                "[Efecto Caballo] (sin decisor) — el jugador podria "
                "intercambiar una carta con otro jugador"
            )

        # `ronda.jugadores` devuelve una copia con todos los jugadores
        # de la mesa. Filtramos al protagonista para pasarle al decisor
        # solo los oponentes.
        otros = [j for j in ronda.jugadores if j is not jugador]
        decision = decisor.elegir_caballo(jugador, otros)
        if decision is None:
            return f"[Efecto Caballo] {jugador.get_nombre()} elige no intercambiar"

        otro, otro_pos, propia_pos = decision

        # Validaciones rápidas
        if otro is jugador:
            return "[Efecto Caballo] decisión inválida: el otro es uno mismo"
        if propia_pos < 0 or propia_pos >= jugador.get_mano().tamano():
            return f"[Efecto Caballo] decisión inválida: propia_pos={propia_pos}"
        if otro_pos < 0 or otro_pos >= otro.get_mano().tamano():
            return f"[Efecto Caballo] decisión inválida: otro_pos={otro_pos}"

        # Hacemos el swap usando Mano.reemplazar (que devuelve la vieja).
        carta_propia = jugador.get_mano().obtener(propia_pos)
        carta_otro = otro.get_mano().obtener(otro_pos)

        jugador.get_mano().reemplazar(propia_pos, carta_otro)
        otro.get_mano().reemplazar(otro_pos, carta_propia)

        # Después del swap, lo que cada jugador "conocía" sobre las cartas
        # intercambiadas se invierte: jugador deja de conocer la suya
        # vieja (ya no la tiene) y arranca sin saber la nueva. Lo mismo
        # del otro lado.
        jugador.olvidar_carta(carta_propia)
        otro.olvidar_carta(carta_otro)

        return (
            f"[Efecto Caballo] {jugador.get_nombre()} intercambia su pos "
            f"{propia_pos} ({carta_propia}) con la pos {otro_pos} de "
            f"{otro.get_nombre()} ({carta_otro})"
        )
