# Dash

Implementación en Python de un juego de cartas con baraja española en el que cada jugador trata de terminar la ronda con el menor puntaje en mano. Originalmente prototipado en Java (`src/dash/`); este README cubre la versión Python que vive en `src/dash_py/`.

## El juego en una línea

Mazo de 48 cartas (variante de baraja española que incluye el 8 y el 9). Cada jugador empieza con 4 cartas boca abajo y solo conoce 2 de ellas. En cada turno tira matches al descarte, levanta del mazo para mejorar su mano, y puede arriesgarse a tirar cartas que no vio. Cuando alguien canta **Dash**, los demás juegan un turno más y se revelan las manos: cuanto menos puntaje, mejor. La partida dura varias rondas hasta que alguien supera los 100 puntos.

## Cómo correrlo

Necesitás Python 3.9 o superior (sin dependencias externas).

```bash
cd Dash/src

# Partida automática con 4 simuladores hasta 100 puntos
python -m dash_py.tester

# Vos como humano + 3 simuladores (input por consola)
python -m dash_py.consola
```

## Estructura del proyecto

```
Dash/
├── src/
│   ├── dash/               # prototipo Java original (referencia)
│   └── dash_py/            # versión Python
│       ├── __init__.py
│       ├── palo.py             Enum Palo {ORO, COPA, BASTO, ESPADA}
│       ├── carta.py            Carta (abstract)
│       ├── carta_normal.py     Cartas sin efecto
│       ├── carta_especial.py   CartaEspecial (abstract)
│       ├── carta_caballo.py    11 — intercambia con otro jugador
│       ├── carta_diez.py       10 — mira una carta propia
│       ├── carta_doce_especial.py  12 de basto/espada — vale 0
│       ├── mano.py             Mano (lista de cartas)
│       ├── mazo.py             Mazo (pila + reshuffle desde descarte)
│       ├── descarte.py         Descarte (pila con tope visible)
│       ├── jugador.py          Jugador: mano + cartas_vistas + puntaje
│       ├── decisor.py          Protocol Decisor + DecisorSimulador + DecisorMixto
│       ├── decisor_consola.py  DecisorConsola (input por terminal)
│       ├── ronda.py            Ronda (orquesta fases del turno y canto)
│       ├── partida.py          Partida (multi-ronda, rotación, límite)
│       ├── tester.py           entrypoint: partida automática 4 simuladores
│       └── consola.py          entrypoint: humano + 3 simuladores
├── diagrama-clases-dash.html
└── README.md
```

Convención: un archivo por clase, identificadores en español, snake_case en métodos.

## Reglas del juego

### Mazo y reparto

El mazo tiene 48 cartas: números 1 al 12 en los cuatro palos `oro`, `copa`, `basto` y `espada` (variante que sí incluye el 8 y el 9). Se reparten 4 cartas a cada jugador, una por una. Cada jugador "ve" sus dos primeras cartas al inicio; las otras dos quedan boca abajo. La primera carta del mazo restante sale al descarte y abre la mesa.

### Valor y efectos

| Carta                  | Valor | Efecto al ir al descarte                          |
|------------------------|-------|---------------------------------------------------|
| 1 a 9                  | su número | ninguno                                       |
| 10                     | 10    | el jugador mira una carta propia que no conocía   |
| 11 (Caballo)           | 11    | el jugador intercambia una carta con otro jugador |
| 12 de oro / copa       | 12    | ninguno                                           |
| 12 de basto / espada   | 0     | ninguno (es la mejor carta del juego)             |

### Estructura del turno

**Fase 1 — tirar matches (opcional).** El jugador puede intentar tirar cartas de su mano, incluso sin saber su valor (bluff).
- Si el número coincide con el tope del descarte: la carta se descarta y dispara su efecto.
- Si no coincide (par mal cantado): la carta se queda en la mano, el jugador la ve (quedó revelada), y recibe 1 carta del mazo como penalización. La mano crece +1.

**Fase 2 — tomar o levantar (obligatoria).** El jugador elige una de dos opciones:
- **Tomar el tope del descarte** y cambiarlo por una de su mano. La carta tomada no dispara efecto (ya lo hizo cuando se descartó). La carta que sale sí dispara efecto. *Esta opción está bloqueada si en fase 1 el jugador ya tiró algo*, para evitar el loophole de tirar un Diez y volvérselo a agarrar.
- **Levantar del mazo** y luego: tirar la levantada al descarte (dispara efecto), o cambiarla por una de la mano (la vieja al descarte con efecto).

