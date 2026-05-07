"""
Participante de una partida.
Tiene una mano (cartas en juego) y un puntaje acumulado entre rondas.

También lleva el set de cartas que el jugador YA VIO de su propia mano
(ese estado es informativo, sirve para que las decisiones simulen la
"memoria" del jugador real).

Las acciones de turno (tirar matches, levantar del mazo, tomar del descarte)
viven en `Ronda`, que las orquesta con acceso al mazo y al descarte.
"""

from __future__ import annotations

from typing import List, Set, TYPE_CHECKING

from .carta import Carta
from .mano import Mano

if TYPE_CHECKING:
    from .descarte import Descarte


class Jugador:

    def __init__(self, nombre: str) -> None:
        self._nombre = nombre
        self._mano = Mano()
        self._puntaje_acumulado = 0
        self._ha_perdido = False
        # Cartas que el jugador ya vio (por identidad de objeto).
        # Cuando una carta sale de la mano, la sacamos del set para
        # no arrastrar información obsoleta.
        self._cartas_vistas: Set[Carta] = set()

    # --- Getters ------------------------------------------------------

    def get_nombre(self) -> str:
        return self._nombre

    def get_mano(self) -> Mano:
        return self._mano

    def get_puntaje_acumulado(self) -> int:
        return self._puntaje_acumulado

    def ha_perdido(self) -> bool:
        return self._ha_perdido

    # Propiedades pythónicas (de solo lectura)
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def mano(self) -> Mano:
        return self._mano

    @property
    def puntaje_acumulado(self) -> int:
        return self._puntaje_acumulado

    # --- Estado de partida -------------------------------------------

    def recibir_carta(self, carta: Carta) -> None:
        # Una carta nueva en la mano arranca como NO vista.
        self._mano.agregar(carta)

    def descartar_carta(self, posicion: int) -> Carta:
        """Saca la carta de la mano y la devuelve (sin tocar el descarte)."""
        carta = self._mano.remover(posicion)
        self._cartas_vistas.discard(carta)
        return carta

    def sumar_puntaje(self, puntos: int) -> None:
        self._puntaje_acumulado += puntos

    def verificar_derrota(self, limite: int) -> None:
        """Marca al jugador como derrotado si su puntaje superó el límite de la partida."""
        if self._puntaje_acumulado >= limite:
            self._ha_perdido = True

    # --- Conocimiento del jugador sobre su propia mano ---------------

    def ver_carta(self, posicion: int) -> Carta:
        """
        El jugador mira una carta de su mano. Queda registrada como vista.
        Devuelve la carta para poder mostrarla.
        """
        carta = self._mano.obtener(posicion)
        self._cartas_vistas.add(carta)
        return carta

    def conoce_carta(self, posicion: int) -> bool:
        """True si la carta en esa posición ya fue vista por el jugador."""
        if posicion < 0 or posicion >= self._mano.tamano():
            return False
        return self._mano.obtener(posicion) in self._cartas_vistas

    def marcar_iniciales_vistas(self, cantidad: int = 2) -> List[Carta]:
        """
        Helper para el reparto: el jugador 've' las primeras `cantidad`
        cartas de su mano. Devuelve la lista para imprimirla en el log.
        """
        vistas: List[Carta] = []
        for i in range(min(cantidad, self._mano.tamano())):
            vistas.append(self.ver_carta(i))
        return vistas

    def olvidar_todo(self) -> None:
        """Resetea el conocimiento (útil al empezar una ronda nueva)."""
        self._cartas_vistas.clear()

    def olvidar_carta(self, carta: Carta) -> None:
        """
        Quita una carta del set de vistas (si estaba). Lo usan internamente
        las acciones que sacan cartas de la mano y también el efecto del
        Caballo cuando intercambia cartas entre jugadores.
        """
        self._cartas_vistas.discard(carta)

    # --- Acciones de turno -------------------------------------------

    def posiciones_que_coinciden(self, descarte: "Descarte") -> List[int]:
        """
        Devuelve las posiciones de la mano cuyo numero coincide con el tope
        del descarte (TODAS, hayan sido vistas o no por el jugador).

        Esta es una utilidad para encontrar matches reales. La REGLA del
        juego permite tirar cualquier carta (incluso a ciegas); si la
        tirada no matchea hay penalización (1 carta del mazo). Por eso
        este método no filtra por `conoce_carta`: el filtrado lo hace
        la estrategia del Decisor (ej. el simulador solo intenta vistas).

        Si el descarte está vacío, no hay match posible: devuelve [].
        """
        tope = descarte.ver_tope()
        if tope is None:
            return []
        valor_tope = tope.get_numero()
        return [
            i for i in range(self._mano.tamano())
            if self._mano.obtener(i).get_numero() == valor_tope
        ]

    # --- Representación ----------------------------------------------

    def __str__(self) -> str:
        return f"{self._nombre} (puntaje acum.: {self._puntaje_acumulado})"

    def __repr__(self) -> str:
        return self.__str__()
