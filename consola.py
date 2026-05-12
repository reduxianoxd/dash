"""
Entrypoint interactivo: jugá una partida de Dash por consola contra
tres simuladores.

Cómo correrlo (desde la carpeta Dash/src/):
    python -m dash_py.consola

El humano es el primer jugador. Los demás los maneja DecisorSimulador
con la heurística por defecto.
"""

from .decisor import DecisorMixto, DecisorSimulador
from .decisor_consola import DecisorConsola
from .jugador import Jugador
from .partida import Partida
from .tester import imprimir_log_turno, imprimir_resumen_ronda


LIMITE_PARTIDA = 100
TOPE_TURNOS_POR_RONDA = 100


def main() -> None:
    print("=================================================")
    print("   DASH — partida interactiva (vos vs simuladores)")
    print("=================================================\n")

    nombre = input("Tu nombre [Iker]: ").strip() or "Iker"

    jugadores = [
        Jugador(nombre),
        Jugador("Maria"),
        Jugador("Lucas"),
        Jugador("Sofia"),
    ]
    humano = jugadores[0]

    decisor = DecisorMixto({
        humano: DecisorConsola(),
        jugadores[1]: DecisorSimulador(umbral_dash=10),
        jugadores[2]: DecisorSimulador(umbral_dash=10),
        jugadores[3]: DecisorSimulador(umbral_dash=10),
    })

    partida = Partida(jugadores, limite=LIMITE_PARTIDA)
    print(f"Partida hasta {partida.limite} puntos. Gana el de MENOR acumulado.\n")

    while not partida.terminada:
        print("\n=================================================")
        print(f"   RONDA {partida.numero_ronda + 1}")
        print("=================================================")

        ronda = partida.nueva_ronda()

        # Mostrarle al humano sus dos cartas iniciales vistas
        print(
            f"\n{humano.get_nombre()}, viste estas dos cartas al repartir:"
        )
        for i in range(humano.get_mano().tamano()):
            if humano.conoce_carta(i):
                print(f"  pos {i}: {humano.get_mano().obtener(i)}")
            else:
                print(f"  pos {i}: ???")
        print(f"\nCarta inicial sobre la mesa: {ronda.descarte.ver_tope()}")
        print("Acumulados:")
        for j in partida.jugadores:
            print(f"  {j.get_nombre()}: {j.get_puntaje_acumulado()}")
        input("\n[ENTER para arrancar la ronda]")

        # Loop de turnos
        turnos = 0
        while not ronda.esta_terminada() and turnos < TOPE_TURNOS_POR_RONDA:
            print("\n-------------------------------------------------")
            print(f"Turno de {ronda.jugador_actual().get_nombre()}")
            print(
                f"Tope: {ronda.descarte.ver_tope()}  |  "
                f"Mazo: {ronda.mazo.tamano()} cartas"
            )
            for j in jugadores:
                marca = " (canto Dash)" if j is ronda.dash_cantado_por else ""
                print(
                    f"  {j.get_nombre()}: {j.get_mano().tamano()} cartas en mano{marca}"
                )

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
            f"{perdedor.get_nombre()} paso el limite de {partida.limite} "
            f"({perdedor.get_puntaje_acumulado()})."
        )
    print(f"Ganador: {ganador.get_nombre() if ganador else '-'}")
    print(f"Rondas jugadas: {partida.numero_ronda}")
    print("\nPuntajes finales:")
    for j in partida.jugadores:
        marca = ""
        if j is ganador:
            marca = "  <-- gano"
        elif j is perdedor:
            marca = "  <-- paso el limite"
        print(f"  {j.get_nombre()}: {j.get_puntaje_acumulado()} puntos{marca}")


if __name__ == "__main__":
    main()