**Fase 1' — más matches (opcional).** La fase 2 puede haber cambiado el tope, revelado cartas (Diez) o reorganizado manos (Caballo). El jugador puede intentar más tiradas con el mismo riesgo de penalización.

**Fase 3 — cantar Dash (opcional, fin del turno propio).** El jugador declara que corta la ronda. Cada otro jugador juega un turno más y luego se cierra. No hay penalización por cantar y no ganar: cada uno suma el valor real de su mano al acumulado.

### Reshuffle

Si el mazo se vacía durante la fase 2 (o al buscar una carta de penalización), el descarte —menos su tope actual— se mezcla y vuelve a ser el mazo.

### Cierre de ronda y partida

Al cerrar la ronda cada jugador suma el puntaje de su mano a su acumulado. El primer jugador rota una posición entre rondas. La partida termina cuando alguien supera el límite (100 por defecto); gana quien tenga el menor acumulado.

## Modelo de clases

```
Carta (abstract) ──── CartaNormal
                └──── CartaEspecial (abstract) ── CartaCaballo
                                              ├── CartaDiez
                                              └── CartaDoceEspecial

Mano     posee  →  List[Carta]
Mazo     posee  →  List[Carta]   (pila, robar() del tope, reshuffle desde descarte)
Descarte posee  →  List[Carta]   (pila, ver_tope() / sacar_tope())
Jugador  posee  →  Mano + cartas_vistas + puntaje_acumulado

Decisor (Protocol)
   ├── DecisorSimulador   heurística simple, nunca bluffea
   ├── DecisorConsola     input() por terminal
   └── DecisorMixto       despacha según un mapa Jugador → Decisor

Ronda    orquesta →  turnos (fase 1 / 2 / 1' / 3) sobre una ronda
Partida  orquesta →  varias Rondas hasta el límite, rota primer jugador
```

`Carta.aplicar_efecto(ronda, jugador, decisor)` devuelve un `Optional[str]` con el log del efecto. La `Ronda` recolecta esos strings y los entrega en el dict de log del turno; los entrypoints deciden cuándo imprimirlos. No se imprime desde dentro de `aplicar_efecto` para preservar el orden temporal.

## El Protocol Decisor

Toda decisión que tomaría una persona en la mesa pasa por el `Decisor`:

```python
class Decisor(Protocol):
    def decidir_proxima_tirada(self, jugador, descarte) -> Optional[int]: ...
    # posición a intentar tirar en fase 1 / fase 1'; None para parar

    def decidir_inicio_fase2(self, jugador, mazo, descarte) -> Tuple[str, Optional[int]]: ...
    # ("tomar_descarte", pos) o ("levantar", None)

    def decidir_swap(self, jugador, levantada, mazo, descarte) -> Tuple[str, Optional[int]]: ...
    # ("tirar", None) o ("cambiar", pos)

    def querer_cantar(self, jugador) -> bool: ...
    def elegir_pos_para_diez(self, jugador) -> Optional[int]: ...
    def elegir_caballo(self, jugador, otros) -> Optional[Tuple[Jugador, int, int]]: ...
    # (otro_jugador, pos_del_otro, pos_propia)
```

`DecisorSimulador` implementa una heurística simple: solo intenta tirar cartas que ya vio (nunca bluffea), toma el tope del descarte si mejora su mano, canta Dash cuando su puntaje estimado es bajo. `DecisorConsola` delega cada decisión en `input()` para que la tome un humano por terminal. `DecisorMixto` combina ambos, útil para partidas con humanos y bots mezclados.

## Cómo extenderlo

**Nuevo tipo de carta especial.** Heredá de `CartaEspecial`, definí `get_valor()` y sobrescribí `aplicar_efecto()` devolviendo el string del log.

**Nuevo decisor (IA, GUI, red).** Implementá el Protocol `Decisor`. No hace falta heredar de ninguna clase concreta.

**Otra variante de mazo.** Agregá un método de fábrica en `Mazo`, equivalente a `crear_mazo_espanol`.

## Origen

El paquete `src/dash_py/` es una migración del prototipo Java en `src/dash/`. El Java original tiene las mismas clases base (`Carta`, `Mazo`, `Mano`, `Jugador`) pero sin `Ronda`, `Descarte`, `Decisor` ni `Partida`, que se sumaron durante la migración para modelar las reglas completas del juego.
