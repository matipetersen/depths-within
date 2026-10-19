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
| `verify_orders` | puede bajar `orders_doubt` | ruido, atención, tiempo; puede contradecir; una vez por misión |

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

Un evento se dispara por **dos tipos de disparador**:

1. **Por estado** (`requires`): el pool aleatorio, filtrado por acto, enfriamiento y condiciones.
2. **Por misión** (`mission` + `at_progress`): se dispara cuando el avance de esa
   misión cruza el umbral, una vez por misión, ignorando enfriamientos. Un evento
   con `mission` pero sin `at_progress` es del pool aleatorio, pero solo mientras
   esa misión está en curso.

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

### 7.1 Misiones: el segundo disparador

La patrulla es una **secuencia de misiones** (`data/missions.json`), cada una con
su ritmo, su ventana de tiempo y sus propios eventos (sección 6). Lo que ocurre
en cada una:

| Misión | Tipo | Qué pasa |
|---|---|---|
| 1. Hundir al acorazado | destruir | Contacto (acechar o forzar) y ataque final; el riesgo depende de la disponibilidad y de cómo se acercó. |
| 2. Encontrar el convoy y reportar | patrulla | Avistamiento: reportar ya (ruido, escoltas), seguir y reportar al anochecer (tiempo) o callar. El acuse de HQ nombra un barco que no estaba en el convoy. |
| 3. Hundir el vapor *Santa Lucía* | **moral** | Las órdenes dicen que las cruces rojas son un engaño. Tres salidas: hundirlo, detenerlo y dejar que salgan los botes, o negarse. |
| 4. Volver por la ruta norte | **moral** | Sin paradas ni contacto. Náufragos en el agua: pasar de largo o rescatarlos (¿y quién es el duodécimo?). |

Cada misión tiene su ventana (`ticks × 1.25`; las morales `× 2.2`: el reloj no
debe robar el dilema). Si se cierra, la misión **fracasa** y empieza la siguiente.

### 7.2 El origen de las órdenes nunca se resuelve

> **Las órdenes llegan de algún sitio, pero no se sabe bien de dónde.**

Cada misión se presenta con su **procedencia** (canal, firma, calidad 0–1):

| Misión | Procedencia | Calidad |
|---|---|---|
| 1 | Sobre sellado, entregado en el muelle, contrafirmado | 0.90 |
| 2 | Relevo de radio; la señal se reconoce, la frecuencia no | 0.60 |
| 3 | Encontrado en la caja fuerte del capitán; nadie recuerda cuándo llegó; la letra parece suya | 0.35 |
| 4 | Sin canal registrado; está en el diario con la fecha de hoy | 0.15 |

**La procedencia se degrada a medida que avanza la patrulla**: cuanto más se
hunde el barco, menos claro es quién manda. Reglas:

- Cada misión declara `mundane_origin` y `uncanny_origin`; el validador exige
  ambos (misma regla de oro que los eventos). Solo el *debrief* (`world.debrief()`)
  los muestra, al final.
- `orders_doubt` (0–1): cuánto desconfía la tripulación del origen. Sube con baja
  calidad y con las misiones morales; desgasta `trust` cada tick.
- **`verify_orders`**: pedir confirmación por radio, una vez por misión. Cuesta
  ruido, atención y tiempo. La respuesta tranquiliza (más probable con buena
  calidad), calla o **contradice** ("mismo indicativo, otro cifrado"). Nunca
  dice quién las envió.
- **Contraórdenes** (`orders_countermand`): una segunda señal anula la primera.
- Consecuencia oculta: que unas órdenes *consten o no en los registros* es
  incierto (`m4_unrecorded`, 50 %). Si no constan, no hay consejo de guerra por
  desobedecerlas ni expediente por torcerlas. El capitán no puede saberlo al decidir.

### 7.3 Misiones morales: deuda moral

Las misiones morales ofrecen siempre tres salidas con etiquetas
(`comply` / `alter` / `refuse`), y ninguna es gratis:

| Salida | Beneficio | Costo |
|---|---|---|
| Cumplir | Misión cumplida; sin conflicto con el mando | `moral_debt`↑, culpa y miedo de todos, `trust`↓, rumor propio (*«hundimos un buque hospital»*) |
| Torcer | La tripulación te sigue; poca deuda | Tiempo, exposición en superficie, riesgo de casco; `orders_bent` |
| Negarse | Sin deuda moral; `trust`↑ | `discipline`↓, `orders_doubt`↑, `orders_defied` |

**`moral_debt`** (oculta) alimenta la culpa de todos y a la presencia
(`attention`). Lo que el barco ha hecho no se deshace y atrae lo que lo persigue.

## 8. Finales (estados, no escenas)

Derivados del estado final (`dread/sim.py: classify_ending`):

