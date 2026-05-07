"""
DecisorConsola: implementación del Protocol `Decisor` que pregunta por
consola (input) qué hacer en cada decisión.

Pensado para jugar a mano contra simuladores. Muestra las cartas que el
jugador conoce con su valor; las que no conoce las muestra como "???".
Tiene una opción de debug para mostrarlas todas.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .carta import Carta
from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo


class DecisorConsola:

    def __init__(self, mostrar_mano_completa: bool = False) -> None:
        # Si está en True, además del "???" se imprime entre paréntesis
        # la carta real (útil para debug, no para jugar realmente).
        self.mostrar_mano_completa = mostrar_mano_completa

    # --- Helpers -----------------------------------------------------

    def _imprimir_mano(self, jugador: Jugador) -> None:
        print(f"\nMano de {jugador.get_nombre()} (lo que conoce):")
        mano = jugador.get_mano()
        for i in range(mano.tamano()):
            carta = mano.obtener(i)
            if jugador.conoce_carta(i):
                print(f"  pos {i}: {carta}")
            elif self.mostrar_mano_completa:
                print(f"  pos {i}: ???   (debug: {carta})")
            else:
                print(f"  pos {i}: ???")

    def _pedir_int(
        self,
        prompt: str,
        min_v: int,
        max_v: int,
    ) -> int:
        while True:
            txt = input(f"{prompt} [{min_v}..{max_v}]: ").strip()
            try:
                v = int(txt)
            except ValueError:
                print("  no es un número válido, probá de nuevo.")
                continue
            if min_v <= v <= max_v:
                return v
            print(f"  fuera de rango, tiene que estar entre {min_v} y {max_v}.")

    def _pedir_si_no(self, prompt: str) -> bool:
        while True:
            txt = input(f"{prompt} (s/n): ").strip().lower()
            if txt in ("s", "si", "sí", "y", "yes"):
                return True
            if txt in ("n", "no"):
                return False
            print("  contestá s o n.")

    # --- Protocol Decisor --------------------------------------------

    def decidir_proxima_tirada(
        self,
        jugador: Jugador,
        descarte: Descarte,
    ) -> Optional[int]:
        """
        Le pregunta al humano si quiere intentar tirar alguna carta.
        Puede tirar una posición que NO conoce (bluff): si la carta
        no matchea el tope, se lleva 1 carta de penalización del mazo.

        Prompt único: posición a tirar, o ENTER para pasar.
        """
        tope = descarte.ver_tope()
        if tope is None or jugador.get_mano().tamano() == 0:
            return None

        print(f"\n>>> ¿Querés intentar tirar alguna carta? (tope: {tope})")
        self._imprimir_mano(jugador)
        while True:
            txt = input(
                f"  Posición a tirar [0..{jugador.get_mano().tamano() - 1}] "
                "o ENTER para pasar: "
            ).strip()
            if txt == "":
                return None
            try:
                pos = int(txt)
            except ValueError:
                print("  no es un número, probá de nuevo.")
                continue
            if 0 <= pos < jugador.get_mano().tamano():
                return pos
            print(
                f"  fuera de rango (0..{jugador.get_mano().tamano() - 1}), "
                "probá de nuevo."
            )

    def decidir_inicio_fase2(
        self,
        jugador: Jugador,
        mazo: Mazo,
        descarte: Descarte,
    ) -> Tuple[str, Optional[int]]:
        """
        Antes de levantar del mazo: el jugador puede tomar el tope del
        descarte y cambiarlo por una de su mano (sin disparar efecto),
        o seguir con el flujo de levantar del mazo.
        """
        print(f"\n>>> Inicio de fase 2 de {jugador.get_nombre()}.")
        print(f"Tope del descarte: {descarte.ver_tope()}")
        print(f"Mazo: {mazo.tamano()} cartas restantes.")
        self._imprimir_mano(jugador)

        tope = descarte.ver_tope()
        if tope is None or jugador.get_mano().tamano() == 0:
            # No tiene sentido ofrecer "tomar" sin tope o sin mano.
            print("  (no hay opción de tomar del descarte: paso a levantar del mazo)")
            return ("levantar", None)

        while True:
            txt = input(
                "¿(t)omar el tope del descarte y cambiarlo por una carta tuya, "
                "o (l)evantar del mazo? [t/l]: "
            ).strip().lower()
            if txt in ("l", "levantar", "mazo"):
                return ("levantar", None)
            if txt in ("t", "tomar", "descarte"):
                pos = self._pedir_int(
                    "¿qué posición tuya querés cambiar por el tope del descarte?",
                    0,
                    jugador.get_mano().tamano() - 1,
                )
                return ("tomar_descarte", pos)
            print("  respondé 't' o 'l'.")

    def decidir_swap(
        self,
        jugador: Jugador,
        levantada: Carta,
        mazo: Mazo,
        descarte: Descarte,
    ) -> Tuple[str, Optional[int]]:
        print(f"\n>>> Turno de {jugador.get_nombre()}.")
        print(f"Tope del descarte: {descarte.ver_tope()}")
        print(f"Mazo: {mazo.tamano()} cartas restantes.")
        self._imprimir_mano(jugador)
        print(f"\nLevantaste del mazo: {levantada} (vale {levantada.get_valor()})")

        if jugador.get_mano().tamano() == 0:
            print("  (no tenés cartas en la mano: la única opción es tirarla)")
            input("  [ENTER para continuar]")
            return ("tirar", None)

        while True:
            txt = input(
                "¿Qué hacés? (t)irar al descarte / (c)ambiar por una carta tuya: "
            ).strip().lower()
            if txt in ("t", "tirar"):
                return ("tirar", None)
            if txt in ("c", "cambiar"):
                pos = self._pedir_int(
                    "¿qué posición tuya querés cambiar?",
                    0,
                    jugador.get_mano().tamano() - 1,
                )
                return ("cambiar", pos)
            print("  respondé 't' o 'c'.")

    def querer_cantar(self, jugador: Jugador) -> bool:
        print(f"\n[Final del turno de {jugador.get_nombre()}]")
        self._imprimir_mano(jugador)
        return self._pedir_si_no("¿Cantás DASH para cortar la ronda?")

    def elegir_pos_para_diez(self, jugador: Jugador) -> Optional[int]:
        print(
            f"\n[Efecto Diez] {jugador.get_nombre()}, podés mirar una carta "
            "de tu mano que todavía no conozcas."
        )
        self._imprimir_mano(jugador)
        if jugador.get_mano().tamano() == 0:
            return None
        if not self._pedir_si_no("¿Querés usar el efecto?"):
            return None
        return self._pedir_int(
            "¿qué posición querés mirar?",
            0,
            jugador.get_mano().tamano() - 1,
        )

    def elegir_caballo(
        self,
        jugador: Jugador,
        otros: List[Jugador],
    ) -> Optional[Tuple[Jugador, int, int]]:
        print(
            f"\n[Efecto Caballo] {jugador.get_nombre()}, podés intercambiar "
            "una carta tuya con la de cualquier otro jugador."
        )
        if not otros:
            return None
        if not self._pedir_si_no("¿Querés usar el efecto?"):
            return None

        print("\nOtros jugadores:")
        for i, o in enumerate(otros):
            print(f"  {i}: {o.get_nombre()}  (mano de {o.get_mano().tamano()} cartas)")

        idx = self._pedir_int(
            "¿con qué jugador intercambiás?", 0, len(otros) - 1
        )
        otro = otros[idx]

        if otro.get_mano().tamano() == 0:
            print(f"  {otro.get_nombre()} no tiene cartas, no se puede.")
            return None

        otro_pos = self._pedir_int(
            f"¿qué posición de {otro.get_nombre()}?",
            0,
            otro.get_mano().tamano() - 1,
        )
        propia_pos = self._pedir_int(
            "¿qué posición tuya?",
            0,
            jugador.get_mano().tamano() - 1,
        )
        return (otro, otro_pos, propia_pos)
