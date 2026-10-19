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

### 7.4 El endgame: la Estación

> **No hay batalla contra la presencia. Nunca.** Lo que cierra el juego es una
> decisión con coste irreversible, tomada con la máxima incertidumbre, que lee todo
> lo que la patrulla dejó atrás.

La misión 5, *Mantener el sector hasta nuevo aviso*, no tiene barra de progreso ni
ventana. Su reloj es la despensa. Procedencia: calidad 0.05 (una frecuencia que el
radiotelegrafista jura no haber sintonizado, con la misma firma que la primera orden).

**El libro de existencias es honrado; las personas, no.** Comida, agua, gasóleo,
absorbente y raciones se muestran exactos. El calendario no: en la estación el diario,
el cronómetro y el cocinero no coinciden en el día. Bajo el 20 % de víveres hay miedo,
fatiga y desconfianza; a cero, muere un hombre cada 8 horas.

**Dos verdades ocultas, fijadas por semilla con dados propios** (no alteran nada de
lo anterior): `war_over` (50 %: la guerra terminó y nadie avisó) y `notice_at`
(a las 50–150 horas de vigilia llega el «nuevo aviso»; nunca llega si la guerra terminó).
El jugador no puede saber cuál es su mundo, salvo escuchando.

El **Consejo de estación** vuelve cada pocas horas y ofrece siempre las mismas salidas,
cada una con su precio:

| Salida | Cómo | Qué cuesta | Qué puede darte |
|---|---|---|---|
| **Mantener** | seguir; opcionalmente recortar raciones | víveres, cordura; el motín vive aquí | un aviso que llegue (y vuelta legal) |
| **Escuchar el mundo** | subir a superficie y sintonizar | exposición aérea (si hay guerra) | si la guerra terminó, **vuelta legal inmediata**; si no, estática |
| **Volver** | 18 h, gasóleo ≥ 25 % | sin aviso es **desobediencia** (si consta); recuento desajustado | salir |
| **La ofrenda** | la propone la tripulación; ver abajo | `moral_debt` +0.5, un hombre menos | un aviso en 6 h, siempre |

**La ofrenda.** Cuando hay deuda (`owed`, `moral_debt`, nombres aprendidos) y miedo, los
hombres vienen a decir que el mar deja ir a un barco cuando se le ha pagado. Tres
respuestas: *prohibirlo* (una de cada cuatro veces lo hacen igual), *mirar a otro lado* (se
ofrece el más culpable) o *dar un nombre* (el que más problemas da: no es casualidad).
**Nunca se sabe si la presencia pidió algo o si fue un asesinato por superstición.**
Es la regla de oro en su forma más pura.

**El mar da.** Una red llena de peces iguales, un chubasco de cielo despejado. Aceptar es
comer, y también deber (`owed`). Rechazar es pasar hambre con la tripulación mirando.

**La vuelta** es un viaje con sus propios eventos (cartas que se actualizan con
reportes falsos, un eco que mantiene la distancia, un muelle a oscuras con un
hombre esperando). Al llegar, que el recuento cuadre depende de lo que se debe:
`p = 0.08 + 0.35·owed + 0.2·(náufragos o hombre de más) + 0.03·nombres_aprendidos` (máx. 0.8).

**Descanso general** (`stand_down`): una tripulación rota se recupera si todos duermen
menos una guardia mínima. Cuesta disciplina y **alimenta a la presencia** (un barco que
duerme es un barco que nadie vigila). Existe para que ninguna espiral sea un callejón sin salida.

**La última escena es el silencio:** los hidrófonos dejan de oír, hasta los ecos
fantasma que fueron el motor de todo. Después, los dos informes.

## 8. Finales (estados, no escenas)

Derivados del estado final (`dread/endings.py: classify_ending`). Los veredictos del
endgame **tienen prioridad** sobre los demás, porque leen toda la patrulla.

