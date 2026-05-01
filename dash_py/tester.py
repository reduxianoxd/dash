"""
Script de prueba para verificar la lógica del juego.

Cómo correrlo (desde la carpeta Dash/src/):
    python -m dash_py.tester

Flujo simulado:
  1. Mazo español de 40 cartas, mezclado.
  2. Reparto de 4 cartas a cada uno de 4 jugadores.
  3. Cada jugador "ve" sus cartas en pos 0 y 1 al inicio (ese es el
     conocimiento que tiene de su mano).
  4. La primera carta del mazo restante va al descarte (boca arriba).
  5. Se juega una ronda con tres fases por turno y la posibilidad de
     cantar Dash al final del turno propio.
  6. Cierre: cada jugador suma a su acumulado el puntaje real de su mano.
"""

from .decisor import DecisorSimulador
from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo
from .ronda import Ronda


# --------------------------------------------------------------------
# Helpers de impresión
# --------------------------------------------------------------------

def imprimir_log_turno(log: dict) -> None:
    j: Jugador = log["jugador"]
    print(f"\nTurno de {j.get_nombre()}:")
    print(f"  tope del descarte: {log['tope_inicial']}")
    print(
        "  mano: ["
        + ", ".join(str(c) for c in log["mano_inicial"])
        + "]"
    )

    tiradas = log["fase1_tiradas"]
    if tiradas:
        print(
            f"  Fase 1 -> tira {len(tiradas)} carta(s) que coinciden: "
            + ", ".join(str(c) for c in tiradas)
        )
        for ef in log["fase1_efectos"]:
            print(f"           {ef}")
    else:
        print("  Fase 1 -> sin coincidencias, no tira nada de la mano")

    f2 = log["fase2"]
    if f2 is None:
        pass
    elif f2["accion"] == "mazo_vacio":
        print("  Fase 2 -> mazo vacio, no se puede levantar")
    elif f2["accion"] == "tirar":
        print(
            f"  Fase 2 -> levanta {f2['levantada']} y la tira directo al descarte"
        )
        if log["fase2_efecto"]:
            print(f"           {log['fase2_efecto']}")
    elif f2["accion"] == "cambiar":
        print(
            f"  Fase 2 -> levanta {f2['levantada']}, la cambia por pos "
            f"{f2['posicion']}. Al descarte: {f2['al_descarte']}"
        )
        if log["fase2_efecto"]:
            print(f"           {log['fase2_efecto']}")

    if log["canto_dash"]:
        print(f"  Fase 3 -> {j.get_nombre()} canta DASH!")

    print(f"  -> mano resultante: {j.get_mano()} (tamano {j.get_mano().tamano()})")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main() -> None:
    print("=================================================")
    print("   TEST: Ronda completa de Dash con efectos reales")
    print("=================================================\n")

    # 1. Mazo español, mezclado
    mazo = Mazo.crear_mazo_espanol()
    print(f"Mazo creado con {mazo.tamano()} cartas (deberian ser 40).")
    mazo.mezclar()
    print("Mazo mezclado.\n")

    # 2. Jugadores
    jugadores = [
        Jugador("Iker"),
        Jugador("Maria"),
        Jugador("Lucas"),
        Jugador("Sofia"),
    ]

    # 3. Reparto: 4 cartas a cada uno
    print("Repartiendo 4 cartas a cada jugador...")
    for _vuelta in range(4):
        for j in jugadores:
            j.recibir_carta(mazo.robar())

    # 4. Cada jugador 've' sus dos primeras cartas
    print("\n--- Cartas iniciales que cada jugador VE (pos 0 y 1) ---")
    for j in jugadores:
        vistas = j.marcar_iniciales_vistas(2)
        print(
            f"{j.get_nombre()}: ve {[str(c) for c in vistas]}; "
            f"mano completa={j.get_mano()}"
        )

    # 5. Carta inicial en el descarte
    descarte = Descarte()
    descarte.tirar(mazo.robar())
    print(f"\nCarta inicial sobre la mesa: {descarte.ver_tope()}")
    print(f"Cartas en el mazo: {mazo.tamano()} (deberian ser {40 - 16 - 1})")

    # 6. Crear y jugar la ronda
    decisor = DecisorSimulador(umbral_dash=10)
    ronda = Ronda(jugadores, mazo, descarte)

    print("\n--- Simulación de la ronda ---")
    max_turnos = len(jugadores) * 20
    turnos_jugados = 0
    while not ronda.esta_terminada() and turnos_jugados < max_turnos:
        if ronda.mazo.esta_vacio() and ronda.dash_cantado_por is None:
            print(
                "\n[INFO] Se acabo el mazo sin canto: cerramos la ronda a la fuerza."
            )
            ronda.forzar_cierre()
            break
        log = ronda.jugar_turno(decisor)
        imprimir_log_turno(log)
        turnos_jugados += 1

    # 7. Cierre y revelación
    print("\n=================================================")
    print("   FIN DE LA RONDA — revelación")
    print("=================================================")
    canto = ronda.dash_cantado_por
    if canto is not None:
        print(f"Canto Dash: {canto.get_nombre()}")
    else:
        print("Nadie canto Dash (cierre forzado).")

    ganador = ronda.ganador_de_la_ronda()
    print(
        f"\nGanador de la ronda (menor puntaje en mano): "
        f"{ganador.get_nombre() if ganador else '-'}"
    )

    print("\nManos finales y puntajes:")
    for j in jugadores:
        marca = "  <-- gano" if j is ganador else ""
        print(
            f"  {j.get_nombre()}: {j.get_mano()}  "
            f"puntaje_mano={j.get_mano().calcular_puntaje()}  "
            f"acumulado={j.get_puntaje_acumulado()}{marca}"
        )

    print(f"\nMazo: {mazo.tamano()} cartas. Descarte: {descarte.tamano()} cartas.")
    print(
        "Total cartas (manos + mazo + descarte) = "
        f"{sum(j.get_mano().tamano() for j in jugadores) + mazo.tamano() + descarte.tamano()} "
        "(deberia ser 40)"
    )

    print("\n=================================================")
    print("   FIN DEL TEST")
    print("=================================================")


if __name__ == "__main__":
    main()