- `lost_with_all_hands`: casco en 0 o sin tripulación.
- `deposed`: motín consumado; el capitán pierde el mando.
- `turned_back`: se abortó la patrulla.
- `stained_victory`: se hundió al buque civil. **Gana el remordimiento, no el consejo de guerra:** la tripulación lo sabe aunque el registro no lo diga.
- `court_martial`: se desobedeció una orden que *consta* en los registros.
- `returned_under_a_cloud`: se torció una orden que *consta*; el mando hará preguntas sobre el diario.
- `returned`: sin sangre en el diario ni expediente.
- `hollow_victory`: misiones cumplidas con cohesión < 0.3 o menos del 60 % de la tripulación.
- `mission_failed`: menos de 3 misiones cumplidas.
- `unaccounted` (reservado): llega a puerto con más tripulantes de los que salieron.

## 9. Criterios de aceptación del bucle

El simulador (`python -m dread.sim`) juega patrullas con políticas fijas
(`mission_first`, `crew_first`, `paranoid`) y un **capitán aleatorio** (`random`)
sobre muchas semillas. El diseño es válido si:

1. **Obedecer lo inmoral se paga:** `mission_first` hunde al buque civil casi
   siempre y `crew_first` casi nunca; el primero acumula mucha más culpa y llega a
   un pavor máximo mucho mayor. Lo que hizo el barco alimenta a la presencia.
2. **Negarse y torcer también cuestan:** `crew_first` cumple menos órdenes tal como
   se dieron y recibe más veces "bajo una nube", pero conserva casco, cohesión y supervivencia.
3. **Finales variados:** el capitán aleatorio no acaba en el mismo final > 60 % de
   las semillas, ve ≥ 5 finales distintos, y todo final alcanzable se alcanza.
4. **Auditoría de ambigüedad:** ≥ 70 % de los eventos de actos I–II se disparan
   con la explicación mundana disponible (`mundane_when`).
5. **Sin muerte súbita:** el casco nunca baja de 0.3 antes del tick 24 con ninguna política.
6. **Sin contenido muerto:** cada evento del catálogo se dispara en alguna política.
7. **Determinismo:** misma semilla, misma patrulla.
8. **La presencia no desaparece con buena gestión:** toda política ve ≥ 2 pulsos
   y el primero antes del tick 30 en ≥ 95 % de las semillas; los pulsos severos
   los gana quien juega mal.

Todos son pruebas automáticas (`tests/test_dread_sim.py`, `tests/test_dread_missions.py`).

(El antiguo criterio "ninguna política termina en el mismo final > 80 %" se retiró:
con misiones morales, el final de una política determinista lo decide una elección
deliberada, que es justo lo que se quiere. La diversidad se mide con el capitán aleatorio.)

### Calibración actual (300 semillas, 4 misiones)

| Política | Órdenes cumplidas | Hunde al buque civil | Culpa | Cohesión | Casco | Dread máx. |
|---|---|---|---|---|---|---|
| `mission_first` | 76 % | 96 % | 0.42 | 0.46 | 0.20 | 0.82 |
| `crew_first` | 51 % | 0 % | 0.00 | 0.76 | 0.48 | 0.29 |
| `paranoid` | 63 % | 91 % | 0.40 | 0.55 | 0.40 | 0.51 |

Finales: `mission_first` 88 % `stained_victory`, 12 % pierde el barco; `crew_first`
55 % `returned_under_a_cloud`, 32 % `mission_failed`, 13 % `returned`.

Estos números son una **primera calibración**, no un objetivo. Lo que fijan los
tests son las relaciones entre políticas, no los valores absolutos.

### La presencia no desaparece con buena gestión

Dos mecanismos lo garantizan (criterio 8):

- **Piso de atención:** `attention` nunca baja de `0.25 × clamp((horas_sumergido − 10) / 60)`.
  Solo cuentan horas sumergido; salir a superficie pausa el reloj.
- **Pulsos obligatorios:** los eventos marcados `"beat": true` manifiestan a la
  presencia. Si pasan 14 ticks (desde el tick 8) sin ninguno, el siguiente sale
  forzosamente de entre los pulsos cuyos requisitos se cumplen.

### Problemas abiertos (conocidos)

- **Las políticas fijas siempre toman la misma decisión moral**, así que no dicen
  nada sobre cómo decide un humano; solo que ambas salidas tienen precio. Hay que jugarlo.
- **Obedecer es muy seguro:** `mission_first` pierde el barco solo el 12 %. La
  deuda moral se paga en horror y culpa, pero el jugador competente la sobrevive.
  Falta un castigo mecánico más directo (motín, sabotaje) en las misiones morales.
- **`crew_first` fracasa ≥ 3 misiones un tercio de las veces.** El coste del
  cuidado puede ser excesivo; solo un humano puede juzgarlo.
- **`court_martial` es raro con las políticas fijas** (nadie rehúsa de plano); solo
  aparece con el capitán aleatorio. No se sabe si el miedo al consejo de guerra
  pesará en un jugador real.
- **Los cuatro textos de misión son fijos** y la secuencia es siempre la misma.
  Generar misiones morales variadas (otro buque, otro dilema) está pendiente.
- **No está conectado al `QuestManager`** del juego (que hoy no se usa en el bucle):
  `DreadBridge.begin_mission(id)` queda como punto de enganche.
- Los pulsos se repiten (`footsteps_on_hull` ~2 veces por patrulla); faltan variantes de texto.

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
