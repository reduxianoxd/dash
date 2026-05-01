"""
Una ronda completa del juego.

Orquesta el flujo:
  - turno por turno entre los jugadores,
  - cada turno tiene fase 1 (tirar matches), fase 2 (levantar y decidir)
    y fase 3 opcional (cantar "Dash" para cortar al final del turno propio),
  - cuando alguien canta Dash, los demás jugadores juegan UN turno más
    cada uno y la ronda se cierra revelando manos y sumando puntajes.

No hay penalización por cantar mal: cada jugador suma a su puntaje
acumulado el valor real de su mano. La gracia está en jugársela cuando
no conocés todas tus cartas.

Las decisiones que toma cada jugador (qué hacer con la levantada, si
canta Dash, qué carta mira con el Diez, qué intercambia con el Caballo)
se delegan en un objeto Decisor (ver `decisor.py`).
"""

from __future__ import annotations

from typing import List, Optional

from .decisor import Decisor
from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo


class Ronda:

    def __init__(
        self,
        jugadores: List[Jugador],
        mazo: Mazo,
        descarte: Descarte,
    ) -> None:
        if len(jugadores) < 2:
            raise ValueError("Se necesitan al menos 2 jugadores para una ronda.")
        self._jugadores = list(jugadores)
        self._mazo = mazo
        self._descarte = descarte
        self._indice_actual = 0
        self._dash_cantado_por: Optional[Jugador] = None
        # Cuántos turnos faltan tras el canto antes de cerrar la ronda.
        # Se inicializa al cantar: cada otro jugador juega un turno más.
        self._turnos_post_dash_restantes = 0
        self._terminada = False

    # --- Estado público ----------------------------------------------

    @property
    def jugadores(self) -> List[Jugador]:
        return list(self._jugadores)

    @property
    def mazo(self) -> Mazo:
        return self._mazo

    @property
    def descarte(self) -> Descarte:
        return self._descarte

    @property
    def dash_cantado_por(self) -> Optional[Jugador]:
        return self._dash_cantado_por

    def jugador_actual(self) -> Jugador:
        return self._jugadores[self._indice_actual]

    def esta_terminada(self) -> bool:
        return self._terminada

    # --- Núcleo: jugar un turno --------------------------------------

    def jugar_turno(self, decisor: Decisor) -> dict:
        """
        Juega un turno del jugador actual y devuelve un dict con el log
        de lo que pasó (para imprimirlo desde afuera).

        Estructura del turno:
          Fase 1: tira todos los matches que tenga (con sus efectos).
          Fase 2: obligatorio levantar del mazo y decidir tirar / cambiar
                  (la carta que va al descarte dispara su efecto).
          Fase 3: si nadie cantó Dash todavía, este jugador puede cantarlo.
        """
        if self._terminada:
            raise RuntimeError("La ronda ya termino.")

        jugador = self.jugador_actual()
        log: dict = {
            "jugador": jugador,
            "tope_inicial": self._descarte.ver_tope(),
            "mano_inicial": jugador.get_mano().get_cartas(),
            "fase1_tiradas": [],
            "fase1_efectos": [],
            "fase2": None,
            "fase2_efecto": None,
            "canto_dash": False,
        }

        # ---- Fase 1: tirar todos los matches --------------------------
        # Lo hacemos de a una para capturar el log del efecto en orden.
        while True:
            posiciones = jugador.posiciones_que_coinciden(self._descarte)
            if not posiciones:
                break
            pos = posiciones[0]
            carta = jugador.descartar_carta(pos)  # saca de la mano + olvida
            self._descarte.tirar(carta)
            efecto_log = carta.aplicar_efecto(self, jugador, decisor=decisor)
            log["fase1_tiradas"].append(carta)
            if efecto_log:
                log["fase1_efectos"].append(efecto_log)

        # ---- Fase 2: obligatorio levantar (si queda mazo) -------------
        if self._mazo.esta_vacio():
            log["fase2"] = {"accion": "mazo_vacio"}
        else:
            levantada = self._mazo.robar()
            accion, pos = decisor.decidir_swap(
                jugador, levantada, self._mazo, self._descarte
            )
            if accion == "tirar":
                self._descarte.tirar(levantada)
                efecto_log = levantada.aplicar_efecto(self, jugador, decisor=decisor)
                log["fase2"] = {
                    "accion": "tirar",
                    "levantada": levantada,
                    "al_descarte": levantada,
                }
                log["fase2_efecto"] = efecto_log
            elif accion == "cambiar":
                if pos is None:
                    raise ValueError("Acción 'cambiar' requiere una posición.")
                vieja = jugador.get_mano().reemplazar(pos, levantada)
                jugador.olvidar_carta(vieja)
                self._descarte.tirar(vieja)
                efecto_log = vieja.aplicar_efecto(self, jugador, decisor=decisor)
                log["fase2"] = {
                    "accion": "cambiar",
                    "levantada": levantada,
                    "posicion": pos,
                    "al_descarte": vieja,
                }
                log["fase2_efecto"] = efecto_log
            else:
                raise ValueError(f"Acción desconocida: {accion}")

        # ---- Fase 3: opcional cantar Dash ---------------------------
        canto_recien = False
        if self._dash_cantado_por is None and decisor.querer_cantar(jugador):
            self._dash_cantado_por = jugador
            self._turnos_post_dash_restantes = len(self._jugadores) - 1
            log["canto_dash"] = True
            canto_recien = True

        # ---- Avanzar al siguiente jugador y chequear cierre ---------
        self._indice_actual = (self._indice_actual + 1) % len(self._jugadores)

        if self._dash_cantado_por is not None and not canto_recien:
            self._turnos_post_dash_restantes -= 1
            if self._turnos_post_dash_restantes <= 0:
                self._cerrar()

        return log

    # --- Cierre ------------------------------------------------------

    def _cerrar(self) -> None:
        """Suma el puntaje de la mano de cada jugador a su acumulado y marca terminada."""
        for j in self._jugadores:
            j.sumar_puntaje(j.get_mano().calcular_puntaje())
        self._terminada = True

    def forzar_cierre(self) -> None:
        """Cierre manual (por ejemplo si se acaba el mazo y se quiere cortar)."""
        self._cerrar()

    # --- Resultado ---------------------------------------------------

    def ganador_de_la_ronda(self) -> Optional[Jugador]:
        """
        El de menor puntaje EN LA MANO al cierre. None si todavía no terminó.
        En empates devuelve el primero en orden de jugadores.
        """
        if not self._terminada:
            return None
        mejor: Optional[Jugador] = None
        mejor_puntaje = 10**9
        for j in self._jugadores:
            p = j.get_mano().calcular_puntaje()
            if p < mejor_puntaje:
                mejor_puntaje = p
                mejor = j
        return mejor