| Final | Cuándo |
|---|---|
| `derelict` | casco 0 o sin tripulación, estando en la estación: el barco aparece a la deriva |
| `lost_with_all_hands` | lo mismo, antes de llegar a la estación |
| `deposed` | motín consumado |
| `turned_back` | se abortó la patrulla (antes de la estación) |
| `the_price` | se hizo la ofrenda |
| `home_unaccounted` | se volvió y el recuento no cuadra |
| `forgotten_post` | se supo de la paz y se volvió: *«nadie canceló tus órdenes porque no quedaba nadie»* |
| `stained_victory` | se hundió al buque civil: la tripulación lo sabe aunque el registro no lo diga |
| `court_martial` | se desobedeció una orden que *consta* en los registros |
| `returned_under_a_cloud` | se torció una orden que *consta* |
| `returned` | sin sangre en el diario ni expediente |
| `hollow_victory` | misiones cumplidas con cohesión < 0.3 o menos del 60 % de la tripulación |
| `mission_failed` | menos de 3 misiones cumplidas |

**El epílogo de todos los finales termina igual**: *los hidrófonos callan; no es el
silencio de un mar vacío, sino el de algo que ha dejado de escuchar.* Y después, **dos
documentos lado a lado, fila por fila**: el informe oficial (todo tiene explicación,
`mundane_*`) y el diario del capitán (nada la tiene, `uncanny_*`). Nadie los reconcilia.

## 9. Criterios de aceptación del bucle

El simulador (`python -m dread.sim`) juega patrullas con políticas fijas
(`mission_first`, `crew_first`, `paranoid`) y un **capitán aleatorio** (`random`)
sobre muchas semillas, y además un **experimento controlado de la estación**
(`run_station`) que parte todas las estrategias del mismo estado. El diseño es válido si:

1. **Obedecer lo inmoral se paga:** `mission_first` hunde al buque civil casi
   siempre y `crew_first` casi nunca; el primero acumula mucha más culpa y llega a
   un pavor máximo mucho mayor. Lo que hizo el barco alimenta a la presencia.
2. **Negarse y torcer también cuestan:** `crew_first` cumple menos órdenes tal como
   se dieron, casi nadie vuelve con las manos limpias, pero conserva casco y cohesión.
3. **Finales variados:** el capitán aleatorio no acaba en el mismo final > 60 % de
   las semillas, ve ≥ 5 finales distintos, y los finales del endgame son alcanzables.
4. **Auditoría de ambigüedad:** ≥ 70 % de los eventos de actos I–II se disparan
   con la explicación mundana disponible (`mundane_when`).
5. **Sin muerte súbita:** el casco nunca baja de 0.3 antes del tick 24 con ninguna política.
6. **Sin contenido muerto:** cada evento del catálogo se dispara en alguna política.
7. **Determinismo:** misma semilla, misma patrulla. **Mirar la pantalla no cambia la partida**
   (el HUD no consume los dados del mundo).
8. **La presencia no desaparece con buena gestión:** toda política ve ≥ 2 pulsos
   y el primero antes del tick 30 en ≥ 95 % de las semillas; los pulsos severos
   los gana quien juega mal.
9. **Cada salida de la estación tiene un precio propio** (experimento controlado):
   irse sin aviso casi siempre acaba en consejo de guerra; escuchar primero es la única
   vía a `forgotten_post` y baja ese riesgo; pagar es la única vía a `the_price` en ≥ 30 %;
   mantener es donde vive el motín; ninguna estrategia acaba en lo mismo > 85 %.
10. **Esperar órdenes no es seguro:** quien se queda «como se ordenó» termina en barco a la
    deriva, ofrenda o pérdida ≥ 70 % de las veces.
11. **Ningún valor oculto llega a la pantalla** (ver sección 12).

Todos son pruebas automáticas (`tests/test_dread_sim.py`, `test_dread_missions.py`,
`test_dread_endgame.py`, `test_dread_ui.py`).

(El antiguo criterio «ninguna política termina en el mismo final > 80 %» se retiró:
con misiones morales, el final de una política determinista lo decide una elección
deliberada, que es lo que se quiere. La diversidad se mide con el capitán aleatorio.)

### Calibración actual (300 semillas, 5 misiones)

| Política | Órdenes cumplidas | Hunde al buque civil | Culpa | Cohesión | Casco | Supervivencia | Dread máx. |
|---|---|---|---|---|---|---|---|
| `mission_first` | 79 % | 97 % | 0.70 | 0.24 | 0.09 | 0.79 | 0.85 |
| `crew_first` | 71 % | 0 % | 0.02 | 0.75 | 0.67 | 0.92 | 0.38 |
| `paranoid` | 80 % | 95 % | 0.76 | 0.10 | 0.18 | 0.89 | 0.90 |

