# DESIGN — Depths Within

Documento de diseño vigente. Si otro documento lo contradice, gana este.
(Los ~80 documentos de fases anteriores están en `docs/archive/` y son históricos.)

## 1. Qué es el juego

Un thriller de encierro y desgaste en un submarino de la Segunda Guerra Mundial.
El jugador es el capitán. La guerra es real y funciona como **reloj externo**
(destructores, cargas de profundidad, silencio obligatorio). Lo que destruye al
submarino es la **tripulación bajo presión** y, quizá, algo más.

La pregunta que el juego le hace al jugador, una y otra vez:
**¿apago el sonar, encierro a un marinero o cumplo la misión?**
Si esas tres decisiones no duelen, el juego no funciona.

### Pilares

1. **Los sistemas generan la historia; la historia fija solo los sostiene.**
   No se escriben diálogos largos. Se escriben estados, disparadores y consecuencias.
2. **Toda decisión cuesta algo que el jugador valora.** No hay opción gratis ni opción obvia.
3. **La tripulación miente (sin querer).** El jugador ve síntomas, no números verdaderos.
4. **El submarino es un personaje:** aire, humedad, ruido, olor, instrumentos que dudan.
5. **Ambigüedad estructural** (sección 2): nada se confirma.

## 2. Reglas de lo sobrenatural

### Regla de oro

> **Todo fenómeno tiene una explicación mundana plausible y una sobrenatural.
> El juego nunca confirma ninguna.**

Consecuencias de diseño, obligatorias:

- Todo evento declara `mundane_cause` y `uncanny_cause` en `data/events.json`.
  Un evento sin ambas no pasa la validación (`tests/test_dread_events.py`).
- Cada evento declara además `mundane_when`: la condición bajo la cual la causa
  mundana es creíble (CO2 alto, sueño, culpa, enemigo real, sabotaje…).
  El simulador audita qué fracción de eventos se disparó con la explicación
  mundana disponible. **Meta: ≥ 70 % en los actos I y II.** Los eventos
  "solo inexplicables" se reservan para el acto III.
- El jugador nunca ve `mundane_cause` / `uncanny_cause`; solo el informe de
  la partida terminada (debrief) y el simulador.

### La presencia

No es un monstruo con barra de vida. Es una **presencia que se manifiesta por
sonido, repetición y ausencia**. Reglas:

| Hace | No hace nunca |
|---|---|
| Imita voces, aprende nombres | Daña el casco directamente |
| Aísla a personas | Aparece en pantalla antes del acto III |
| Repite sonidos y frases | Es confirmada por un instrumento fiable |
| Hace que la tripulación se destruya sola | Mata por sí misma |

**`attention`** (0–1) es la variable oculta de la presencia. Nunca se muestra al
jugador. Sube con: pings activos, tripulantes solos (en guardia nocturna o
aislados por orden), nombres que la tripulación grita o responde, y el propio
miedo colectivo. Baja con: grupo reunido y rutina sostenida, superficie, silencio
compartido. Es la palanca de la que cuelgan los eventos "solo inexplicables".
Por eso **aislar a un marinero y apagar el sonar tienen un costo oculto distinto**:
una alimenta a la presencia, la otra desconfía de la tripulación.

## 3. Modelo de estado

Todos los valores son 0–1 salvo que se indique. Tick = 1 hora de juego
(consistente con `engine/game.py`, que avanza una hora por turno).

### 3.1 Por tripulante (verdad oculta)

| Variable | Significado | Sube por | Baja por |
|---|---|---|---|
| `fear` | miedo | eventos, voces, rumores, combate | rutina, cohesión, superficie |
| `fatigue` | sueño perdido | guardia, descansos cancelados, CO2 | descanso (se reduce con miedo y CO2) |
| `guilt` | culpa acumulada | órdenes crueles, pérdidas, desapariciones | lentamente, con cohesión |
| `trust` | confianza en el capitán | decisiones coherentes y cuidado | ocultar cosas, castigos, sonar apagado |
| `candor` | (rasgo fijo) cuánto dice lo que siente | — | — |

Además: `role`, `section` (guardia 0–2), `isolated`, `missing`, `alive`,
`believes` (rumores que cree) y `name_known` (la presencia aprendió su nombre).

### 3.2 Reportado frente a real

Lo que el jugador ve en un informe es:

