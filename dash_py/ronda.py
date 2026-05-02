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
            "fase1": {"tiradas": [], "efectos": [], "fallidas": [], "penalizaciones": []},
            "fase2": None,
            "fase2_efecto": None,
            "fase1_post": {"tiradas": [], "efectos": [], "fallidas": [], "penalizaciones": []},
            "reshuffle": 0,  # cantidad de cartas recicladas durante el turno
            "canto_dash": False,
        }

        # ---- Fase 1: tirar matches (con riesgo de penalización) -------
        log["fase1"] = self._tirar_matches(jugador, decisor)

        # ---- Fase 2: tomar del descarte O levantar del mazo ----------
        # Si en fase 1 ya tiramos cartas, el tope del descarte ahora es
        # nuestra propia tirada: ofrecer "tomar" abriría un loophole donde
        # el jugador tira para disparar un efecto y se la vuelve a agarrar.
        # Por eso solo permitimos elegir si la fase 1 no tuvo tiradas.
        if log["fase1"]["tiradas"]:
            accion_inicio, pos_inicio = ("levantar", None)
            log["tomar_bloqueado"] = True
        else:
            accion_inicio, pos_inicio = decisor.decidir_inicio_fase2(
                jugador, self._mazo, self._descarte
            )

        if accion_inicio == "tomar_descarte":
            if pos_inicio is None:
                raise ValueError("'tomar_descarte' requiere una posición.")
            tope = self._descarte.ver_tope()
            if tope is None:
                # El decisor quiso tomar pero no hay tope: degradamos a levantar.
                accion_inicio = "levantar"
            else:
                # Sacar el tope del descarte y meterlo en la mano (vista,
                # porque el jugador la vio antes de tomarla). La carta
                # tomada NO dispara efecto: ya disparó cuando alguien
                # la descartó originalmente.
                tomada = self._descarte.sacar_tope()
                vieja = jugador.get_mano().reemplazar(pos_inicio, tomada)
                jugador.olvidar_carta(vieja)
                jugador.ver_carta(pos_inicio)
                # La carta vieja sí va al descarte como descarte real:
                # el jugador se está deshaciendo de ella, así que dispara
                # su efecto si lo tiene.
                self._descarte.tirar(vieja)
                efecto_log = vieja.aplicar_efecto(self, jugador, decisor=decisor)
                log["fase2"] = {
                    "accion": "tomar_descarte",
                    "tomada": tomada,
                    "posicion": pos_inicio,
                    "al_descarte": vieja,
                }
                log["fase2_efecto"] = efecto_log

        if accion_inicio == "levantar":
            # Si el mazo se vació, intentamos reciclar el descarte primero.
            if self._mazo.esta_vacio():
                log["reshuffle"] = self._mazo.recargar_desde_descarte(self._descarte)

            if self._mazo.esta_vacio():
                log["fase2"] = {"accion": "mazo_vacio"}
            else:
                levantada = self._mazo.robar()
                accion, pos = decisor.decidir_swap(
                    jugador, levantada, self._mazo, self._descarte
                )
                if accion == "tirar":
                    self._descarte.tirar(levantada)
                    efecto_log = levantada.aplicar_efecto(
                        self, jugador, decisor=decisor
                    )
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
                    # La levantada entra a la mano y el jugador la VIO al
                    # robarla del mazo: la registramos como conocida así
                    # los efectos posteriores (p. ej. Diez) no la consideran
                    # "no vista".
                    jugador.ver_carta(pos)
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

        # ---- Fase 1' (post fase 2): tirar matches recién habilitados -
        # La fase 2 puede haber dejado un tope nuevo y/o haber revelado
        # cartas (Diez) o reorganizado manos (Caballo) que ahora abren
        # nuevos matches. Damos otra vuelta de "tirar matches".
        log["fase1_post"] = self._tirar_matches(jugador, decisor)

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

    # --- Helpers internos --------------------------------------------

    def _tirar_matches(self, jugador: Jugador, decisor: Decisor):
        """
        Loop de intento de tiradas. El decisor elige qué posición intentar
        (o None para parar). Para cada intento:
          - si el número de la carta coincide con el tope del descarte:
            la carta se va al descarte y dispara su efecto.
          - si NO coincide: la carta se queda en la mano, queda revelada
            para el jugador (la "vio" al intentar tirarla), y el jugador
            recibe 1 carta del mazo como penalización (la mano crece +1).

        Devuelve un dict con cuatro listas:
          - "tiradas":        cartas que efectivamente se descartaron
          - "efectos":        strings de log de los efectos disparados
          - "fallidas":       lista de (posicion, carta) que no matchearon
          - "penalizaciones": cartas tomadas del mazo como penalización
        """
        tiradas = []
        efectos = []
        fallidas = []
        penalizaciones = []
        while True:
            pos = decisor.decidir_proxima_tirada(jugador, self._descarte)
            if pos is None:
                break
            if pos < 0 or pos >= jugador.get_mano().tamano():
                # Decisión inválida: la ignoramos y paramos por seguridad.
                break

            carta = jugador.get_mano().obtener(pos)
            tope = self._descarte.ver_tope()

            if tope is not None and carta.get_numero() == tope.get_numero():
                # Match correcto: la carta sale al descarte y dispara efecto
                carta = jugador.descartar_carta(pos)
                self._descarte.tirar(carta)
                efecto_log = carta.aplicar_efecto(self, jugador, decisor=decisor)
                tiradas.append(carta)
                if efecto_log:
                    efectos.append(efecto_log)
            else:
                # Match fallido (par mal cantado): la carta NO se va.
                # El jugador la revela (ahora la conoce). Se le agrega 1
                # carta del mazo como penalización (con reshuffle si hace
                # falta).
                jugador.ver_carta(pos)
                fallidas.append((pos, carta))

                if self._mazo.esta_vacio():
                    self._mazo.recargar_desde_descarte(self._descarte)
                if not self._mazo.esta_vacio():
                    penalty = self._mazo.robar()
                    jugador.recibir_carta(penalty)
                    # La que el jugador acaba de levantar también la "ve".
                    jugador.ver_carta(jugador.get_mano().tamano() - 1)
                    penalizaciones.append(penalty)
                # Si el mazo seguía vacío después del reshuffle, no hay
                # carta de penalización física; el "fallaste" se loguea
                # igual.

        return {
            "tiradas": tiradas,
            "efectos": efectos,
            "fallidas": fallidas,
            "penalizaciones": penalizaciones,
        }

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
