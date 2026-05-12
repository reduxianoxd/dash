"""
Script de prueba para verificar la lógica del juego.

Cómo correrlo (desde la carpeta Dash/src/):
    python -m dash_py.tester

Juega una partida completa entre 4 simuladores, ronda tras ronda, hasta
que alguien supere el límite (default 100). Muestra el log de cada turno
y el resumen al final de cada ronda y de la partida.
"""

from .decisor import DecisorSimulador
from .jugador import Jugador
from .partida import Partida


# --------------------------------------------------------------------
# Helpers de impresión
# --------------------------------------------------------------------

def _imprimir_fase_tirar(fase: dict, etiqueta: str) -> None:
    """Imprime exitosas, fallidas y penalizaciones de una sub-fase de tirar matches."""
    tiradas = fase.get("tiradas") or []
    fallidas = fase.get("fallidas") or []
    penalizaciones = fase.get("penalizaciones") or []

    if not tiradas and not fallidas:
        if etiqueta == "Fase 1":
            print(f"  {etiqueta} -> no intenta tirar nada")
        return

    if tiradas:
        print(
            f"  {etiqueta} -> tira {len(tiradas)} carta(s) que matchean: "
            + ", ".join(str(c) for c in tiradas)
        )
        for ef in fase.get("efectos", []):
            print(f"           {ef}")
    if fallidas:
        intentos = ", ".join(f"pos {p}={c}" for p, c in fallidas)
        print(
            f"  {etiqueta} -> {len(fallidas)} intento(s) FALLIDO(s) "
            f"(par mal cantado): {intentos}"
        )
        if penalizaciones:
            print(
                "           penalizacion: levanta del mazo "
                + ", ".join(str(c) for c in penalizaciones)
            )


def imprimir_log_turno(log: dict) -> None:
    j: Jugador = log["jugador"]
    print(f"\nTurno de {j.get_nombre()}:")
    print(f"  tope del descarte: {log['tope_inicial']}")
    print(
        "  mano: ["
        + ", ".join(str(c) for c in log["mano_inicial"])
        + "]"
    )

    if log.get("reshuffle"):
        print(
            f"  [reshuffle] mazo vacio: se reciclaron {log['reshuffle']} "
            "cartas del descarte"
        )

    _imprimir_fase_tirar(log["fase1"], etiqueta="Fase 1")

    f2 = log["fase2"]
    if f2 is None:
        pass
    elif f2["accion"] == "mazo_vacio":
        print("  Fase 2 -> mazo vacio, no se puede levantar")
    elif f2["accion"] == "tirar":
        print(f"  Fase 2 -> levanta {f2['levantada']} y la tira directo al descarte")
        if log["fase2_efecto"]:
            print(f"           {log['fase2_efecto']}")
    elif f2["accion"] == "cambiar":
        print(
            f"  Fase 2 -> levanta {f2['levantada']}, la cambia por pos "
            f"{f2['posicion']}. Al descarte: {f2['al_descarte']}"
        )
        if log["fase2_efecto"]:
            print(f"           {log['fase2_efecto']}")
    elif f2["accion"] == "tomar_descarte":
        print(
            f"  Fase 2 -> toma el tope del descarte ({f2['tomada']}), "
            f"lo cambia por pos {f2['posicion']}. Al descarte: {f2['al_descarte']}"
        )
        if log["fase2_efecto"]:
            print(f"           {log['fase2_efecto']}")

    fase1_post = log.get("fase1_post") or {}
    if fase1_post.get("tiradas") or fase1_post.get("fallidas"):
        _imprimir_fase_tirar(fase1_post, etiqueta="Fase 1' (post fase 2)")

    if log["canto_dash"]:
        print(f"  Fase 3 -> {j.get_nombre()} canta DASH!")

    print(f"  -> mano resultante: {j.get_mano()} (tamano {j.get_mano().tamano()})")


def imprimir_resumen_ronda(ronda, partida: Partida) -> None:
    print("\n-------------------------------------------------")
    print(f"   FIN DE LA RONDA {partida.numero_ronda}")
    print("-------------------------------------------------")
    canto = ronda.dash_cantado_por
    if canto is not None:
        print(f"Canto Dash: {canto.get_nombre()}")
    else:
        print("Cierre forzado (sin canto).")

    print("Manos finales y puntajes:")
    for j in partida.jugadores:
        print(
            f"  {j.get_nombre()}: {j.get_mano()}  "
            f"puntaje_mano={j.get_mano().calcular_puntaje()}  "
            f"acumulado={j.get_puntaje_acumulado()}"
        )


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

LIMITE_PARTIDA = 100
TOPE_TURNOS_POR_RONDA = 100  # safety contra rondas infinitas


def main() -> None:
    print("=================================================")
    print("   TEST: Partida completa de Dash (4 simuladores)")
    print("=================================================\n")

    jugadores = [
        Jugador("Iker"),
        Jugador("Maria"),
        Jugador("Lucas"),
        Jugador("Sofia"),
    ]
    decisor = DecisorSimulador(umbral_dash=10)
    partida = Partida(jugadores, limite=LIMITE_PARTIDA)

    while not partida.terminada:
        print("\n=================================================")
        print(f"   RONDA {partida.numero_ronda + 1}")
        print(f"   Orden: {[j.get_nombre() for j in partida.proxima_orden]}")
        print("=================================================")

        ronda = partida.nueva_ronda()
        # Mostrar reparto y cartas iniciales vistas
        print("Reparto y cartas iniciales:")
        for j in partida.jugadores:
            vistas_idx = [
                i for i in range(j.get_mano().tamano()) if j.conoce_carta(i)
            ]
            vistas = [str(j.get_mano().obtener(i)) for i in vistas_idx]
            print(
                f"  {j.get_nombre()}: ve {vistas}; "
                f"mano completa = {j.get_mano()}"
            )
        print(f"Carta inicial sobre la mesa: {ronda.descarte.ver_tope()}")
        print(f"Mazo: {ronda.mazo.tamano()} cartas")

        # Loop de turnos con safety
        turnos = 0
        while not ronda.esta_terminada() and turnos < TOPE_TURNOS_POR_RONDA:
            log = ronda.jugar_turno(decisor)
            imprimir_log_turno(log)
            turnos += 1
        if not ronda.esta_terminada():
            print("\n[INFO] Tope de turnos alcanzado: cerramos la ronda a la fuerza.")
            ronda.forzar_cierre()

        partida.cerrar_ronda(ronda)
        imprimir_resumen_ronda(ronda, partida)

    # Cierre de la partida
    print("\n=================================================")
    print("   FIN DE LA PARTIDA")
    print("=================================================")
    perdedor = partida.perdedor()
    ganador = partida.ganador()
    if perdedor:
        print(
            f"{perdedor.get_nombre()} paso el limite de {partida.limite} puntos "
            f"({perdedor.get_puntaje_acumulado()})."
        )
    print(f"Ganador (menor puntaje): {ganador.get_nombre() if ganador else '-'}")
    print(f"Total de rondas jugadas: {partida.numero_ronda}")
    print("\nPuntajes finales:")
    for j in partida.jugadores:
        marca = ""
        if j is ganador:
            marca = "  <-- gano"
        elif j is perdedor:
            marca = "  <-- paso el limite"
        print(
            f"  {j.get_nombre()}: {j.get_puntaje_acumulado()} puntos{marca}"
        )

    print("\n=================================================")
    print("   FIN DEL TEST")
    print("=================================================")


if __name__ == "__main__":
    main()