```
candor_eff = candor × trust × (0.6 + 0.4 × cohesión)
reportado  = lerp(0.15, estrés_real, candor_eff)
```

Con baja confianza un tripulante dice "todo bien" estando roto. El jugador solo
puede ver **síntomas** (`Crew.symptoms()`), cada uno con umbral sobre el valor
verdadero: silencios, errores en el puesto, microsueños, hablar solo, evitar
la mirada, dejar ofrendas, acaparar comida, rumorear. Observarlos exige
presencia (rondas, médico) y no es perfecto.

### 3.3 De la nave

`cohesion`, `discipline`, `routine`, `hull`, `readiness`, `co2` (fracción; 0.005 normal,
0.015 molesto, 0.03+ peligroso), `noise`, `attention` (oculta), `progress` (misión),
`sonar_on`, `silent_running`, `surfaced`, `hours_submerged`, `flags`, `rumors`.

`routine` es la media de cinco rutinas con nivel propio: **comidas, música, cartas,
café, guardias**. Cada una se desgasta sola y se restaura con una orden (que
cuesta tiempo de misión). **Cuando la rutina se rompe, el horror avanza.**

### 3.4 Índice de pavor y etapas

```
dread = 0.30·miedo_medio + 0.15·culpa_media + 0.15·(1−confianza_media)
      + 0.15·fatiga_media + 0.10·presión_CO2 + 0.15·(1−rutina)
```

Las etapas del sistema anterior (DENIAL → MADNESS) se conservan **solo como
presentación**, derivadas de `dread`. **El tiempo transcurrido ya no es causa de
horror**: `HorrorMetrics.total_days` queda obsoleto como disparador.

### 3.5 Rumores

Un rumor tiene `intensity`, `believers` y un efecto continuo (`drift`) sobre
quienes lo creen. Se propaga solo, más rápido con miedo y cohesión (la gente
habla), y **no se controla directamente**: el jugador puede `address_crew`
(costoso, depende de la confianza) o aislar a un portador (que alimenta a la
presencia). Ejemplos: "el torpedero vio a alguien en el tubo 3", "el capitán está
marcado".

## 4. El sonar como fuente principal de horror

El sonar real (`world/sonar_systems.py`: GHG, termoclina, fatiga del operador)
**se conserva**. Encima va una capa de **contactos fantasma** (`dread/phantom.py`):

- `echo`: un contacto que solo oye un operador (`audible_to`). Se mueve contra la corriente.
- `voice`: usa un nombre que la presencia aprendió.
- `morse`: mensajes de barcos hundidos; nombres de tripulantes aún vivos.

Dinámica:

- Crece si se ignora (`intensity` sube con `attention`) y se vuelve audible
  para más gente.
- **Apagar el sonar** calla los fantasmas, baja el miedo del operador, **y
  deja al submarino ciego ante contactos reales** (detección real 0.9 → 0.3) y
  erosiona la confianza de quienes lo oyeron ("el capitán nos oculta algo").
- **Dejarlo encendido** mantiene la alerta real, pero desgasta al operador y
  alimenta la creencia compartida.
- El sonarista, fatigado y asustado, "traduce" ecos como frases.

Dos contraejemplos deliberados: un contacto enemigo **real** aparece justo cuando
todos creen que es alucinación, y una alarma general por un fantasma gasta
recursos y delata la posición.

## 5. Órdenes costosas del capitán

Cada orden (`dread/orders.py`) tiene beneficio inmediato **y** un costo oculto.

| Orden | Beneficio | Costo |
|---|---|---|
| `silence_sonar` | calla fantasmas; baja miedo del operador | ciego ante lo real; baja `trust` |
| `isolate(c)` | corta rumor; frena sabotaje | `trust`/`guilt` de c; sube `attention`; tras 6 h sube el miedo de c |
| `force_compartment(c)` | se cumple la tarea | `trust`↓↓, `guilt` de c y testigos |
| `cancel_rest` | `readiness`↑ ahora | `fatigue` acumulativa, errores, `discipline`↓ luego |
| `ration(alcohol/tobacco)` | `discipline`↑ | `trust`↓, `routine`↓ |
| `hold_ritual` | `routine`↑, `cohesion`↑ | tiempo de misión |
| `address_crew` | baja un rumor | gasta `trust`; si `trust` es bajo, lo empeora |
| `scrub_air` | `co2`↓ | consume reserva de cal sodada |
| `surface` | `co2`, miedo y `attention`↓ | riesgo aéreo; progreso casi nulo |
| `active_ping` | información real | `noise`↑, `attention`↑ |
| `silent_running` | `noise`↓ en combate | progreso ×0.5 |

