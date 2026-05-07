"""
Partida: una serie de rondas de Dash entre los mismos jugadores.

Cada ronda se arma con un mazo nuevo, el reparto y el descarte inicial.
Al cerrarse, los puntajes en mano se suman al acumulado de cada jugador.
La partida termina cuando alguien llega o supera el límite (ej. 100).
Gana el de MENOR puntaje acumulado al cierre.

El "primer jugador" de cada ronda rota: en la ronda 1 arranca jugadores[0],
en la ronda 2 jugadores[1], y así. Esto reparte equitativamente la
desventaja/ventaja de jugar primero.
"""

from __future__ import annotations

from typing import List, Optional

from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo
from .ronda import Ronda


LIMITE_DEFAULT = 100


class Partida:

    def __init__(
        self,
        jugadores: List[Jugador],
        limite: int = LIMITE_DEFAULT,
        cartas_iniciales_vistas: int = 2,
    ) -> None:
        if len(jugadores) < 2:
            raise ValueError("Se necesitan al menos 2 jugadores.")
        self._jugadores = list(jugadores)
        self._limite = limite
        self._cartas_iniciales_vistas = cartas_iniciales_vistas
        self._indice_inicial = 0   # índice del primer jugador de la próxima ronda
        self._numero_ronda = 0     # rondas ya cerradas
        self._terminada = False

    # --- Estado público ----------------------------------------------

    @property
    def jugadores(self) -> List[Jugador]:
        return list(self._jugadores)

    @property
    def limite(self) -> int:
        return self._limite

    @property
    def numero_ronda(self) -> int:
        return self._numero_ronda

    @property
    def terminada(self) -> bool:
        return self._terminada

    @property
    def proxima_orden(self) -> List[Jugador]:
        """Orden en que jugarán los jugadores en la próxima ronda."""
        n = len(self._jugadores)
        return [
            self._jugadores[(self._indice_inicial + i) % n]
            for i in range(n)
        ]

    # --- Construir y cerrar una ronda --------------------------------

    def nueva_ronda(self) -> Ronda:
        """
        Prepara una ronda lista para jugar:
          - mazo nuevo de 48 cartas, mezclado.
          - reparto de 4 cartas a cada jugador (orden rotado según el
            índice inicial de esta partida).
          - cada jugador "ve" sus N primeras cartas (default 2).
          - una carta del mazo arranca el descarte boca arriba.
        Devuelve la Ronda creada (todavía sin turnos jugados).
        """
        if self._terminada:
            raise RuntimeError("La partida ya termino.")

        # 1) Limpiar el estado de los jugadores que pueda quedar de la
        #    ronda anterior (mano + cartas vistas).
        for j in self._jugadores:
            mano = j.get_mano()
            while not mano.esta_vacia():
                mano.remover(0)
            j.olvidar_todo()

        # 2) Mazo nuevo
        mazo = Mazo.crear_mazo_espanol()
        mazo.mezclar()

        # 3) Orden de jugadores (rotado)
        orden = self.proxima_orden

        # 4) Reparto: 4 cartas a cada uno, una por una
        for _vuelta in range(4):
            for j in orden:
                j.recibir_carta(mazo.robar())

        # 5) Cada jugador ve sus primeras N cartas
        for j in orden:
            j.marcar_iniciales_vistas(self._cartas_iniciales_vistas)

        # 6) Carta inicial al descarte
        descarte = Descarte()
        descarte.tirar(mazo.robar())

        return Ronda(orden, mazo, descarte)

    def cerrar_ronda(self, ronda: Ronda) -> None:
        """
        Tras jugarse la ronda completa (ronda.esta_terminada() == True),
        verificar derrotas y rotar el primer jugador para la próxima.
        Los puntajes ya fueron sumados al acumulado dentro de Ronda._cerrar.
        """
        if not ronda.esta_terminada():
            raise RuntimeError("La ronda todavia no termino, no se puede cerrar.")

        # Verificar si alguien superó el límite
        for j in self._jugadores:
            j.verificar_derrota(self._limite)

        if any(j.ha_perdido() for j in self._jugadores):
            self._terminada = True

        # Rotar repartidor / primer jugador
        self._indice_inicial = (
            (self._indice_inicial + 1) % len(self._jugadores)
        )
        self._numero_ronda += 1

    # --- Resultado ---------------------------------------------------

    def ganador(self) -> Optional[Jugador]:
        """
        Jugador con menor puntaje acumulado. None si la partida sigue.
        En empates, devuelve el primero en orden de inscripción.
        """
        if not self._terminada:
            return None
        mejor: Optional[Jugador] = None
        mejor_puntaje = 10**9
        for j in self._jugadores:
            p = j.get_puntaje_acumulado()
            if p < mejor_puntaje:
                mejor_puntaje = p
                mejor = j
        return mejor

    def perdedor(self) -> Optional[Jugador]:
        """El que disparó el cierre (primero en pasar el límite)."""
        if not self._terminada:
            return None
        for j in self._jugadores:
            if j.ha_perdido():
                return j
        return None