Finales: `mission_first` 51 % `derelict`, 28 % `the_price`, 10 % `lost_with_all_hands`, 8 % `home_unaccounted`.
`crew_first` 36 % `home_unaccounted`, 27 % `forgotten_post`, 14 % `returned_under_a_cloud`, 11 % `returned`, 10 % `the_price`.
`paranoid` 49 % `the_price`, 39 % `derelict`.

### El experimento controlado de la estación (300 semillas, mismo estado inicial)

| Estrategia | Finales principales | Supervivencia |
|---|---|---|
| `hold` (mantener) | 44 % `court_martial` (el motín lo saca de allí), 19 % `home_unaccounted`, 16 % `deposed`, 14 % `the_price` | 0.93 |
| `leave_now` | 80 % `court_martial`, 20 % `home_unaccounted` | 0.96 |
| `listen_then_leave` | 32 % `forgotten_post`, 24 % `court_martial`, 23 % `home_unaccounted` | 0.93 |
| `pay` (ofrenda) | 48 % `the_price`, 33 % `court_martial` | 0.90 |

**Lo que se aprende:** con el mismo estado, la supervivencia casi no distingue las
salidas (0.90–0.96). **Las salidas difieren en el veredicto, no en quién vive.** Eso es
coherente con el diseño (no hay batalla), pero significa que el coste de cada salida
es moral y legal, y que su peso tiene que sentirlo el jugador en el texto, no en una barra.

Estos números son una **primera calibración**, no un objetivo. Lo que fijan los
tests son las relaciones entre estrategias, no los valores absolutos.

### La presencia no desaparece con buena gestión

- **Piso de atención:** `attention` nunca baja de `0.25 × clamp((horas_sumergido − 10) / 60)`.
- **Pulsos obligatorios:** los eventos `"beat": true` manifiestan a la presencia; si pasan
  14 ticks sin ninguno, el siguiente sale de entre los pulsos cuyos requisitos se cumplen.

### Problemas abiertos (conocidos)

- **Las políticas fijas no son jugadores.** Las diferencias entre ellas vienen en buena parte
  del estado con el que llegan a la estación; por eso existe el experimento controlado.
  Hay que jugarlo a mano antes de fiarse de cualquier número.
- **`hollow_victory` ya no se alcanza** en el simulador (el endgame lo desplaza) y `deposed`
  y `court_martial` son raros con políticas fijas.
- **Escuchar primero es casi siempre lo correcto** si el jugador cree en la posibilidad de
  una paz ignorada. El único coste real es la exposición aérea y las 3 horas en superficie.
  Falta un precio más pesado a escuchar (p. ej. oír cosas que no son la radio).
- **La ofrenda nunca es necesaria para sobrevivir**: tiene que ser una tentación. En el
  experimento no mejora la supervivencia. Quizá deba acelerar mucho más la salida cuando
  la despensa está baja.
- **El libro de existencias solo tiene sentido en la estación**; en las misiones 1–4 casi
  no pesa (no llega a escasear).
- **El mapa de contenido es corto**: 5 misiones fijas, 3 eventos de viaje y 1 escena de ofrenda.
- **No está conectado al `QuestManager`** del juego (que hoy no se usa en el bucle):
  `DreadBridge.begin_mission(id)` es el punto de enganche. La estación aún no puede
  arrancarse desde el juego en vivo (usa `begin_mission("m5_station")`, sin probar con tcod).
- Los pulsos se repiten (`footsteps_on_hull`); faltan variantes de texto.

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

## 12. UX / UI

> **Principio rector: el libro de existencias es honrado; las personas no.**
> El jugador planifica con cifras fiables y decide con información que miente.

Hay un prototipo jugable en terminal que aplica todo esto:
`python -m dread.play` (interactivo) o `python -m dread.play --auto crew_first` (ver jugar a una política).
La lógica de pantalla vive en `dread/hud.py` (funciones puras: mundo → texto) para que
cualquier interfaz (la actual de tcod incluida) pueda consumirla.