## 6. Eventos

`data/events.json`. Cada evento:

```
id, act (1-3), weight, cooldown, once?,
requires        condiciones sobre el estado (DSL de dread/conditions.py)
mundane_when    condición bajo la que la causa mundana es creíble
mundane_cause   texto (solo debrief)
uncanny_cause   texto (solo debrief)
target?         selector de tripulante ("highest fear", "role sonar"…)
text            lo que ve el jugador
effects         lista de operaciones sobre el estado
choices?        opciones: key, text, tags, requires, effects, cost
```

Reglas:

- Máximo **un evento por tick** y enfriamiento global mínimo de 3 ticks.
- Los eventos con `choices` son **decisiones del capitán**; bloquean el tiempo
  hasta resolverse.
- Los combates son eventos *programados* (reloj externo), no aleatorios.

Catálogo inicial (ver el JSON): marinero que desaparece (litera tibia),
llamada desde el tubo de torpedos, ofrendas en máquinas, dos testigos del mismo
muerto, voz del capitán por radio, sueño compartido, pánico que bloquea una
válvula, capitán "marcado" y motín, médico que receta silencios, intento de
escapar por la escotilla, entrada de diario que nadie escribió, contacto real
tomado por alucinación, alarma falsa.

## 7. Actos y estructura de patrulla

Patrulla de vertical slice: **72 ticks (3 días)**. Los actos se **derivan del
estado, no del calendario**: `act = min(según_dread, 1 + tick // 24)`, con
`según_dread = 1` si `dread < 0.22`, `2` si `< 0.38`, `3` desde ahí. El tope por
tiempo solo impide que el acto III aparezca el primer día; nunca lo provoca.

- **Acto I — Normalidad bajo tensión.** Rutina, combate de la guerra, primer eco que solo oye un operador.
- **Acto II — Grietas.** Desaparición, rumores, órdenes costosas, primer motín en gestación.
- **Acto III — Sin salida.** Eventos "solo inexplicables", la presencia más audible, la tripulación se destruye o el capitán escoge qué salvar.

## 8. Finales (estados, no escenas)

Derivados del estado final (`dread/sim.py: classify_ending`):

- `lost_with_all_hands`: casco en 0.
- `deposed`: motín consumado; el capitán pierde el mando.
- `hollow_victory`: misión cumplida con cohesión < 0.3.
- `returned`: misión cumplida y tripulación entera.
- `turned_back`: se abortó la misión; la tripulación vive.
- `unaccounted`: llega a puerto con más (o menos) tripulantes de los que salieron
  (final del acto III, reservado).

## 9. Criterios de aceptación del bucle

El simulador (`python -m dread.sim`) juega patrullas con políticas fijas
(`mission_first`, `crew_first`, `paranoid`) sobre muchas semillas. El diseño es
válido si:

1. **Las políticas divergen en un trade-off real:** `mission_first` completa la
   misión bastante más a menudo que `crew_first`, y `crew_first` deja mejor
   cohesión, supervivencia y casco. Si una estrategia domina en todo, falta un dilema.
2. **Ninguna política termina en el mismo final > 80 % de las semillas.**
3. **Auditoría de ambigüedad:** ≥ 70 % de los eventos de actos I–II se disparan
   con la explicación mundana disponible (`mundane_when`).
4. **Sin muerte súbita:** el casco nunca baja de 0.3 antes del tick 24 con ninguna política.
5. **Sin contenido muerto:** cada evento del catálogo se dispara en alguna política.
6. **Determinismo:** misma semilla, misma patrulla.
7. **La presencia no desaparece con buena gestión:** toda política ve ≥ 2 pulsos
   y el primero antes del tick 30 en ≥ 95 % de las semillas; los pulsos severos
   los gana quien juega mal.

Todos son pruebas automáticas (`tests/test_dread_sim.py`).

### Calibración actual (300 semillas, 72 ticks)

