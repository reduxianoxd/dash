[README.md](https://github.com/user-attachments/files/27280376/README.md)
# Dash

Implementación en Python de un juego de cartas con baraja española en el que cada jugador trata de terminar la ronda con el menor puntaje en mano. Originalmente prototipado en Java (`src/dash/`); este README cubre la versión Python que vive en `src/dash_py/`.

## El juego en una línea

Mazo español de 40 cartas. Cada jugador empieza con 4 cartas boca abajo y solo conoce 2 de ellas. En cada turno tira matches al descarte y/o levanta del mazo para mejorar su mano. Cuando alguien canta **Dash**, los demás juegan un turno más y se revelan las manos: cuanto menos puntaje, mejor.

## Estructura del proyecto

```
Dash/
├── src/
│   ├── dash/               # proyecto Java original (referencia)
│   └── dash_py/            # migración a Python (este README)
│       ├── __init__.py
│       ├── palo.py
│       ├── carta.py
│       ├── carta_normal.py
│       ├── carta_especial.py
│       ├── carta_caballo.py
│       ├── carta_diez.py
│       ├── carta_doce_especial.py
│       ├── mano.py
│       ├── mazo.py
│       ├── descarte.py
│       ├── jugador.py
│       ├── decisor.py
│       ├── ronda.py
│       └── tester.py
├── diagrama-clases-dash.html
└── README.md
```

Convención: un archivo por clase, nombres en español, snake_case en métodos.

## Cómo correr el tester

Necesitás Python 3.9 o superior (no usa dependencias externas).

```
cd Dash/src
python -m dash_py.tester
```

El tester arma una mesa de 4 jugadores, reparte, abre el descarte, y juega una ronda completa con un simulador automático hasta que alguien canta Dash. Imprime turno a turno con los efectos de las cartas especiales y muestra el ganador y los puntajes acumulados al cierre.

## Reglas implementadas

### Mazo y reparto

La baraja española tiene 40 cartas: números 1, 2, 3, 4, 5, 6, 7, 10, 11 y 12 en los cuatro palos `oro`, `copa`, `basto` y `espada`. No hay 8 ni 9. Se reparten 4 cartas a cada jugador, una por una, y la primera carta del mazo restante sale boca arriba sobre la mesa para abrir el descarte.

Cada jugador "ve" sus dos primeras cartas al inicio (`marcar_iniciales_vistas(2)`); las otras dos quedan boca abajo y solo se descubren si las mira con un efecto.

### Valor de cada carta

| Carta              | Valor en puntos | Efecto al ir al descarte                            |
|--------------------|-----------------|-----------------------------------------------------|
| 1 a 7              | su número       | ninguno                                             |
| 10                 | 10              | el jugador mira una carta propia que no conocía     |
| 11 (Caballo)       | 11              | el jugador intercambia una carta con otro jugador   |
| 12 de oro / copa   | 12              | ninguno                                             |
| 12 de basto / espada | 0             | ninguno (es la carta más valiosa del juego)         |

### Estructura del turno

1. **Fase 1 (opcional).** El jugador puede tirar todas las cartas de su mano cuyo número coincida con el tope del descarte. La mano se achica.
2. **Fase 2 (obligatoria).** Levanta una carta del mazo y decide:
   - tirarla directo al descarte, o
   - cambiarla por una de su mano (la vieja se va al descarte).
3. **Fase 3 (opcional, al final del turno propio).** Cantar **Dash**: declara que cree tener el menor puntaje y corta la ronda. Los demás jugadores juegan exactamente un turno más cada uno y luego se revelan las manos.

Cualquier carta que toque el descarte dispara su efecto: tanto si se tira desde la mano como si llega ahí por un swap o por una tirada directa desde el mazo.

### Cierre y puntaje

Al cerrarse la ronda, cada jugador suma a su puntaje acumulado el valor de las cartas que le quedaron en la mano. No hay penalización por cantar Dash y no ganar: simplemente sumás lo tuyo. La gracia de cantar es que en una ronda con muchas incógnitas también te la jugás a la suerte.

## Modelo de clases

El diseño separa el "modelo del juego" (clases inmutables o de bajo nivel) de la "lógica de partida" (clases que orquestan).

```
Palo  ──┐
        │
Carta (abstract) ──── CartaNormal
        │
        └────── CartaEspecial (abstract) ── CartaCaballo
                                            CartaDiez
                                            CartaDoceEspecial

Mano    posee  →  List[Carta]
Mazo    posee  →  List[Carta]   (pila, se roba del tope)
Descarte posee →  List[Carta]   (pila, se ve el tope)
Jugador posee  →  Mano + puntaje + cartas_vistas

Decisor (Protocol)
   └── DecisorSimulador  (estrategia simple para el tester)

Ronda  orquesta  →  jugadores + Mazo + Descarte + Decisor
```

`Carta.aplicar_efecto(ronda, jugador, decisor)` es el punto de extensión polimórfico. Devuelve un string log (o `None`) para que la `Ronda` lo recolecte y lo imprima en orden.

## Decisor: cómo conectás un jugador real

Toda decisión que tomaría una persona en la mesa pasa por el `Decisor`:

```python
class Decisor(Protocol):
    def decidir_swap(self, jugador, levantada, mazo, descarte) -> Tuple[str, Optional[int]]: ...
    def querer_cantar(self, jugador) -> bool: ...
    def elegir_pos_para_diez(self, jugador) -> Optional[int]: ...
    def elegir_caballo(self, jugador, otros) -> Optional[Tuple[Jugador, int, int]]: ...
```

El proyecto trae `DecisorSimulador` con una heurística simple: cambia la levantada por la peor carta de la mano si conviene, canta Dash si su puntaje en mano es ≤ 10, mira la primera posición no vista cuando dispara el Diez, y en el Caballo intercambia su pos 0 con la del primer oponente.

Para enchufar un jugador humano basta con escribir otra clase que implemente las cuatro firmas y pasársela a `Ronda.jugar_turno`.

## Cómo extenderlo

- **Nuevo tipo de carta especial.** Heredá de `CartaEspecial`, definí `get_valor()` y sobrescribí `aplicar_efecto()` devolviendo el string del log.
- **Nuevo decisor (IA, humano por consola, GUI).** Implementá el `Protocol` `Decisor`. No hace falta heredar de ninguna clase concreta.
- **Otra variante de mazo.** Agregá un método de fábrica en `Mazo`, equivalente a `crear_mazo_espanol`.

## Lo que todavía no está

- **Reshuffle del descarte cuando se acaba el mazo.** Hoy si el mazo se vacía sin que nadie haya cantado, la ronda se cierra a la fuerza.
- **Penalización por par mal cantado.** El nombre de la mecánica que hace que la mano pueda crecer arriba de 4 cartas — pendiente de modelar.
- **Partida (varias rondas hasta que un jugador se pasa del límite).** Está la base (`Jugador.verificar_derrota(limite)`) pero falta el loop que rote la mano para repartir y termine la partida.
- **Interfaz humana.** Solo hay simulador. Falta una `DecisorConsola` o GUI.

## Origen

El paquete `src/dash_py/` es una migración 1 a 1 del proyecto Java en `src/dash/`. El Java original tiene las mismas clases (`Carta`, `Mazo`, `Mano`, `Jugador`, etc.) sin la `Ronda`, el `Descarte` ni el `Decisor`, que se sumaron durante la migración para terminar de modelar las reglas del juego.