### 12.1 Reglas de información

| Se muestra **exacto** | Se muestra **filtrado** | **Nunca** se muestra |
|---|---|---|
| Casco, víveres, agua, gasóleo, absorbente, CO₂, raciones, hombres a bordo | Cada hombre: lo que *dice* (cuatro frases) y lo que *se ve* (síntomas, con probabilidad) | `fear`, `guilt`, `trust`, `attention`, `moral_debt`, `orders_doubt`, `owed`, `war_over`, `notice_at`, nombres aprendidos |
| Procedencia de las órdenes (canal, firma) | El sonar: lo que el operador decide contar | `mundane_*` / `uncanny_*` (solo en el epílogo) |
| Consumo diario de víveres | El calendario: el cronómetro, el diario y el cocinero no coinciden | Probabilidades de cualquier tirada |

**Ni un número sobre las personas.** Lo comprueba un test (`test_the_ledger_is_exact_and_the_people_are_not`).
La brecha entre «dice que está bien» y «habla solo» es el juego.

### 12.2 Pantalla del puente

Una pantalla, de arriba abajo por orden de urgencia: **órdenes y reloj → libro de existencias
→ los hombres → sonar → diario → menú de órdenes o decisión**. Captura real de una partida
(día 5, en la estación, con el absorbente agotado y el aire «foul»):

```
==============================================================================
ORDERS: Hold the sector until further notice
Received: Received on a frequency the radio man swears he never tuned. It
  repeats every six hours, word for word. The same call sign as the first
  order. A different voice each time.
Day 5  ·  chronometer 04:00  ·  control-room clock 04:00 less eleven minutes
Day by the log: 5.  Day by the chronometer: 6.  The cook says it is later.
==============================================================================
LEDGER (exact)
  Hull      [#########.]  89%      Diesel    [##########]  99%
  Food      [######....]  60%  (-6%/day)    Rations   75%
  Water     [#####.....]  53%  (-8%/day)    Absorbent [..........]   0%
  Air       CO2 3.1% (foul)    Men aboard: 12

THE MEN (what they say, what you can see)
  Brandt   sonar    says he is fine.  Seen: repeats rumors.
  Keller   torpedo  says he is fine.  Seen: nothing you can see.
  Vogel    engine   says he is fine.  Seen: nothing you can see.
  Hahn     helm     says he is fine.  Seen: nothing you can see.
  Lenz     radio    says he is fine.  Seen: nothing you can see.
  Ostrow   medic    says he is fine.  Seen: nothing you can see.
  Weiss    cook     says he is fine.  Seen: nothing you can see.
  Maier    deck     says he is fine.  Seen: nothing you can see.
  Fuchs    sonar    says he is fine.  Seen: nothing you can see.
  Reiter   torpedo  says he is fine.  Seen: nothing you can see.
  Arndt    engine   says he is fine.  Seen: nothing you can see.
  Kopp     helm     says he is fine.  Seen: nothing you can see.

SONAR: ON
  Brandt reports: "...-- sunk three days ago, still sending"

LOG
[089] A squall out of a clear sky, just long enough to fill every tank, and
      gone. The sky is as empty as before.
```

Fíjate en lo que ocurre ahí: **el libro grita** (absorbente 0 %, aire 3,1 %) mientras
**los hombres dicen que están bien**. Quien solo lee lo que le dicen, pierde.

### 12.3 Modelo de interacción

- **Tiempo:** `Enter` = una hora; `w` = esperar hasta que ocurra algo (máx. 12 h). La estación
  se juega a **jornadas**, no a horas: `w` es el modo normal.
- **Las decisiones detienen el reloj.** Una decisión es un modal con opciones numeradas, cada una
  con su **coste en una línea** entre paréntesis (qué pierdes), no su efecto. No se avanza hasta responder.
- **Las órdenes del capitán** son un menú numerado con una **pista de coste cualitativa**
  («rápido ahora; lento después», «cuesta horas», «se acordará»). Cada orden cuesta; el
  juego lo dice sin detallar.
- **Las órdenes que nombran a un hombre** preguntan *¿cuál?* (confinar, liberar, forzar).
- **Nada se explica.** No hay tooltips con porcentajes. El jugador aprende mirando.

### 12.4 El epílogo