| Política | Misión cumplida | Pierde el barco | Cohesión | Supervivencia | Casco | Dread máx. | Pulsos |
|---|---|---|---|---|---|---|---|
| `mission_first` | 55% | 8% | 0.47 | 0.90 | 0.18 | 0.73 | 10.1 (primero: tick 14) |
| `crew_first` | 38% | 0% | 0.77 | 0.97 | 0.44 | 0.30 | 7.4 (primero: tick 15) |
| `paranoid` | 60% | 32% | 0.60 | 0.95 | 0.14 | 0.44 | 8.1 (primero: tick 15) |

Estos números son una **primera calibración**, no un objetivo. Lo que fijan los
tests son las relaciones entre políticas, no los valores absolutos.

### La presencia no desaparece con buena gestión

Dos mecanismos lo garantizan (criterio 7):

- **Piso de atención:** `attention` nunca baja de `0.25 × clamp((horas_sumergido − 10) / 60)`.
  El tiempo bajo el agua le da un punto de apoyo pase lo que pase. Solo cuentan
  horas sumergido; salir a superficie pausa el reloj.
- **Pulsos obligatorios:** los eventos marcados `"beat": true` son los que
  manifiestan a la presencia. Si pasan 14 ticks (a partir del tick 8) sin
  ninguno, el siguiente evento sale forzosamente de entre los pulsos cuyos
  requisitos se cumplen. Hay pulsos de requisitos bajos (`footsteps_on_hull`,
  `extra_place_set`, `clock_slow`) para que el juego cuidadoso los vea.

El jugador cuidadoso ve pulsos leves y repetidos (pasos en el casco, un lugar de más
en la mesa). Los severos (`hatch_caller`, `unaccounted_count`, `tube_breathing`)
los gana quien juega mal.

### Problemas abiertos (conocidos)

- **`crew_first` fracasa la misión ~60 %.** El costo en tiempo del cuidado
  (rituales, superficie, búsquedas) puede ser excesivo. Falta ver si el jugador
  humano lo percibe como justo.
- **`paranoid` pierde el barco ~un tercio de las veces** por quedarse sordo ante
  contactos reales. Es la lección buscada, pero conviene revisar si es demasiado dura.
- **Pulsos repetidos:** `footsteps_on_hull` sale ~2 veces por patrulla con el mismo
  texto. Es repetición deliberada, pero hace falta más variantes de texto.
- Las políticas son simples. Un jugador humano combinará órdenes de formas que
  el simulador no cubre; hay que jugar la patrulla a mano antes de fiarse de estos números.

## 10. Qué cambia en el código existente

| Hoy | Problema | Destino |
|---|---|---|
| `HorrorMetrics.calculate_horror_stage` por `total_days` | el horror es un reloj | etapa derivada de `dread` |
| `HorrorManager`: encuentro con `# TODO: Actually spawn` | no hace nada | se reemplaza por `DreadWorld.tick()` |
| `PhysicalPhase.hull_damage_rate` / `creature_visible` | monstruo que daña el casco | se retira del modelo nuevo |
| `DecisionManager.resolve_option` (`pass` en moral/XP) | decisiones sin consecuencia | decisiones de `DreadWorld` con efectos reales |
| `generate_random_decision` al 1.5 % | decisiones aleatorias sin contexto | eventos con prerrequisitos |
| `try/except Exception: pass` en el bloque de horror | bugs silenciosos | se registra el error |
| `LoyaltyTracker` (loyalty + 3 estreses) | moral única y verdadera | `Crew` con verdad/reporte/síntomas |

Se **conserva**: sonar histórico, armas, mapa táctico, tiempo, suministros,
`crew_loyalty` para el ranking de fin de guerra.

La lógica nueva vive en el paquete `dread/` (solo biblioteca estándar, sin
dependencias de tcod, testeable sin ventana). `dread/bridge.py` la conecta al juego.

## 11. Fuera de alcance por ahora

Más renderers/tilesets, más tipos de submarino, árbol de misiones históricas
extra y cualquier diálogo largo. Hasta que los criterios de la sección 9 pasen,
el trabajo va al estado y a los eventos, no a la capa visual.

## 12. Referencias

Lovecraft, *El templo*; McCammon, *The Night Boat*; Buchheim, *Das Boot*
(rutina, claustrofobia real); Simmons, *El terror*; Crichton, *Esfera*;
Armfield, *Our Wives Under the Sea*; Hodgson, *The Ghost Pirates*.
Juegos: Barotrauma, Iron Lung, SOMA, Sunless Sea, Return of the Obra Dinn
(el diario inconsistente), Still Wakes the Deep, el estrés de Darkest Dungeon.
