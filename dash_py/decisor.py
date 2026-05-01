"""
Decisor: agrupa todas las decisiones que toma "alguien" durante la partida.

La idea es que la lógica del juego (Ronda, Carta) le pregunte al Decisor
qué hacer cuando hace falta una decisión humana / de IA:

  - decidir_swap:           qué hacer con la carta levantada en fase 2.
  - querer_cantar:          si canta Dash al final del turno propio.
  - elegir_pos_para_diez:   qué carta propia mira al disparar el Diez.
  - elegir_caballo:         con qué jugador / posiciones intercambia el Caballo.

Implementaciones concretas:
  - DecisorSimulador: la heurística que usa el tester.
  - (futuro) DecisorHumano que pregunte por consola.
  - (futuro) DecisorIA con estrategias más finas.
"""

from __future__ import annotations

from typing import List, Optional, Protocol, Tuple, runtime_checkable

from .carta import Carta
from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo


# Acción que se devuelve en fase 2: ("tirar", None) o ("cambiar", posicion)
AccionSwap = Tuple[str, Optional[int]]

# Decisión del Caballo: con quién y qué posiciones intercambiar.
# (otro_jugador, posicion_del_otro, posicion_propia) o None para no usar el efecto.
DecisionCaballo = Optional[Tuple[Jugador, int, int]]


@runtime_checkable
class Decisor(Protocol):

    def decidir_swap(
        self,
        jugador: Jugador,
        levantada: Carta,
        mazo: Mazo,
        descarte: Descarte,
    ) -> AccionSwap: ...

    def querer_cantar(self, jugador: Jugador) -> bool: ...

    def elegir_pos_para_diez(self, jugador: Jugador) -> Optional[int]: ...

    def elegir_caballo(
        self,
        jugador: Jugador,
        otros: List[Jugador],
    ) -> DecisionCaballo: ...


# --------------------------------------------------------------------
# Implementación por defecto: heurística sencilla del simulador
# --------------------------------------------------------------------

UMBRAL_DASH_DEFAULT = 10


class DecisorSimulador:
    """
    Estrategia simple para correr partidas automáticas:

    - decidir_swap: si la levantada vale menos que la peor de la mano, cambia.
    - querer_cantar: canta si el puntaje de la mano es <= umbral.
    - elegir_pos_para_diez: la primera posición que el jugador todavía no haya visto;
      si las vio todas, ninguna (devuelve None).
    - elegir_caballo: intercambia su pos 0 con la pos 0 del primer otro jugador.
    """

    def __init__(self, umbral_dash: int = UMBRAL_DASH_DEFAULT) -> None:
        self.umbral_dash = umbral_dash

    # ---- Fase 2 -----------------------------------------------------
    def decidir_swap(
        self,
        jugador: Jugador,
        levantada: Carta,
        mazo: Mazo,
        descarte: Descarte,
    ) -> AccionSwap:
        mano = jugador.get_mano()
        peor_pos = -1
        peor_valor = -1
        for i in range(mano.tamano()):
            v = mano.obtener(i).get_valor()
            if v > peor_valor:
                peor_valor = v
                peor_pos = i

        if peor_pos != -1 and levantada.get_valor() < peor_valor:
            return ("cambiar", peor_pos)
        return ("tirar", None)

    # ---- Fase 3 -----------------------------------------------------
    def querer_cantar(self, jugador: Jugador) -> bool:
        return jugador.get_mano().calcular_puntaje() <= self.umbral_dash

    # ---- Efecto del Diez --------------------------------------------
    def elegir_pos_para_diez(self, jugador: Jugador) -> Optional[int]:
        mano = jugador.get_mano()
        for i in range(mano.tamano()):
            if not jugador.conoce_carta(i):
                return i
        return None  # ya vio todas, no hay nada nuevo que mirar

    # ---- Efecto del Caballo -----------------------------------------
    def elegir_caballo(
        self,
        jugador: Jugador,
        otros: List[Jugador],
    ) -> DecisionCaballo:
        if not otros:
            return None
        objetivo = otros[0]
        if objetivo.get_mano().tamano() == 0 or jugador.get_mano().tamano() == 0:
            return None
        return (objetivo, 0, 0)