Un solo final de pantalla: el texto del final, la frase del silencio, y **los dos informes lado a lado,
fila por fila**: el oficial (todo explicable) a la izquierda, el diario (nada lo es) a la derecha.
Sin árbitro: *«nadie ha pedido que se reconcilien»*.

### 12.5 Conectado a la ventana de tcod (MVP)

El HUD ya está conectado al juego real. **Cómo probarlo:** `python main.py --quick` (o `python main.py`)
y, dentro de la ventana:

| Tecla | Qué hace |
|---|---|
| `TAB` | abre/cierra el **puente del capitán** (libro de existencias, los hombres, el sonar, el diario, las órdenes) |
| número + `Enter` | da esa orden (dos dígitos como máximo); `Enter`/`Espacio` en el puente = esperar una hora |
| `W` | esperar hasta que ocurra algo (máx. 12 h); funciona también en el mapa |
| `1`–`9` ante una decisión | responde; **el reloj se detiene hasta que se responde** |
| `Esc` en el puente | vuelve al mapa; `Q` sale |
| al acabar la patrulla | `↑↓` / `RePág AvPág` para leer el epílogo; `Q` sale |

`DREAD_MISSIONS=0` ejecuta el modelo de horror sin la historia de las cinco misiones.
Sin ventana (CI, SSH, entorno en la nube): `python tools/dread_preview.py DIRECTORIO` juega
una patrulla por el juego real y guarda PNG de lo que dibujaría la ventana.

**Dónde está cada cosa:** `dread/hud.py` produce el texto (funciones puras); `ui/dread_ui.py` lo coloca,
le asigna color y encamina las teclas; `engine/game.py` le cede las teclas antes que al mapa;
`ui/panels/panel_manager.py` dibuja la capa encima del mapa.

**Cambios hechos al pasarlo a la ventana (todos por las reglas de la sección 12.1):**
- La cabecera mostraba `Stage: <etapa de horror>`: **un valor oculto**. Ahora muestra el día.
- Al cambiar de etapa el modelo anunciaba «THE TRUTH IS UNDENIABLE. SOMETHING IS DOWN HERE WITH US»:
  filtraba la etapa *y* confirmaba lo sobrenatural. En el modelo nuevo no se anuncia nada.
- La tecla `B` también imprimía la etapa. Ahora imprime el día.
- **El modo gráfico no tenía forma de responder decisiones** (`1`–`4` son velocidades). Ahora hay un modal.
- Paleta: azul marino, gris acero, ámbar solo para alarmas del libro; ninguna información va solo en color.

**Limitaciones conocidas del MVP:**
- **Dos libros de existencias conviven.** La cabecera del mapa sigue mostrando las baterías y el O₂ del
  simulador táctico; el puente muestra los víveres, el gasóleo, el absorbente y el CO₂ del modelo de
  horror. No están unificados.
- **Las misiones son una capa narrativa.** Hundir «al acorazado» en la historia no exige hundir un buque en el
  mapa táctico, ni al revés. Los combates de destructores programados están desactivados en el juego en vivo.
- **Sumergirse arranca el reloj:** el juego empieza en superficie; se fija una profundidad objetivo de 60 m para
  que la patrulla corra desde el primer momento. En superficie no avanza la misión.
- **Probado sin abrir la ventana SDL** (consola de tcod sin pantalla + capturas PNG + 13 pruebas de teclas y
  pantalla). Falta jugarlo en un escritorio de verdad: tamaño de fuente, ratón, redimensionado.
- La paleta no se ha comprobado contra daltonismo.
- Faltan el **audio** (los fantasmas del sonar son texto; el silencio final no se oye) y un panel del
  puente que no tape el mapa táctico.

## 13. Referencias

Lovecraft, *El templo*; McCammon, *The Night Boat*; Buchheim, *Das Boot*
(rutina, claustrofobia real); Simmons, *El terror*; Crichton, *Esfera*;
Armfield, *Our Wives Under the Sea*; Hodgson, *The Ghost Pirates*.
Juegos: Barotrauma, Iron Lung, SOMA, Sunless Sea, Return of the Obra Dinn
(el diario inconsistente), Still Wakes the Deep, el estrés de Darkest Dungeon.
