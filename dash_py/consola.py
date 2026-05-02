"""
Entrypoint interactivo: jugá una ronda de Dash por consola contra
tres simuladores.

Cómo correrlo (desde la carpeta Dash/src/):
    python -m dash_py.consola

El humano es el primer jugador (por defecto "Iker"). Los demás los maneja
DecisorSimulador con la heurística por defecto.
"""

from .decisor import DecisorMixto, DecisorSimulador
from .decisor_consola import DecisorConsola
from .descarte import Descarte
from .jugador import Jugador
from .mazo import Mazo
from .ronda import Ronda
from .tester import imprimir_log_turno


def main() -> None:
    print("=================================================")
    print("   DASH — partida interactiva (vos vs simuladores)")
    print("=================================================\n")

    # Pedimos el nombre del humano (con default Iker)
    nombre = input("Tu nombre [Iker]: ").strip() or "Iker"

    jugadores = [
        Jugador(nombre),
        Jugador("Maria"),
        Jugador("Lucas"),
        Jugador("Sofia"),
    ]
    humano = jugadores[0]

    # Mazo + reparto
    mazo = Mazo.crear_mazo_espanol()
    mazo.mezclar()
    print(f"\nMazo de 40 cartas mezclado. Repartiendo 4 a cada uno...")
    for _vuelta in range(4):
        for j in jugadores:
            j.recibir_carta(mazo.robar())

    # Cada jugador (incluido vos) ve sus 2 primeras cartas al inicio
    for j in jugadores:
        j.marcar_iniciales_vistas(2)

    print(f"\n{humano.get_nombre()}, estas son las dos cartas que viste al repartir:")
    for i in range(humano.get_mano().tamano()):
        if humano.conoce_carta(i):
            print(f"  pos {i}: {humano.get_mano().obtener(i)}")
        else:
            print(f"  pos {i}: ???")
    input("\n[ENTER para empezar la ronda]")

    # Carta inicial sobre la mesa
    descarte = Descarte()
    descarte.tirar(mazo.robar())

    # Decisores: humano + 3 simuladores
    decisor_humano = DecisorConsola()
    decisor_sim = DecisorSimulador(umbral_dash=10)
    decisor = DecisorMixto({
        humano: decisor_humano,
        jugadores[1]: decisor_sim,
        jugadores[2]: decisor_sim,
        jugadores[3]: decisor_sim,
    })

    ronda = Ronda(jugadores, mazo, descarte)

    # Loop de turnos
    max_turnos = len(jugadores) * 30
    turnos = 0
    while not ronda.esta_terminada() and turnos < max_turnos:
        # Antes de cada turno mostramos un mini-resumen del estado público
        print("\n-------------------------------------------------")
        print(f"Turno de {ronda.jugador_actual().get_nombre()}")
        print(f"Tope del descarte: {descarte.ver_tope()}  |  Mazo: {mazo.tamano()} cartas")
        for j in jugadores:
            print(
                f"  {j.get_nombre()}: {j.get_mano().tamano()} cartas en mano"
                + (f" (canto Dash)" if j is ronda.dash_cantado_por else "")
            )

        log = ronda.jugar_turno(decisor)
        # Para los turnos de simuladores, imprimimos el log "tester-style"
        # para que veas lo que hicieron. Para tu turno, ya viste todo
        # mientras decidías, así que igual lo imprimimos resumido.
        imprimir_log_turno(log)
        turnos += 1

    # Cierre y revelación
    print("\n=================================================")
    print("   FIN DE LA RONDA — revelación")
    print("=================================================")
    if ronda.dash_cantado_por is not None:
        print(f"Canto Dash: {ronda.dash_cantado_por.get_nombre()}")
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


if __name__ == "__main__":
    main()
