/* Depths Within: the dread engine, ported line by line from dread/*.py.
 *
 * It is a port, not a rewrite: same names (snake_case where the data files use them), same
 * order of operations, and the same random numbers. `PyRandom` reproduces CPython's
 * Mersenne Twister (seeding, random(), choice(), choices(), randint(), uniform()), and
 * `fsum` reproduces the compensated float sum that Python 3.12+ uses in sum(). Given the same
 * seed and the same inputs, the log it writes is the log the Python engine writes
 * (tests/test_web_parity.py checks that, on the shipped file).
 *
 * No DOM in here, so Node can run it.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Dread = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ---------------------------------------------------------------- Python's random
  class PyRandom {
    constructor(seed) {
      this.mt = new Uint32Array(624);
      this.idx = 624;
      this.seed(seed);
    }
    _initGenrand(s) {
      const mt = this.mt;
      mt[0] = s >>> 0;
      for (let i = 1; i < 624; i++) {
        const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = (Math.imul(1812433253, prev) + i) >>> 0;
      }
    }
    seed(n) {
      n = Math.abs(n);
      const key = [];
      if (n === 0) key.push(0);
      while (n > 0) { key.push(n % 4294967296); n = Math.floor(n / 4294967296); }
      this._initGenrand(19650218);
      const mt = this.mt;
      let i = 1, j = 0;
      for (let k = Math.max(624, key.length); k > 0; k--) {
        const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ Math.imul(prev, 1664525)) + key[j] + j) >>> 0;
        i++; j++;
        if (i >= 624) { mt[0] = mt[623]; i = 1; }
        if (j >= key.length) j = 0;
      }
      for (let k = 623; k > 0; k--) {
        const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ Math.imul(prev, 1566083941)) - i) >>> 0;
        i++;
        if (i >= 624) { mt[0] = mt[623]; i = 1; }
      }
      mt[0] = 0x80000000;
      this.idx = 624;
    }
    _next() {
      const mt = this.mt;
      if (this.idx >= 624) {
        let kk = 0, y;
        for (; kk < 624 - 397; kk++) {
          y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
          mt[kk] = mt[kk + 397] ^ (y >>> 1) ^ ((y & 1) ? 0x9908b0df : 0);
        }
        for (; kk < 623; kk++) {
          y = (mt[kk] & 0x80000000) | (mt[kk + 1] & 0x7fffffff);
          mt[kk] = mt[kk + (397 - 624)] ^ (y >>> 1) ^ ((y & 1) ? 0x9908b0df : 0);
        }
        y = (mt[623] & 0x80000000) | (mt[0] & 0x7fffffff);
        mt[623] = mt[396] ^ (y >>> 1) ^ ((y & 1) ? 0x9908b0df : 0);
        this.idx = 0;
      }
      let y = mt[this.idx++];
      y ^= y >>> 11;
      y ^= (y << 7) & 0x9d2c5680;
      y ^= (y << 15) & 0xefc60000;
      y ^= y >>> 18;
      return y >>> 0;
    }
    random() {
      const a = this._next() >>> 5, b = this._next() >>> 6;
      return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
    }
    _getrandbits(k) { return k === 0 ? 0 : this._next() >>> (32 - k); }
    _randbelow(n) {
      if (!n) return 0;
      const k = 32 - Math.clz32(n);
      let r = this._getrandbits(k);
      while (r >= n) r = this._getrandbits(k);
      return r;
    }
    choice(seq) { return seq[this._randbelow(seq.length)]; }
    randint(a, b) { return a + this._randbelow(b - a + 1); }
    uniform(a, b) { return a + (b - a) * this.random(); }
    /** random.choices(population, weights, k=1)[0] */
    choices1(population, weights) {
      const cum = [];
      let acc = 0;
      weights.forEach((w, i) => { acc = i === 0 ? w : acc + w; cum.push(acc); });
      const total = cum[cum.length - 1] + 0.0;
      let lo = 0, hi = population.length - 1;
      const x = this.random() * total;
      while (lo < hi) {                       // bisect_right(cum, x, 0, hi)
        const mid = (lo + hi) >> 1;
        if (x < cum[mid]) hi = mid; else lo = mid + 1;
      }
      return population[lo];
    }
  }

  // ---------------------------------------------------------------- numeric helpers
  const clamp = (x, lo = 0.0, hi = 1.0) => Math.max(lo, Math.min(hi, x));
  const lerp = (a, b, t) => a + (b - a) * t;

  /** Python 3.12+ sum() of floats: Neumaier compensated summation. */
  function fsum(arr) {
    if (arr.length === 0) return 0;
    let f = arr[0], c = 0.0;
    for (let i = 1; i < arr.length; i++) {
      const x = arr[i], t = f + x;
      if (Math.abs(f) >= Math.abs(x)) c += (f - t) + x; else c += (x - t) + f;
      f = t;
    }
    if (c && Number.isFinite(c)) f += c;
    return f;
  }
  /** max()/min() with Python's tie rule: the first one wins. */
  function maxBy(arr, key) {
    let best = arr[0], bk = key(best);
    for (let i = 1; i < arr.length; i++) { const k = key(arr[i]); if (k > bk) { best = arr[i]; bk = k; } }
    return best;
  }
  function minBy(arr, key) {
    let best = arr[0], bk = key(best);
    for (let i = 1; i < arr.length; i++) { const k = key(arr[i]); if (k < bk) { best = arr[i]; bk = k; } }
    return best;
  }
  const pad3 = (n) => String(n).padStart(3, '0');
  const tag = (t) => `[${pad3(t)}]`;

  // ---------------------------------------------------------------- data
  let DATA = null;
  function setData(data) {
    DATA = {
      events: data.events.map((e) => e),
      missions: data.missions.map((m) => ({
        id: m.id, kind: m.kind, ticks: m.ticks, moral: !!m.moral, title: m.title, briefing: m.briefing,
        channel: (m.provenance && m.provenance.channel) || '', signed: (m.provenance && m.provenance.signed) || '',
        quality: (m.provenance && m.provenance.quality !== undefined) ? m.provenance.quality : 0.5,
        mundane_origin: m.mundane_origin, uncanny_origin: m.uncanny_origin,
        window: m.window !== undefined ? m.window : 1.8,
        chart: m.chart || null,
        acts: (m.acts || []).map((a) => ({
          id: a.id, label: a.label, hint: a.hint || '', hours: Number(a.hours),
          needs: a.needs || [], effects: a.effects || [],
        })),
      })),
    };
  }
  const provenanceLine = (m) => `${m.channel} ${m.signed}`.trim();

  // ---------------------------------------------------------------- state (dread/state.py)
  const ROLES = ['sonar', 'torpedo', 'engine', 'helm', 'radio', 'medic', 'cook', 'deck'];
  const COMPARTMENTS = ['bow torpedo room', 'control room', 'crew quarters', 'engine room', 'after torpedo room'];
  const ROUTINE_ITEMS = ['meals', 'music', 'cards', 'coffee', 'watches'];

  class Crew {
    constructor(id, name, role, section, candor) {
      Object.assign(this, {
        id, name, role, section, candor, fear: 0.1, fatigue: 0.1, guilt: 0.0, trust: 0.8,
        alive: true, missing: false, isolated: false, isolated_ticks: 0, name_known: false,
        ill: false, hides: false, ill_ticks: 0,
      });
      this.believes = new Set();
    }
    get active() { return this.alive && !this.missing; }
    stress() { return clamp(0.45 * this.fear + 0.35 * this.fatigue + 0.20 * this.guilt); }
    reported(cohesion) {
      const candorEff = clamp(this.candor * this.trust * (0.6 + 0.4 * cohesion));
      return lerp(0.15, this.stress(), candorEff);
    }
    symptoms() {
      const out = [];
      if (this.fear > 0.5) out.push('jumpy');
      if (this.fear > 0.7) out.push('talks to himself');
      if (this.fatigue > 0.6) out.push('errors at station');
      if (this.fatigue > 0.8) out.push('microsleeps');
      if (this.guilt > 0.5) out.push('avoids eyes');
      if (this.trust < 0.4) out.push('silent when the captain speaks');
      if (this.guilt > 0.4 && this.fear > 0.4) out.push('leaves small offerings');
      if (this.believes.size > 0 && this.fear > 0.3) out.push('repeats rumors');
      if (this.ill && !this.hides) out.push('feverish');
      return out;
    }
  }

  class Rumor {
    constructor(id, text, intensity, drift) {
      this.id = id; this.text = text; this.intensity = intensity;
      this.believers = new Set(); this.drift = drift || {};
    }
  }

  class Ship {
    constructor() {
      Object.assign(this, {
        cohesion: 0.8, discipline: 0.7, hull: 1.0, readiness: 1.0, co2: 0.005, noise: 0.1,
        attention: 0.0, progress: 0.0, food: 1.0, water: 1.0, fuel: 1.0, rations: 1.0,
        returning: false, owed: 0.0, orders_doubt: 0.0, moral_debt: 0.0, scrubber: 1.0,
        sonar_on: true, silent_running: false, surfaced: false, rest_cancelled: false,
        stand_down: false, hours_submerged: 0, torpedoes: 12, scope_up: false, decoys: 4,
        dr_error: 0.0, last_fix: 0, last_log: -99, log_true: 0, log_soft: 0, log_blank: 0,
        speed_order: 'standard', depth_order: 'shallow', depth_extra: 0, dive_lag: 0, torpedo_type: 'steam', shot_type: 'steam', battery: 1.0, snorkel: false, spares: 1.0, dc_active: false,
        helm_pending: null, helm_lag: 0,
      });
      this.tubes = ['loaded', 'loaded', 'loaded', 'loaded', 'loaded', 'loaded'];
      this.types = { steam: 6, electric: 4, acoustic: 2 };
      this.damage = {};
      COMPARTMENTS.forEach((c) => { this.damage[c] = 0.0; });
      this.routines = {};
      ROUTINE_ITEMS.forEach((k) => { this.routines[k] = 0.9; });
      this.flags = new Set();
      this.rumors = new Map();
    }
    get routine() {
      const v = Object.values(this.routines);
      return fsum(v) / v.length;
    }
  }

  function dreadIndex(ship, crew) {
    const live = crew.filter((c) => c.active);
    if (!live.length) return 1.0;
    const n = live.length;
    const fear = fsum(live.map((c) => c.fear)) / n;
    const guilt = fsum(live.map((c) => c.guilt)) / n;
    const trust = fsum(live.map((c) => c.trust)) / n;
    const fatigue = fsum(live.map((c) => c.fatigue)) / n;
    const co2Pressure = clamp((ship.co2 - 0.005) / 0.025);
    return clamp(0.30 * fear + 0.15 * guilt + 0.15 * (1 - trust) + 0.15 * fatigue
      + 0.10 * co2Pressure + 0.15 * (1 - ship.routine));
  }

  // ---------------------------------------------------------------- conditions
  const OPS = {
    '>': (a, b) => a > b, '>=': (a, b) => a >= b, '<': (a, b) => a < b,
    '<=': (a, b) => a <= b, '==': (a, b) => a === b, '!=': (a, b) => a !== b,
  };

  function resolvePath(path, world) {
    const parts = path.split('.');
    const head = parts[0];
    if (head === 'ship') return Number(world.ship[parts[1]]);
    if (head === 'world') return Number(world[parts[1]]);
    if (head === 'crew') {
      const live = world.active_crew();
      const kind = parts[1];
      if (kind === 'count') return live.length;
      const vals = live.map((c) => c[parts[2]]);
      if (!vals.length) return 0.0;
      if (kind === 'avg') return fsum(vals) / vals.length;
      if (kind === 'max') return Math.max(...vals);
      return Math.min(...vals);
    }
    if (head === 'dread') return world.dread();
    throw new Error(`unknown path ${path}`);
  }

  const isEmpty = (o) => o && typeof o === 'object' && !Array.isArray(o) && Object.keys(o).length === 0;

  function evaluate(cond, world) {
    if (cond === null || cond === undefined || isEmpty(cond)) return true;
    if ('never' in cond) return false;
    if ('all' in cond) return cond.all.every((c) => evaluate(c, world));
    if ('any' in cond) return cond.any.some((c) => evaluate(c, world));
    if ('not' in cond) return !evaluate(cond.not, world);
    if ('path' in cond) return OPS[cond.op](resolvePath(cond.path, world), cond.value);
    if ('flag' in cond) return world.ship.flags.has(cond.flag);
    if ('no_flag' in cond) return !world.ship.flags.has(cond.no_flag);
    if ('crew_where' in cond) {
      const w = cond.crew_where;
      const op = OPS[w.op || '>='];
      for (const c of world.active_crew()) {
        if ('role' in w && c.role !== w.role) continue;
        if ('stat' in w && !op(c[w.stat], w.value)) continue;
        return true;
      }
      return false;
    }
    if ('mission' in cond) {
      const want = Array.isArray(cond.mission) ? cond.mission : [cond.mission];
      return world.run !== null && want.includes(world.run.mission.id);
    }
    if ('outcome' in cond) return world.ship.flags.has(`outcome:${cond.outcome.mission}:${cond.outcome.is}`);
    if ('phantom' in cond) return world.deck.phantoms.some((p) => p.kind === cond.phantom);
    if ('rumor' in cond) {
      const r = world.ship.rumors.get(cond.rumor);
      if (!r) return false;
      return r.believers.size >= (cond.believers_gte !== undefined ? cond.believers_gte : 1);
    }
    throw new Error(`unknown condition ${JSON.stringify(cond)}`);
  }

  // ---------------------------------------------------------------- phantom sonar
  const VOICE_LINES = [
    '{name}... {name}... come up here.', "{name}, it's cold. Open the hatch.",
    'Why did you leave me, {name}?', '{name}. {name}. {name}.',
  ];
  const ECHO_LINES = ['an echo that keeps pace with us, then slows', 'a slow return moving against the current',
    'something that breathes in time with the screws'];
  const MORSE_LINES = ['...-- sunk three days ago, still sending', 'recall order, signed by a dead officer',
    'a list of names, one of them still aboard'];
  const fillName = (s, name) => s.split('{name}').join(name);

  class SonarDeck {
    constructor() {
      this.phantoms = []; this.names_learned = new Set(); this._next_id = 1; this.sonar_off_ticks = 0;
    }
    spawn(kind, audible, intensity, text, rng, crew) {
      if (!text) text = this._textFor(kind, rng, crew);
      const p = { id: this._next_id, kind, audible_to: new Set(audible), intensity, age: 0, text };
      this._next_id += 1;
      this.phantoms.push(p);
      return p;
    }
    _textFor(kind, rng, crew) {
      if (kind === 'voice') {
        const names = (crew || []).filter((c) => this.names_learned.has(c.id) && c.active).map((c) => c.name);
        const name = names.length && rng ? rng.choice(names) : 'someone';
        return fillName(rng ? rng.choice(VOICE_LINES) : VOICE_LINES[0], name);
      }
      const pool = kind === 'echo' ? ECHO_LINES : MORSE_LINES;
      return rng ? rng.choice(pool) : pool[0];
    }
    tick(world) {
      const ship = world.ship, rng = world.rng, crew = world.crew;
      const live = world.active_crew();
      if (ship.sonar_on) this.sonar_off_ticks = 0; else this.sonar_off_ticks += 1;
      for (const p of this.phantoms.slice()) {
        p.age += 1;
        p.intensity = clamp(p.intensity + 0.02 * ship.attention - 0.006);
        if (p.intensity <= 0.0) { this.phantoms.splice(this.phantoms.indexOf(p), 1); continue; }
        if (p.intensity > 0.6 && rng.random() < 0.08) {
          const cand = live.filter((c) => !p.audible_to.has(c.id));
          if (cand.length) p.audible_to.add(maxBy(cand, (c) => c.fear + c.fatigue).id);
        }
        if (ship.sonar_on) {
          for (const cid of Array.from(p.audible_to).sort((a, b) => a - b)) {
            const c = world.crew_by_id(cid);
            if (!c || !c.active) continue;
            c.fear = clamp(c.fear + 0.012 * p.intensity);
            c.fatigue = clamp(c.fatigue + 0.004);
            if (p.kind === 'voice' && rng.random() < 0.15 * p.intensity) {
              this.names_learned.add(c.id);
              c.name_known = true;
              ship.attention = clamp(ship.attention + 0.01);
            }
          }
        } else {
          const liveIds = new Set(live.map((x) => x.id));
          let heard = 0;
          p.audible_to.forEach((c) => { if (liveIds.has(c)) heard += 1; });
          if (heard >= 2) for (const c of live) c.trust = clamp(c.trust - 0.002);
        }
      }
      const sonarOps = live.filter((c) => c.role === 'sonar');
      if (sonarOps.length && this.phantoms.length < 4) {
        const op = maxBy(sonarOps, (c) => c.fear + c.fatigue);
        const deep = world.depth_m >= 120;
        const pSpawn = 0.01 + 0.05 * ship.attention + 0.015 * (op.fear + op.fatigue) + (deep ? 0.02 : 0.0);
        if (ship.sonar_on && rng.random() < pSpawn) {
          let kind = rng.choice(deep ? ['echo', 'voice', 'voice', 'morse'] : ['echo', 'echo', 'voice', 'morse']);
          if (kind === 'voice' && this.names_learned.size === 0) kind = 'echo';
          this.spawn(kind, [op.id], 0.3, '', rng, crew);
        }
      }
    }
    mute_all() {
      for (const p of this.phantoms) p.intensity = clamp(p.intensity - 0.15);
      this.phantoms = this.phantoms.filter((p) => p.intensity > 0.0);
    }
  }

  // ---------------------------------------------------------------- events
  const GLOBAL_COOLDOWN = 3, BEAT_GAP = 14, BEAT_START = 8;
  const SHIP_CLAMP = { co2: [0.0, 0.1], dr_error: [0.0, 40.0] };

  class EventEngine {
    constructor(events, useSchedule) {
      this.use_schedule = useSchedule;
      this.events = events;
      this.byId = new Map(events.map((e) => [e.id, e]));
      this.last_fired = new Map();
      this.last_any = -99;
      this.last_beat = 0;
    }
    select(world) {
      const t = world.tick_no, act = world.act();
      const run = world.run;
      if (run !== null) {
        const due = this.events.filter((e) => e.mission === run.mission.id && 'at_progress' in e
          && !run.phase_fired.has(e.id) && world.ship.progress >= e.at_progress && evaluate(e.requires, world));
        if (due.length) return minBy(due, (e) => e.at_progress);
      }
      const scheduled = this.events.filter((e) => this.use_schedule && (e.schedule || []).includes(t)
        && this._ready(e, t, act, world));
      if (scheduled.length) return scheduled[0];
      if (t - this.last_any < GLOBAL_COOLDOWN) return null;
      const cands = this.events.filter((e) => !('schedule' in e) && this._ready(e, t, act, world));
      const overdue = t >= BEAT_START && t - this.last_beat >= BEAT_GAP;
      const beats = cands.filter((e) => e.beat);
      if (overdue && beats.length) {
        return world.rng.choices1(beats, beats.map((e) => (e.weight !== undefined ? e.weight : 1.0)));
      }
      if (world.rng.random() > 0.22 + 0.35 * world.dread()) return null;
      if (!cands.length) return null;
      return world.rng.choices1(cands, cands.map((e) => (e.weight !== undefined ? e.weight : 1.0)));
    }
    radioReady(ev, world) {
      if (world.tick_no - (this.last_fired.has(ev.id) ? this.last_fired.get(ev.id) : -99) < (ev.cooldown !== undefined ? ev.cooldown : 18)) return false;
      if (ev.once && this.last_fired.has(ev.id)) return false;
      return evaluate(ev.requires, world);
    }
    _ready(ev, t, act, world) {
      if (ev.radio) return false;
      if ('at_progress' in ev) return false;
      if ('mission' in ev) {
        const ms = Array.isArray(ev.mission) ? ev.mission : [ev.mission];
        if (world.run === null || !ms.includes(world.run.mission.id)) return false;
      }
      if ('schedule' in ev && !this.use_schedule) return false;
      if (!ev.acts.includes(act) && !('schedule' in ev)) return false;
      if (ev.once && this.last_fired.has(ev.id)) return false;
      const last = this.last_fired.has(ev.id) ? this.last_fired.get(ev.id) : -99;
      if (t - last < (ev.cooldown !== undefined ? ev.cooldown : 12)) return false;
      return evaluate(ev.requires, world);
    }
    fire(ev, world) {
      const t = world.tick_no;
      this.last_fired.set(ev.id, t);
      this.last_any = t;
      if ('at_progress' in ev && world.run !== null) world.run.phase_fired.add(ev.id);
      const target = this._pickTarget(ev.target, world);
      world.event_target = target;
      const mundaneOk = evaluate(ev.mundane_when, world);
      const text = ev.text.split('{target}').join(target ? target.name : 'someone');
      const record = { tick: t, id: ev.id, act: world.act(), text, mundane_ok: mundaneOk, choice: null, beat: !!ev.beat };
      if (ev.beat) this.last_beat = t;
      world.fired.push(record);
      world.log.push(`${tag(t)} ${text}`);
      applyEffects(ev.effects || [], world, target);
      const choices = (ev.choices || []).filter((c) => evaluate(c.requires, world)).map((c) => ({
        key: c.key, text: c.text, tags: c.tags || [], cost: c.cost || '', effects: c.effects,
      }));
      if (choices.length) {
        world.pending = { event_id: ev.id, text, target_id: target ? target.id : null, choices };
      }
      return record;
    }
    _pickTarget(spec, world) {
      if (!spec) return null;
      let pool = world.active_crew().filter((c) => !c.isolated || spec.include_isolated);
      if ('role' in spec) {
        const byRole = pool.filter((c) => c.role === spec.role);
        if (byRole.length) pool = byRole;
      }
      if (!pool.length) return null;
      const sel = spec.select || 'random';
      if (sel === 'highest') return maxBy(pool, (c) => c[spec.stat]);
      if (sel === 'lowest') return minBy(pool, (c) => c[spec.stat]);
      return world.rng.choice(pool);
    }
  }

  function who(spec, world, target) {
    if (spec === 'target') return target ? [target] : [];
    if (spec === 'all') return world.active_crew();
    if (spec === 'random') { const pool = world.active_crew(); return pool.length ? [world.rng.choice(pool)] : []; }
    if (spec === 'others') return world.active_crew().filter((c) => !target || c.id !== target.id);
    if (spec.startsWith('role:')) return world.active_crew().filter((c) => c.role === spec.slice(5));
    if (spec.startsWith('highest:') || spec.startsWith('lowest:')) {
      const [kind, stat] = spec.split(':');
      const pool = world.active_crew();
      if (!pool.length) return [];
      return [(kind === 'highest' ? maxBy : minBy)(pool, (c) => c[stat])];
    }
    throw new Error(`unknown who ${spec}`);
  }

  function applyEffects(effects, world, target) {
    const ship = world.ship;
    for (const fx of effects) {
      const op = fx.op;
      if (op === 'ship') {
        const [lo, hi] = SHIP_CLAMP[fx.stat] || [0.0, 1.0];
        ship[fx.stat] = clamp(ship[fx.stat] + fx.value, lo, hi);
      } else if (op === 'crew') {
        for (const c of who(fx.who, world, target)) c[fx.stat] = clamp(c[fx.stat] + fx.value);
      } else if (op === 'flag') {
        ship.flags.add(fx.name);
        if ('ttl' in fx) world.flag_expiry.set(fx.name, world.tick_no + fx.ttl);
      } else if (op === 'unflag') {
        ship.flags.delete(fx.name);
      } else if (op === 'routine') {
        ship.routines[fx.item] = clamp(ship.routines[fx.item] + fx.value);
      } else if (op === 'rumor') {
        let r = ship.rumors.get(fx.id);
        if (!r) r = new Rumor(fx.id, fx.text, fx.intensity !== undefined ? fx.intensity : 0.5, Object.assign({}, fx.drift || {}));
        r.intensity = clamp(Math.max(r.intensity, fx.intensity !== undefined ? fx.intensity : r.intensity));
        const seed = fx.seed !== undefined ? fx.seed : 'target';
        const seeded = seed !== 'none' ? who(seed, world, target) : [];
        for (const c of seeded) { r.believers.add(c.id); c.believes.add(r.id); }
        ship.rumors.set(r.id, r);
      } else if (op === 'phantom') {
        const aud = who(fx.audible, world, target).map((c) => c.id);
        if (aud.length) world.deck.spawn(fx.kind, aud, fx.intensity !== undefined ? fx.intensity : 0.4, fx.text || '', world.rng, world.crew);
      } else if (op === 'vanish') {
        for (const c of who(fx.who, world, target)) c.missing = true;
        ship.flags.add('sailor_missing');
      } else if (op === 'isolate') {
        for (const c of who(fx.who, world, target)) c.isolated = true;
      } else if (op === 'release') {
        for (const c of who(fx.who, world, target)) { c.isolated = false; c.isolated_ticks = 0; }
      } else if (op === 'kill') {
        for (const c of who(fx.who, world, target)) c.alive = false;
      } else if (op === 'combat') {
        world.combat(fx.severity);
      } else if (op === 'log_entry') {
        world.ship[`log_${fx.kind}`] += 1;
      } else if (op === 'peace_news') {
        if (world.truth.war_over) {
          world.ship.flags.add('peace_known');
          world.log.push(`${tag(world.tick_no)} The radio man reads the date aloud twice. It is eleven months after an armistice nobody told us about.`);
        } else world.log.push(`${tag(world.tick_no)} Something about a date, and a word that might be 'armistice', or 'amnesty', or a man's name.`);
      } else if (op === 'traffic_act') {
        trafficAct(world, fx.action);
      } else if (op === 'engage_order') {
        engageOrder(world, fx.order);
      } else if (op === 'depth_order') {
        world.ship.depth_order = fx.value; world.ship.depth_extra = 0;
      } else if (op === 'emergency_surface') {
        const sh = world.ship;
        sh.surfaced = true; sh.scope_up = false; sh.depth_extra = 0; sh.flags.delete('sinking');
        sh.hull = clamp(sh.hull - 0.04);
        for (const c of world.active_crew()) c.fear = clamp(c.fear + 0.06);
        world.log.push(`${tag(world.tick_no)} Everything blown. The boat climbs like something thrown, and breaks the surface in a wash of white.`);
      } else if (op === 'tubes') {
        for (let i = 0; i < 4; i++) if (world.ship.tubes[i] !== 'empty') world.ship.tubes[i] = fx.state;
      } else if (op === 'fire') {
        fireTorpedoes(world, fx.n);
      } else if (op === 'leave_station') {
        world.log.push(`${tag(world.tick_no)} ${world.leave_station()}`);
      } else if (op === 'check_world') {
        world.log.push(`${tag(world.tick_no)} ${world.check_world()}`);
      } else if (op === 'summon_notice') {
        world.notice_at_override = world.vigil_ticks + 6;
      } else if (op === 'travel_delay') {
        world.travel_left = Math.max(1, world.travel_left + fx.value);
      } else if (op === 'set') {
        ship[fx.stat] = fx.value;
      } else if (op === 'time') {
        world.lose_hours(fx.value * world.patrol_ticks);
      } else if (op === 'rumor_intensity') {
        const r = ship.rumors.get(fx.id);
        if (r) r.intensity = clamp(r.intensity + fx.value);
      } else if (op === 'verify_orders') {
        world.log.push(`${tag(world.tick_no)} ${orders.verify_orders(world)}`);
      } else if (op === 'mission_outcome') {
        world.resolve_mission(fx.value);
      } else if (op === 'if') {
        applyEffects(evaluate(fx.cond, world) ? fx.then : (fx.else || []), world, target);
      } else if (op === 'chance') {
        let p = fx.p;
        for (const m of ('mod' in fx ? [fx.mod] : []).concat(fx.mods || [])) p += m.k * (resolvePath(m.path, world) - (m.ref !== undefined ? m.ref : 0.0));
        for (const [flag, bonus] of Object.entries(fx.if_flag || {})) if (ship.flags.has(flag)) p += bonus;
        applyEffects(world.rng.random() < clamp(p, 0.02, 0.98) ? fx.then : (fx.else || []), world, target);
      } else if (op === 'mute_phantoms') {
        world.deck.mute_all();
      } else if (op === 'log') {
        world.log.push(`${tag(world.tick_no)} ${fx.text}`);
      } else {
        throw new Error(`unknown effect op ${op}`);
      }
    }
  }

  // ---------------------------------------------------------------- orders
  const orders = {
    silence_sonar(w) {
      w.ship.sonar_on = false; w.deck.mute_all();
      for (const c of w.active_crew()) if (c.role === 'sonar') c.fear = clamp(c.fear - 0.15);
      return 'Sonar off. The headsets go quiet.';
    },
    restore_sonar(w) { w.ship.sonar_on = true; return 'Sonar back on.'; },
    isolate(w, cid) {
      const c = w.crew_by_id(cid);
      if (!c || !c.active || c.isolated) return 'Nothing to do.';
      c.isolated = true; c.trust = clamp(c.trust - 0.25); c.guilt = clamp(c.guilt + 0.15);
      w.ship.rumors.forEach((r) => r.believers.delete(cid));
      for (const o of w.active_crew()) o.trust = clamp(o.trust - 0.03);
      w.ship.attention = clamp(w.ship.attention + 0.03);
      return `${c.name} is confined to the forward berth.`;
    },
    release(w, cid) {
      const c = w.crew_by_id(cid);
      if (!c || !c.isolated) return 'Nothing to do.';
      c.isolated = false; c.isolated_ticks = 0;
      return `${c.name} is back on the watch bill.`;
    },
    force_compartment(w, cid) {
      const c = w.crew_by_id(cid);
      if (!c || !c.active) return 'Nothing to do.';
      w.ship.hull = clamp(w.ship.hull + 0.05);
      c.fear = clamp(c.fear + 0.2); c.guilt = clamp(c.guilt + 0.1);
      for (const o of w.active_crew()) { o.trust = clamp(o.trust - 0.12); o.guilt = clamp(o.guilt + 0.05); }
      return `${c.name} goes in. The repair holds.`;
    },
    stand_down(w) {
      w.ship.stand_down = true; w.ship.rest_cancelled = false;
      return 'All hands but the skeleton watch are sent to their bunks.';
    },
    cancel_rest(w) {
      if (!w.ship.rest_cancelled) for (const c of w.active_crew()) c.trust = clamp(c.trust - 0.03);
      w.ship.rest_cancelled = true;
      return 'Rest is cancelled for all hands.';
    },
    grant_rest(w) { w.ship.rest_cancelled = false; return 'Normal watch rotation resumes.'; },
    hold_ritual(w) {
      const s = w.ship;
      const order = Object.keys(s.routines).map((k, i) => [k, i]).sort((a, b) => (s.routines[a[0]] - s.routines[b[0]]) || (a[1] - b[1]));
      for (const [item] of order.slice(0, 2)) s.routines[item] = clamp(s.routines[item] + 0.4);
      w.lose_hours(0.75);
      for (const c of w.active_crew()) c.fear = clamp(c.fear - 0.03);
      return 'The crew eats together. Someone finds a deck of cards.';
    },
    address_crew(w) {
      const live = w.active_crew();
      if (!live.length) return 'No one to address.';
      const avg = fsum(live.map((c) => c.trust)) / live.length;
      w.ship.rumors.forEach((r) => { r.intensity = clamp(r.intensity - 0.35 * avg); });
      for (const c of live) c.trust = clamp(c.trust - 0.03 + 0.05 * avg);
      return 'The captain speaks over the intercom.';
    },
    scrub_air(w) {
      const s = w.ship;
      if (s.scrubber < 0.12) return 'The absorbent is spent.';
      s.scrubber = clamp(s.scrubber - 0.12);
      s.co2 = clamp(s.co2 - 0.004, 0.005, 0.1);
      return 'Fresh absorbent in the scrubbers.';
    },
    raise_periscope(w) { w.ship.scope_up = true; return 'The periscope rises. The sea is very bright.'; },
    lower_periscope(w) { w.ship.scope_up = false; return 'The periscope is housed.'; },
    surface(w) {
      const s = w.ship;
      s.surfaced = true; s.scope_up = false; s.co2 = Math.max(0.005, s.co2 - 0.01); s.attention = clamp(s.attention - 0.1);
      for (const c of w.active_crew()) c.fear = clamp(c.fear - 0.1);
      return 'Surfacing. The hatch opens on cold air.';
    },
    dive(w) {
      const s = w.ship;
      if (!s.surfaced) return 'We are not on the surface.';
      const err = roleError(w, 'deck');
      if (err > 0 && w.rng.random() < err * 0.8) { s.dive_lag = 2; return 'The hatch will not dog. We stay on the surface a while longer.'; }
      s.surfaced = false;
      return 'Diving.';
    },
    active_ping(w) {
      w.ship.noise = clamp(w.ship.noise + 0.35); w.ship.attention = clamp(w.ship.attention + 0.02);
      return 'One ping. The hull rings with it.';
    },
    silent_running(w, on) {
      w.ship.silent_running = on;
      return on ? 'Silent running.' : 'Resuming normal running.';
    },
    take_fix(w) { return takeFix(w); },
    load_torpedoes(w, kind) { return loadType(w, kind); },
    listen_radio(w) { return listenRadio(w); },
    call_council(w) { return callCouncil(w); },
    sick_call(w) { return sickCall(w); },
    write_log(w) { return writeLog(w); },
    set_speed(w, level) { return setSpeed(w, level); },
    set_depth(w, level) { return setDepth(w, level); },
    snorkel(w, on) { return setSnorkel(w, on); },
    damage_control(w, on) { return setDamageControl(w, on); },
    verify_orders(w) {
      const run = w.run;
      if (run === null || run.phase_fired.has('verified')) return 'Nothing more to verify.';
      run.phase_fired.add('verified');
      const s = w.ship;
      s.noise = clamp(s.noise + 0.15); s.attention = clamp(s.attention + 0.03);
      w.lose_hours(0.7);
      const roll = w.rng.random();
      if (roll < run.mission.quality * 0.8) {
        s.orders_doubt = clamp(s.orders_doubt - 0.25);
        return 'A reply confirms the order, relayed through a station you cannot identify.';
      }
      if (roll < 0.8) { s.orders_doubt = clamp(s.orders_doubt + 0.05); return 'No acknowledgement.'; }
      s.orders_doubt = clamp(s.orders_doubt + 0.2);
      s.flags.add('orders_contradicted');
      return 'The reply contradicts the order: same call sign, different cipher.';
    },
  };

  // ---------------------------------------------------------------- the world
  const DEFAULT_NAMES = ['Brandt', 'Keller', 'Vogel', 'Hahn', 'Lenz', 'Ostrow', 'Weiss', 'Maier', 'Fuchs', 'Reiter', 'Arndt', 'Kopp'];
  const HARD_LIMIT_FACTOR = 1.1, ATTENTION_FLOOR = 0.25, REST_CANCEL_FATIGUE = 0.012, PACE = 0.95;

  // ---------------------------------------------------------------- the boat's machinery (dread/systems.py)
  const SPEEDS = { slow: [0.5, 4.0], standard: [1.0, 8.0], flank: [1.6, 13.0] };
  const DEPTHS = { shallow: 60, deep: 120, test: 180 };
  const DRAIN = { slow: 0.003, standard: 0.006, flank: 0.02 }, HOTEL = 0.001, IDLE_DRAIN = 0.002;
  const ENGINE_FACTOR = { ok: 1.0, damaged: 0.6, dead: 0.3 };
  const integrity = (w, comp) => Math.max(0.0, Math.min(1.0, 1.0 - 2.0 * w.ship.damage[comp]));
  const systemState = (w, comp) => { const i = integrity(w, comp); return i < 0.35 ? 'dead' : i < 0.7 ? 'damaged' : 'ok'; };
  function roleError(w, role) {
    const crew = w.active_crew().filter((c) => c.role === role);
    if (!crew.length) return 0.6;
    const strain = fsum(crew.map((c) => (c.fear + c.fatigue) / 2)) / crew.length;
    return Math.max(0.0, Math.min(0.6, 1.2 * strain - 0.2));
  }
  // the sea floor and what the hull can bear (dread/bathy.py)
  const KEEL_MARGIN = 8;
  const seabedAt = (x, y) => Math.trunc(Math.min(900, 45 + 4.0 * Math.hypot(x - 100.0, y - 12.0) + 20 * ((Math.floor(Math.trunc(x) / 7) + Math.floor(Math.trunc(y) / 5)) % 3)));
  const crushDepth = (hull) => Math.trunc(100 + 200 * Math.max(0.0, Math.min(1.0, hull)));
  const seabedHere = (w) => { const [x, y] = trueXY(w); return seabedAt(x, y); };
  function depthM(w) {
    const s = w.ship;
    if (s.surfaced) return 0;
    if (s.scope_up) return 14;
    return Math.min(DEPTHS[s.depth_order] + s.depth_extra, Math.max(14, seabedHere(w) - KEEL_MARGIN));
  }
  const underKeel = (w) => (w.ship.surfaced || w.ship.flags.has('bottomless') ? null : Math.max(0, seabedHere(w) - depthM(w)));
  const movingNow = (w) => w.ship.returning || (w.working !== null && !w.work_blocked);
  function pace(w) {
    const s = w.ship;
    if (s.battery <= 0 && !s.surfaced) return 0.0;
    return SPEEDS[s.speed_order][0] * (s.silent_running ? 0.5 : 1.0) * ENGINE_FACTOR[systemState(w, 'engine room')];
  }
  const usableBowTubes = (w) => ({ ok: 4, damaged: 2, dead: 0 }[systemState(w, 'bow torpedo room')]);
  // torpedoes: three kinds, each with a habit (dread/systems.py)
  const TYPE_KN = { steam: 44.0, electric: 30.0, acoustic: 24.0 }, TYPE_BONUS = { steam: 0.0, electric: -0.05, acoustic: 0.15 };
  function spendOne(w) {
    const s = w.ship;
    let t = s.torpedo_type;
    if (s.types[t] <= 0) {
      t = Object.keys(s.types).reduce((a, k) => (s.types[k] > s.types[a] ? k : a), Object.keys(s.types)[0]);
      w.log.push(`${tag(w.tick_no)} No more ${s.torpedo_type} fish; the room loads ${t}.`);
      s.torpedo_type = t;
    }
    s.types[t] -= 1; s.torpedoes -= 1;
    return t;
  }
  function loadType(w, kind) {
    const s = w.ship;
    if (w.engagement !== null) return 'Not now. The room has no time to change fish.';
    if (kind === s.torpedo_type) return `The tubes already hold ${kind} torpedoes.`;
    if (s.types[kind] <= 0) return `There are no ${kind} torpedoes aboard.`;
    w.lose_hours(1.0);
    s.torpedo_type = kind;
    s.tubes = [0, 1, 2, 3, 4, 5].map((i) => (i < s.torpedoes ? 'loaded' : 'empty'));
    return `The torpedo room reloads the tubes with ${kind} fish.`;
  }
  function fireTorpedoes(w, n) {
    const s = w.ship;
    const room = w.active_crew().some((c) => c.role === 'torpedo') ? roleError(w, 'torpedo') : 0.6;
    const kind = s.torpedo_type;
    s.shot_type = kind;
    let fired = 0;
    for (let i = 0; i < usableBowTubes(w); i++) {
      if (fired < n && (s.tubes[i] === 'open' || s.tubes[i] === 'flooded') && s.torpedoes > 0) {
        if (room > 0 && w.rng.random() < 0.5 * room) {
          w.log.push(`${tag(w.tick_no)} Tube ${i + 1} does not answer.`);
          s.flags.add('tube_fail'); w.flag_expiry.set('tube_fail', w.tick_no + 2);
          continue;
        }
        s.tubes[i] = 'empty'; spendOne(w); fired += 1;
      }
    }
    if (!fired) return;
    if (kind === 'steam' && w.engagement === null && w.rng.random() < 0.35) {
      w.log.push(`${tag(w.tick_no)} The wakes run straight back to us. Her escorts have seen them.`);
      w.combat(0.4);
    } else if (kind === 'acoustic') {
      if (contactRows(w).some((r) => !r[3]) && w.rng.random() < 0.5) {
        s.flags.add('torp_ghost'); w.flag_expiry.set('torp_ghost', w.tick_no + 2);
        w.log.push(`${tag(w.tick_no)} The torpedo turns from the target toward a sound nobody else can find.`);
      }
      if (w.rng.random() < 0.04 + 0.5 * Math.max(0.0, s.noise - 0.12)) {
        s.hull = clamp(s.hull - 0.12);
        s.flags.add('torp_circular'); w.flag_expiry.set('torp_circular', w.tick_no + 2);
        for (const c of w.active_crew()) c.fear = clamp(c.fear + 0.08);
        w.log.push(`${tag(w.tick_no)} A circular run. The fish comes round for the loudest thing it knows, which is us.`);
      }
    }
  }
  function applyHelm(w, kind, level) { if (kind === 'speed') w.ship.speed_order = level; else w.ship.depth_order = level; }
  function helmOrder(w, kind, level, text) {
    const s = w.ship;
    let err = roleError(w, 'helm');
    if (systemState(w, 'control room') !== 'ok') err = Math.max(err, 0.3);
    if (err > 0 && w.rng.random() < err * 0.8) {
      s.helm_pending = [kind, level]; s.helm_lag = 2;
      return 'The helmsman repeats the old order. It will take a moment.';
    }
    applyHelm(w, kind, level);
    return text;
  }
  function setSpeed(w, level) {
    const s = w.ship;
    if (level === s.speed_order && s.helm_pending === null) return `We are already making ${level} speed.`;
    const state = systemState(w, 'engine room');
    if (level === 'flank' && state !== 'ok') return 'The engine room cannot give it.';
    if (state === 'dead' && level !== 'slow') return 'The engine room can give no more than slow.';
    return helmOrder(w, 'speed', level, `Ahead ${level}.`);
  }
  function setDepth(w, level) {
    const s = w.ship;
    if (s.surfaced) return 'We are on the surface.';
    if (level === s.depth_order && s.helm_pending === null) return `We are already at ${DEPTHS[level]} metres.`;
    if (systemState(w, 'control room') === 'dead') return 'The planes are jammed. We stay where we are.';
    const sb = seabedHere(w);
    if (DEPTHS[level] > sb - KEEL_MARGIN - 6) return `There is not the water for it: the chart gives ${sb} metres here.`;
    if (DEPTHS[level] >= crushDepth(s.hull)) return 'She would not survive it. The hull is not what it was.';
    if (level !== 'shallow') s.scope_up = false;
    return helmOrder(w, 'depth', level, `Going to ${DEPTHS[level]} metres.`);
  }
  function setSnorkel(w, on) {
    const s = w.ship;
    if (on && !(s.scope_up && !s.surfaced)) return 'Snorkel depth means the periscope is up.';
    s.snorkel = on;
    return on ? 'The diesels run on the snorkel. The boat shudders and the air moves.' : 'The diesels stop.';
  }
  function setDamageControl(w, on) {
    const s = w.ship;
    if (on && s.spares <= 0) return 'There is nothing left to repair with.';
    if (on && s.hull >= 0.999) return 'Nothing is broken that anyone can find.';
    s.dc_active = on;
    return on ? 'All hands that can be spared go to the worst compartment.' : 'The damage control party stands down.';
  }
  function systemsTick(w) {
    const s = w.ship, live = w.active_crew(), t = w.tick_no;
    if (s.dive_lag > 0 && s.surfaced) {
      s.dive_lag -= 1;
      if (s.dive_lag === 0) { s.surfaced = false; w.log.push(`${tag(t)} The hatch is dogged at last. Diving.`); }
    }
    if (s.helm_pending !== null) {
      s.helm_lag -= 1;
      if (s.helm_lag <= 0) {
        const [kind, level] = s.helm_pending;
        s.helm_pending = null;
        applyHelm(w, kind, level);
        w.log.push(`${tag(t)} The helm answers: ${kind === 'speed' ? 'ahead ' + level : DEPTHS[level] + ' metres'}.`);
      }
    }
    s.dr_error = Math.min(40.0, s.dr_error + (movingNow(w) ? 0.12 : 0.03) * (1.0 + 1.5 * roleError(w, 'helm') + s.attention));
    if (s.snorkel && !(s.scope_up && !s.surfaced)) { s.snorkel = false; w.log.push(`${tag(t)} The diesels stop; there is no snorkel to breathe through.`); }
    if (s.surfaced) s.battery = clamp(s.battery + 0.06);
    else if (s.snorkel) {
      s.battery = clamp(s.battery + 0.03); s.fuel = clamp(s.fuel - 0.005); s.co2 = clamp(s.co2 - 0.004, 0.005, 0.1); s.attention = clamp(s.attention + 0.004);
    } else {
      const rate = movingNow(w) ? DRAIN[s.speed_order] : IDLE_DRAIN;
      s.battery = clamp(s.battery - (rate * (s.silent_running ? 0.6 : 1.0) + HOTEL));
    }
    if (s.battery <= 0.0 && !s.surfaced) {
      if (!s.flags.has('battery_dead')) { s.flags.add('battery_dead'); w.log.push(`${tag(t)} The batteries are flat. The lights go. We cannot move until we surface or run the diesels.`); }
    } else if (s.flags.has('battery_dead') && s.battery > 0.1) {
      s.flags.delete('battery_dead'); w.log.push(`${tag(t)} The lights come back. The motors turn.`);
    }
    if (s.battery < 0.25 && !s.surfaced) {
      for (const c of live) c.fear = clamp(c.fear + 0.003);
      s.attention = clamp(s.attention + 0.003);
    }
    if (!s.surfaced) {
      const sb = seabedHere(w);
      if (s.flags.has('sinking')) s.depth_extra = Math.min(150, s.depth_extra + 15);
      else if (s.depth_extra) s.depth_extra = Math.max(0, s.depth_extra - 10);
      const d = depthM(w);
      if (s.depth_extra && DEPTHS[s.depth_order] + s.depth_extra > sb - KEEL_MARGIN && !s.scope_up) {
        s.hull = clamp(s.hull - 0.01); s.noise = clamp(s.noise + 0.1);
        if (!s.flags.has('grounded')) { s.flags.add('grounded'); w.log.push(`${tag(t)} The keel scrapes. There is a bottom after all, and we are on it.`); }
      } else s.flags.delete('grounded');
      const crush = crushDepth(s.hull);
      if (d >= crush) { s.hull = 0.0; w.log.push(`${tag(t)} The pressure hull gives at ${d} metres. It is very quick, and nobody is left to be surprised.`); }
      else if (d > crush - 30 && w.rng.random() < 0.1) { s.hull = clamp(s.hull - 0.05); w.log.push(`${tag(t)} A frame buckles with a sound like a gun. The hull is nearer its limit than the gauge says.`); }
      if (d >= 120) {
        s.attention = clamp(s.attention + 0.0015 * (d / 60.0 - 1.0));
        const afraid = live.filter((c) => c.fear > 0.6);
        if (afraid.length && w.rng.random() < (d < 180 ? 0.03 : 0.06) * afraid.length) {
          const man = maxBy(afraid, (c) => c.fear);
          s.noise = clamp(s.noise + 0.1);
          for (const c of live) c.fear = clamp(c.fear + 0.02);
          w.log.push(`${tag(t)} ${man.name} cries out and presses both hands flat against the hull, as if to hold it.`);
        }
      }
      if (s.depth_order === 'deep') {
        for (const c of live) c.fear = clamp(c.fear + 0.0015);
        if (s.hull < 0.6 && w.rng.random() < 0.02) { s.hull = clamp(s.hull - 0.02); w.log.push(`${tag(t)} A seam weeps at 120 metres.`); }
      } else if (s.depth_order === 'test') {
        for (const c of live) c.fear = clamp(c.fear + 0.004);
        if (s.hull < 0.8 && w.rng.random() < 0.05) { s.hull = clamp(s.hull - 0.04); w.log.push(`${tag(t)} A seam gives at test depth. The pumps race.`); }
      }
    }
    if (s.dc_active) {
      if (s.hull >= 0.999 || s.spares <= 0.0) {
        s.dc_active = false;
        w.log.push(`${tag(t)} Damage control stands down: ` + (s.hull >= 0.999 ? 'nothing left to mend.' : 'the spares are gone.'));
      } else {
        s.hull = clamp(s.hull + 0.005); s.spares = clamp(s.spares - 0.012);
        for (const c of live) c.fatigue = clamp(c.fatigue + 0.003);
      }
    }
  }

  // ---------------------------------------------------------------- the engagement (dread/combat.py)
  const ORDER_FACTOR = { hold: 1.0, deep: 0.9, silent: 0.8, evade: 0.55, decoy: 0.5 };
  function combatStart(w, severity) {
    const s = w.ship;
    if (w.engagement !== null) { w.engagement.turns_left += 1; return; }
    const escorts = 1 + Math.trunc(severity * 3);
    w.engagement = { severity, escorts, turns_left: 1 + Math.trunc(severity * 4), turn: 0, order: null, wide_said: false, prev: null };
    s.flags.add('in_combat');
    const warned = s.sonar_on && !s.flags.has('fault_sonar');
    for (const c of w.active_crew()) c.fear = clamp(c.fear + 0.04 * severity * (warned ? 1.0 : 1.5));
    w.log.push(`${tag(w.tick_no)} ` + (warned ? 'Screws on the headsets, closing. ' : 'No warning. ') + `${escorts === 1 ? 'One escort' : escorts + ' escorts'} working the water above us.`);
  }
  function engagementDecision(w) {
    const e = w.engagement, s = w.ship;
    const shaky = roleError(w, 'helm') >= 0.3 ? ' The helmsman is shaking.' : '';
    const mk = (key, text, tags, cost) => ({ key, text, tags, cost, effects: [{ op: 'engage_order', order: key }] });
    const ch = [mk('hold', 'Hold course and depth.', ['mission'], 'They know where you were.')];
    if (systemState(w, 'control room') !== 'dead' && s.depth_order === 'shallow') ch.push(mk('deep', 'Go deep.', ['care'], 'Down where the hull speaks.' + shaky));
    ch.push(mk('silent', 'Rig for silent running.', ['care', 'comply'], 'Nothing moves and nobody speaks; the men must keep still.'));
    if (systemState(w, 'engine room') === 'ok' && s.battery > 0.2) ch.push(mk('evade', 'Turn into the screws and run at flank.', ['mission', 'attack'], 'Fast, loud, and the batteries go.' + shaky));
    if (s.decoys > 0) ch.push(mk('decoy', 'Release a decoy.', ['care'], `${s.decoys} left. It may not be believed.`));
    const text = `Charges. ${e.escorts} escort${e.escorts > 1 ? 's' : ''} above; turn ${e.turn + 1}, and the pattern is still falling. Your order?`;
    return { event_id: 'engagement_turn', text, target_id: null, choices: ch };
  }
  function engageOrder(w, key) {
    const e = w.engagement, s = w.ship;
    if (e === null) return;
    e.order = key;
    if (e.prev === null) e.prev = [s.speed_order, s.depth_order, s.silent_running];
    if (key === 'deep') w.log.push(`${tag(w.tick_no)} ` + setDepth(w, 'deep'));
    else if (key === 'silent') s.silent_running = true;
    else if (key === 'evade') w.log.push(`${tag(w.tick_no)} ` + setSpeed(w, 'flank'));
    else if (key === 'decoy') s.decoys -= 1;
  }
  function engagementResolve(w) {
    const e = w.engagement, s = w.ship, live = w.active_crew();
    const r0 = w.rng.random();
    const guess = r0 < 0.5 ? 'shallow' : r0 < 0.85 ? 'deep' : 'test';
    const close = s.depth_order === guess;
    const threat = 0.2 + 0.35 * e.severity + 0.1 * (e.escorts - 1);
    const loud = Math.max(0.2, Math.min(1.5, s.noise * 2.5));
    let pHit = threat * loud * (close ? 1.0 : 0.35) * ORDER_FACTOR[e.order];
    if (s.attention >= 0.5) {
      pHit *= 0.5;
      if (!e.wide_said) { e.wide_said = true; w.log.push(`${tag(w.tick_no)} The charges fall a hundred yards wide. Again, on the same side.`); }
    }
    if (live.length) {
      const meanFear = fsum(live.map((c) => c.fear)) / live.length;
      if (w.rng.random() < clamp(meanFear - 0.45, 0.0, 0.45)) {
        const man = maxBy(live, (c) => c.fear);
        const kind = Math.trunc(w.rng.random() * 3);
        const valve = w.engine.byId.get('valve_panic');
        if (kind === 0 && valve && w.tick_no - (w.engine.last_fired.has('valve_panic') ? w.engine.last_fired.get('valve_panic') : -99) >= (valve.cooldown !== undefined ? valve.cooldown : 14)) w.engine.fire(valve, w);
        else if (kind === 0) { s.hull = clamp(s.hull - 0.04); w.log.push(`${tag(w.tick_no)} ${man.name} opens the wrong valve. Water, cold, and a smell of the sea at the bottom of it.`); }
        else if (kind === 1 && s.torpedoes > 0) {
          spendOne(w); s.noise = clamp(s.noise + 0.15); pHit = clamp(pHit + 0.1, 0.0, 0.9);
          w.log.push(`${tag(w.tick_no)} ${man.name} fires a tube without orders. The whole boat hears it go.`);
        } else { s.noise = clamp(s.noise + 0.15); pHit = clamp(pHit + 0.15, 0.0, 0.9); w.log.push(`${tag(w.tick_no)} ${man.name} drops a wrench. In the silence it is a bell.`); }
        man.fear = clamp(man.fear + 0.05);
        for (const c of live) c.trust = clamp(c.trust - 0.01);
      }
    }
    if (w.rng.random() < clamp(pHit, 0.02, 0.9)) {
      s.hull = clamp(s.hull - e.severity * (0.08 + 0.12 * w.rng.random()));
      for (const c of live) { c.fear = clamp(c.fear + 0.07); c.fatigue = clamp(c.fatigue + 0.05); }
      w.log.push(`${tag(w.tick_no)} A charge close aboard. The lights flicker; something in the hull rings like a struck glass.`);
    } else {
      for (const c of live) c.fear = clamp(c.fear + 0.025);
      w.log.push(`${tag(w.tick_no)} The charges fall wide.`);
    }
    if (e.order === 'decoy' && w.rng.random() < 0.5) { e.turns_left = Math.min(e.turns_left, 1); w.log.push(`${tag(w.tick_no)} One escort goes after the decoy.`); }
    e.order = null; e.turn += 1; e.turns_left -= 1;
  }
  function combatTick(w) {
    const e = w.engagement;
    if (e === null) return;
    if (e.order !== null) engagementResolve(w);
    if (e.turns_left <= 0) {
      for (const c of w.active_crew()) c.fatigue = clamp(c.fatigue + 0.1 * e.severity);
      w.engagement = null;
      const s = w.ship;
      s.flags.delete('in_combat');
      w.log.push(`${tag(w.tick_no)} The screws fade. The sea goes back to being the sea.`);
      if (e.prev !== null && (s.speed_order !== e.prev[0] || s.depth_order !== e.prev[1] || s.silent_running !== e.prev[2])) {
        [s.speed_order, s.depth_order, s.silent_running] = e.prev;
        s.helm_pending = null;
        w.log.push(`${tag(w.tick_no)} Normal running resumes.`);
      }
      return;
    }
    if (w.pending === null) w.pending = engagementDecision(w);
  }

  class World {
    constructor(seed, opts) {
      if (!DATA) throw new Error('Dread.setData() first');
      opts = opts || {};
      this.rng = new PyRandom(seed);
      this.crew = DEFAULT_NAMES.map((name, i) => new Crew(i, name, ROLES[i % ROLES.length], i % 3, round2Python(this.rng.uniform(0.25, 0.85))));
      this.ship = new Ship();
      this.deck = new SonarDeck();
      this.engine = new EventEngine(DATA.events, opts.use_schedule !== undefined ? opts.use_schedule : true);
      this.patrol_ticks = opts.patrol_ticks || 72;
      this.tick_no = 0;
      this.log = [];
      this.fired = [];
      this.pending = null;
      this.event_target = null;
      this.flag_expiry = new Map();
      this.mutiny_clock = 0;
      this.legacy_loss = 0.0;
      this.peak_dread = 0.0;
      this._hull_seen = 1.0;
      this.engagement = null;
      this.traffic = [];
      this.traffic_id = 0;
      this.missions = opts.missions !== undefined ? opts.missions : DATA.missions;
      this.run = null;
      this.mission_i = -1;
      this.results = [];
      const trng = new PyRandom(seed * 31 + 7);
      const warOver = trng.random() < 0.5;
      this.truth = { war_over: warOver, notice_at: warOver ? null : trng.randint(50, 150) };
      this.notice_at_override = null;
      this.vigil_ticks = 0;
      this.travel_left = 0;
      this.check_until = -1;
      this.starving = 0;
      if (this.missions.length) this._start_mission(0);
    }
    active_crew() { return this.crew.filter((c) => c.active); }
    crew_by_id(cid) { return this.crew.find((c) => c.id === cid) || null; }
    dread() { return dreadIndex(this.ship, this.crew); }
    get sonar_off_ticks() { return this.deck.sonar_off_ticks; }
    get names_known() { return this.deck.names_learned.size; }
    get on_station() { return this.run !== null && this.run.mission.kind === 'hold'; }
    get notice_ready() {
      if (!this.on_station || this.ship.flags.has('notice_received')) return 0.0;
      const due = this.notice_at_override !== null ? this.notice_at_override : this.truth.notice_at;
      return (due !== null && this.vigil_ticks >= due) ? 1.0 : 0.0;
    }
    act() {
      const d = this.dread();
      const byDread = d < 0.22 ? 1 : d < 0.38 ? 2 : 3;
      return Math.min(byDread, 1 + Math.floor(this.tick_no / 24));
    }
    get solution_error() { return solutionError(this); }
    get depth_m() { return depthM(this); }
    get type_bonus() { return TYPE_BONUS[this.ship.shot_type]; }
    get traffic_near() { return trafficNear(this); }
    get ill_count() { return this.active_crew().filter((c) => c.ill).length; }
    get finished() {
      const f = this.ship.flags;
      const done = this.missions.length ? this.mission_i >= this.missions.length : this.ship.progress >= 1.0;
      const limit = !this.missions.length ? this.patrol_ticks * HARD_LIMIT_FACTOR : 2000;
      return done || this.ship.hull <= 0.0 || f.has('deposed') || f.has('aborted')
        || this.active_crew().length === 0 || this.tick_no >= limit;
    }

    /** What the captain gets to see: stress as reported and symptoms as observed. */
    report(observerSkill) {
      const skill = observerSkill !== undefined ? observerSkill : 0.6;
      const medic = this.active_crew().some((c) => c.role === 'medic');
      const p = Math.min(0.95, skill + (medic ? 0.25 : 0.0));
      const look = new PyRandom(this.tick_no * 7919 + 17);   // looking never touches the patrol's dice
      return this.active_crew().map((c) => ({
        id: c.id, name: c.name, role: c.role, says: c.reported(this.ship.cohesion),
        symptoms: c.symptoms().filter(() => look.random() < p),
      }));
    }

    choose(key) {
      if (this.pending === null) throw new Error('no pending decision');
      const ch = this.pending.choices.find((c) => c.key === key);
      if (!ch) throw new Error(`no such choice ${key}`);
      const target = this.pending.target_id !== null ? this.crew_by_id(this.pending.target_id) : null;
      applyEffects(ch.effects, this, target);
      this.settle_damage();
      for (let i = this.fired.length - 1; i >= 0; i--) {
        if (this.fired[i].id === this.pending.event_id) { this.fired[i].choice = key; break; }
      }
      this.log.push(`${tag(this.tick_no)} > ${ch.text}`);
      this.pending = null;
      return ch.text;
    }

    tick() {
      if (this.pending !== null) throw new Error('a decision is pending; call choose() first');
      this.settle_damage();
      this.tick_no += 1;
      const s = this.ship;
      for (const [name, until] of Array.from(this.flag_expiry.entries())) {
        if (this.tick_no >= until) { s.flags.delete(name); this.flag_expiry.delete(name); }
      }
      if (!s.surfaced) s.hours_submerged += 1;
      this._physics();
      this._resources();
      systemsTick(this);
      healthTick(this);
      updateTraffic(this);
      this._voyage();
      this._rumors();
      this.deck.tick(this);
      this._mission();
      this._mission_flow();
      if (this.on_station) this.vigil_ticks += 1;
      this._mutiny();
      combatTick(this);
      const ev = this.pending === null && this.engagement === null ? this.engine.select(this) : null;
      if (ev !== null) this.engine.fire(ev, this);
      this.settle_damage();
      this.peak_dread = Math.max(this.peak_dread, this.dread());
    }

    /** Book what the hull lost (or got back) against a compartment. Display only; no dice of the world's. */
    settle_damage() {
      const s = this.ship, d = this._hull_seen - s.hull;
      if (Math.abs(d) < 1e-9) return;
      if (d > 0) {
        const name = new PyRandom(this.tick_no * 6151 + Math.round(s.hull * 1000)).choice(COMPARTMENTS);
        s.damage[name] += d;
      } else {
        const name = maxBy(COMPARTMENTS, (c) => s.damage[c]);
        s.damage[name] = Math.max(0.0, s.damage[name] + d);
      }
      this._hull_seen = s.hull;
    }

    _physics() {
      const s = this.ship, live = this.active_crew();
      const n = Math.max(1, live.length);
      if (s.surfaced) s.co2 = Math.max(0.005, s.co2 - 0.01);
      else s.co2 = clamp(s.co2 + 0.00075 * n / 10, 0.0, 0.1);
      const base = Math.max(0.01, (s.silent_running ? 0.04 : 0.1) + { slow: -0.03, standard: 0.0, flank: 0.15 }[s.speed_order] + (s.snorkel ? 0.2 : 0.0));
      s.noise = clamp(base + (s.noise - base) * 0.6);
      for (const k of Object.keys(s.routines)) s.routines[k] = clamp(s.routines[k] - 0.008);
      if (s.rest_cancelled) s.routines.watches = clamp(s.routines.watches - 0.01);
      const routine = s.routine, cohesion = s.cohesion, depth = depthM(this);
      for (const c of live) {
        const onWatch = Math.floor(this.tick_no / 4) % 3 === c.section;
        if (s.stand_down) c.fatigue = clamp(c.fatigue + (onWatch ? 0.005 : -0.03));
        else if (onWatch) c.fatigue = clamp(c.fatigue + 0.015);
        else if (s.rest_cancelled) c.fatigue = clamp(c.fatigue + REST_CANCEL_FATIGUE);
        else {
          const quality = (s.co2 > 0.015 ? 0.5 : 1.0) * (c.fear > 0.6 ? 0.5 : 1.0) * (depth < 120 ? 1.0 : depth < 180 ? 0.8 : 0.6) * ({ ok: 1.0, damaged: 0.7, dead: 0.4 }[systemState(this, 'crew quarters')]);
          c.fatigue = clamp(c.fatigue - 0.012 * quality);
        }
        if (s.co2 > 0.015) c.fatigue = clamp(c.fatigue + 0.003);
        const decay = 0.006 * routine * cohesion * (1 - 0.5 * s.attention);
        c.fear = Math.max(0.05, c.fear - decay);
        if (c.fatigue > 0.5) c.fear = clamp(c.fear + 0.003 + 0.01 * (c.fatigue - 0.5));
        if (s.co2 > 0.03) c.fear = clamp(c.fear + 0.006);
        if (c.isolated) {
          c.isolated_ticks += 1;
          if (c.isolated_ticks > 6) c.fear = clamp(c.fear + 0.01);
        }
        if (cohesion > 0.6) c.guilt = clamp(c.guilt - 0.002);
        if (routine > 0.5) c.trust = clamp(c.trust + 0.002, 0.0, 0.9);
        else if (routine < 0.3) c.trust = clamp(c.trust - 0.002);
      }
      const mean = (a) => fsum(live.map((c) => c[a])) / n;
      const isoFrac = live.filter((c) => c.isolated).length / n;
      s.cohesion = lerp(s.cohesion, clamp(0.4 * mean('trust') + 0.45 * routine + 0.15 * (1 - 3 * isoFrac)), 0.06);
      s.discipline = lerp(s.discipline, clamp(0.35 + 0.4 * mean('trust') + 0.25 * (1 - mean('fatigue'))), 0.05);
      s.readiness = clamp(1.05 - 0.4 * mean('fatigue') - 0.3 * (1 - s.discipline) + (s.rest_cancelled ? 0.35 : 0.0), 0.0, 1.4);
      if (mean('fatigue') > 0.6 && !s.stand_down) {
        s.hull = clamp(s.hull - 0.004 * clamp((mean('fatigue') - 0.5) / 0.4));
      } else if (mean('fatigue') < (s.stand_down ? 0.8 : 0.5) && s.hull < 1.0) {
        s.hull = clamp(s.hull + 0.0015);
      }
      if (s.rest_cancelled) for (const c of live) c.trust = clamp(c.trust - 0.004);
      const floor = this.run !== null ? 0.3 * (1 - this.run.mission.quality) : 0.0;
      s.orders_doubt = Math.max(floor, s.orders_doubt - 0.002);
      for (const c of live) {
        c.trust = clamp(c.trust - 0.0012 * s.orders_doubt);
        c.guilt = clamp(c.guilt + 0.0008 * s.moral_debt);
      }
      if (s.stand_down) {
        s.discipline = clamp(s.discipline - 0.002);
        s.attention = clamp(s.attention + 0.004);
        if (mean('fatigue') < 0.3) {
          s.stand_down = false;
          this.log.push(`${tag(this.tick_no)} The boat wakes. Normal watches resume.`);
        }
      }
      const d = this.dread();
      let da = 0.003 * live.filter((c) => c.isolated).length + 0.012 * d + 0.01 * s.moral_debt
        - 0.004 * routine * s.cohesion - 0.001;
      if (s.scope_up && !s.surfaced) da += 0.004;
      if (s.surfaced) da -= 0.03;
      s.attention = clamp(s.attention + da);
      s.attention = Math.max(s.attention, ATTENTION_FLOOR * clamp((s.hours_submerged - 10) / 60));
      for (const c of live) {
        const night = [0, 1, 2, 3, 22, 23].includes(this.tick_no % 24);
        if (c.isolated || (night && c.fear > 0.5)) {
          if (this.rng.random() < 0.15 * s.attention && !c.name_known) {
            c.name_known = true;
            this.deck.names_learned.add(c.id);
          }
        }
      }
    }

    _resources() {
      const s = this.ship, live = this.active_crew();
      const share = live.length / 12;
      s.food = clamp(s.food - 0.0036 * share * s.rations);
      s.water = clamp(s.water - 0.0042 * share * s.rations);
      if (s.surfaced) s.fuel = clamp(s.fuel - 0.006);
      if (s.surfaced && this.tick_no >= this.check_until && this.check_until > 0 && s.flags.has('checking')) {
        s.flags.delete('checking');
        s.surfaced = false;
      }
      if (s.food < 0.2 || s.water < 0.2) {
        for (const c of live) {
          c.fear = clamp(c.fear + 0.004); c.fatigue = clamp(c.fatigue + 0.003); c.trust = clamp(c.trust - 0.002);
        }
      }
      if (s.food <= 0 || s.water <= 0) {
        this.starving += 1;
        if (this.starving % 8 === 0 && live.length) {
          const victim = maxBy(live, (c) => c.fatigue);
          victim.alive = false;
          this.log.push(`${tag(this.tick_no)} ${victim.name} does not wake. Nobody says what he died of.`);
          for (const c of this.active_crew()) { c.fear = clamp(c.fear + 0.06); c.guilt = clamp(c.guilt + 0.04); }
        }
      } else {
        this.starving = 0;
      }
    }

    leave_station() {
      const s = this.ship;
      if (!this.on_station) return 'There is no station to leave.';
      if (s.returning) return 'We are already under way.';
      if (s.fuel < 0.25 || s.flags.has('adrift')) return 'Not enough diesel for the passage. We would drift. Surface and charge first.';
      s.returning = true;
      this.travel_left = 18;
      s.flags.add('left_station');
      const lawful = s.flags.has('notice_received') || s.flags.has('peace_known');
      if (!lawful) s.flags.add('orders_defied');
      s.surfaced = false;
      return lawful ? 'Setting course for base.' : 'Setting course for base. There has been no notice; everyone knows it.';
    }

    check_world() {
      const s = this.ship;
      s.surfaced = true;
      s.flags.add('checking');
      this.check_until = this.tick_no + 3;
      s.noise = clamp(s.noise + 0.1);
      s.attention = clamp(s.attention - 0.1);
      for (const c of this.active_crew()) c.fear = clamp(c.fear - 0.04);
      if (this.truth.war_over) {
        s.flags.add('peace_known');
        return 'On the surface the radio plays dance music. A voice reads the date: eleven months past an armistice nobody told us about.';
      }
      return 'On the surface, static. Under it something that might be music, or someone counting.';
    }

    _voyage() {
      const s = this.ship;
      if (!s.returning) return;
      s.fuel = clamp(s.fuel - 0.012);
      this.travel_left -= 1;
      if (s.fuel <= 0) {
        s.returning = false;
        s.flags.add('adrift');
        this.log.push(`${tag(this.tick_no)} The engines die. We are adrift.`);
      } else if (this.travel_left <= 0) {
        this._arrive();
      }
    }

    _arrive() {
      const s = this.ship;
      s.returning = false;
      const extra = (s.flags.has('survivors_taken') || s.flags.has('extra_man')) ? 1 : 0;
      const p = Math.min(0.8, 0.08 + 0.35 * s.owed + 0.2 * extra + 0.015 * this.names_known);
      if (this.rng.random() < p) {
        s.flags.add('home_unaccounted');
        this.log.push(`${tag(this.tick_no)} The pier is there. The count on the gangway does not match the roll, and nobody can say which of us is the extra.`);
      } else {
        this.log.push(`${tag(this.tick_no)} The pier is there. Lines are passed. The roll is called, and it is right.`);
      }
      const lawful = s.flags.has('notice_received') || s.flags.has('peace_known');
      this.resolve_mission(lawful ? 'success' : 'left');
    }

    _rumors() {
      const s = this.ship, live = this.active_crew();
      const n = Math.max(1, live.length);
      for (const [rid, r] of Array.from(s.rumors.entries())) {
        for (const cid of Array.from(r.believers)) {
          const c = this.crew_by_id(cid);
          if (!c || !c.active) { r.believers.delete(cid); continue; }
          c.fear = clamp(c.fear + 0.004 * r.intensity);
          for (const [stat, v] of Object.entries(r.drift)) c[stat] = clamp(c[stat] + v);
        }
        if (r.believers.size) {
          const share = r.believers.size / n;
          for (const c of live) {
            if (r.believers.has(c.id) || c.isolated) continue;
            const p = 0.05 * r.intensity * share * (0.5 + c.fear) * (0.5 + s.cohesion);
            if (this.rng.random() < p) { r.believers.add(c.id); c.believes.add(rid); }
          }
        }
        r.intensity = clamp(r.intensity - 0.004);
        if (r.intensity < 0.03) {
          for (const cid of r.believers) { const c = this.crew_by_id(cid); if (c) c.believes.delete(rid); }
          s.rumors.delete(rid);
        }
      }
    }

    _start_mission(i) {
      this.mission_i = i;
      const m = this.missions[i];
      this.ship.tubes = [0, 1, 2, 3, 4, 5].map((i) => (i < this.ship.torpedoes ? 'loaded' : 'empty'));
      this.run = {
        mission: m, start_tick: this.tick_no, outcome: null, phase_fired: new Set(),
        acts_done: 0, working: null, work_left: 0.0, lost: 0.0,
      };
      const s = this.ship;
      s.progress = 0.0;
      s.orders_doubt = clamp(Math.max(s.orders_doubt * 0.5, (1 - m.quality) * 0.6 + (m.moral ? 0.15 : 0.0)));
      this.log.push(`${tag(this.tick_no)} ORDERS: ${m.title}. ${m.briefing}`);
      this.log.push(`${tag(this.tick_no)}   Received: ${provenanceLine(m)}`);
    }

    resolve_mission(outcome) {
      const run = this.run;
      if (run === null || run.outcome !== null) return;
      run.outcome = outcome;
      const m = run.mission;
      this.results.push({ mission: m.id, outcome, tick: this.tick_no });
      this.ship.flags.add(`outcome:${m.id}:${outcome}`);
      this.log.push(`${tag(this.tick_no)} Mission '${m.title}': ${outcome}.`);
      if (this.mission_i + 1 < this.missions.length) this._start_mission(this.mission_i + 1);
      else { this.mission_i += 1; this.run = null; }
    }

    _mission_flow() {
      const run = this.run;
      if (run === null || run.outcome !== null) return;
      const m = run.mission;
      if (m.kind === 'hold') {
        if (this.vigil_ticks > 480) { this.ship.flags.add('derelict'); this.resolve_mission('failed'); }
        return;
      }
      if (this.tick_no > run.start_tick + m.ticks * m.window - run.lost) {
        this.log.push(`${tag(this.tick_no)} The window for '${m.title}' has closed.`);
        this.resolve_mission('failed');
      } else if (this.ship.progress >= 1.0) {
        const fin = this.engine.events.filter((e) => e.mission === m.id && (e.at_progress !== undefined ? e.at_progress : 0) >= 1.0
          && !run.phase_fired.has(e.id));
        if (!fin.length) this.resolve_mission('success');
      }
    }

    _mission() {
      const s = this.ship, run = this.run;
      const speed = s.readiness * pace(this) * (s.surfaced ? 0.0 : 1.0) * (s.stand_down ? 0.3 : 1.0);
      if (run !== null) {
        if (run.outcome === null && run.mission.acts.length) {
          this._work();
        } else if (run.outcome === null && run.mission.kind !== 'hold') {
          s.progress = clamp(s.progress + speed / (run.mission.ticks * PACE));
        }
      } else {
        s.progress = clamp(s.progress + speed / (this.patrol_ticks * PACE) - this.legacy_loss);
        this.legacy_loss = 0.0;
      }
      if (s.surfaced && this.rng.random() < 0.08 && !(this.truth.war_over && this.vigil_ticks > 0)) {
        this.log.push(`${tag(this.tick_no)} Aircraft overhead. We are exposed.`);
        s.hull = clamp(s.hull - 0.12);
        for (const c of this.active_crew()) c.fear = clamp(c.fear + 0.05);
      }
    }

    // -- the acts: what the captain orders to carry the mission out
    lose_hours(hours) {
      if (this.run !== null && this.run.outcome === null) this.run.lost += hours;
      else this.legacy_loss += hours / this.patrol_ticks;
    }
    next_act() {
      const run = this.run;
      if (run === null || run.outcome !== null) return null;
      const acts = run.mission.acts;
      return run.acts_done < acts.length ? acts[run.acts_done] : null;
    }
    act_status() {
      const a = this.next_act();
      if (a === null) return { act: null, ok: false, why: '' };
      if (this.run.working !== null) return { act: a, ok: false, why: 'Already under way.' };
      if (this.ship.surfaced) return { act: a, ok: false, why: 'We are on the surface. Dive first.' };
      const why = this._unmet(a);
      if (why) return { act: a, ok: false, why };
      return { act: a, ok: true, why: '' };
    }
    _unmet(a) {
      for (const need of a.needs) if (!evaluate(need.requires, this)) return need.why || 'It cannot be done now.';
      return '';
    }
    get working() {
      const run = this.run;
      return run === null || run.working === null ? null : run.mission.acts[run.working];
    }
    get work_blocked() {
      const a = this.working;
      if (a === null) return '';
      if (this.ship.surfaced) return 'We are on the surface.';
      if (this.ship.stand_down) return 'The crew is asleep.';
      if (this.engagement !== null) return 'We are under attack.';
      if (this.ship.battery <= 0 && !this.ship.surfaced) return 'The batteries are flat.';
      return this._unmet(a);
    }
    do_act() {
      const { act, ok, why } = this.act_status();
      if (act === null) return 'There is nothing to order. The rest is waiting.';
      if (!ok) return why;
      const run = this.run;
      run.working = run.acts_done;
      run.work_left = Number(act.hours);
      this._set_progress();
      const msg = `You order it: ${act.label}.`;
      this.log.push(`${tag(this.tick_no)} > ${msg}`);
      return msg;
    }
    _set_progress() {
      const run = this.run, n = run.mission.acts.length;
      let part = 0.0;
      if (run.working !== null) part = 1.0 - run.work_left / run.mission.acts[run.working].hours;
      this.ship.progress = clamp((run.acts_done + part) / n);
    }
    _work() {
      const run = this.run;
      if (run === null || run.outcome !== null || run.working === null) return;
      if (this.work_blocked) return;
      const a = run.mission.acts[run.working];
      run.work_left -= Math.min(1.0, this.ship.readiness) * pace(this);
      if (run.work_left <= 0.0) {
        run.work_left = 0.0;
        run.acts_done += 1;
        run.working = null;
        this.log.push(`${tag(this.tick_no)} Done: ${a.label}.`);
        applyEffects(a.effects, this);
      }
      if (run.outcome === null && this.run === run) this._set_progress();
    }

    _mutiny() {
      const s = this.ship;
      if (!s.flags.has('mutiny_brewing')) { this.mutiny_clock = 0; return; }
      const live = this.active_crew();
      if (live.length && fsum(live.map((c) => c.trust)) / live.length > 0.5) {
        s.flags.delete('mutiny_brewing');
        this.log.push(`${tag(this.tick_no)} The whispering stops. The moment passes.`);
        return;
      }
      this.mutiny_clock += 1;
      if (this.mutiny_clock >= 12) {
        s.flags.add('deposed');
        this.log.push(`${tag(this.tick_no)} The crew takes the control room. You are relieved of command.`);
      }
    }

    combat(severity) { combatStart(this, severity); }
  }

  // Python's round(x, 2) rounds the exact binary value to the nearest decimal; so does toFixed.
  // They only differ on exact binary ties, which a random double in this range never is.
  function round2Python(x) { return Number(x.toFixed(2)); }

  // ---------------------------------------------------------------- endings
  const ENDING_TEXT = {
    lost_with_all_hands: ['The pressure hull gives. It is quick, and no one is left to be surprised.'],
    derelict: ['She is found drifting, with every hatch dogged from the inside.',
      'The log is kept up to the last page. The last pages are in a hand that is not the captain\'s.'],
    deposed: ['You are relieved of command in the control room, politely, by men you trained.',
      'They bring the boat home themselves. It is not recorded who gave the order.'],
    turned_back: ['You break off and turn for home. The patrol is entered as abandoned.'],
    the_price: ['The sea is flat to the horizon. The radio gives a single tone, then an order to return to base.',
      'The boat goes home with fewer men than it left with. Everyone agrees on the number, and nobody on the names.'],
    home_unaccounted: ['The pier is there. The count on the gangway does not match the roll.',
      'The harbour master says the boat is expected. He does not say by whom.'],
    forgotten_post: ['You come home to a peace that began a year ago. No one ever cancelled your orders;',
      'there was no one left to cancel them. The station is a footnote in a closed file.'],
    the_lamp: ['You come home with every order carried out. The quay is full of fishing boats with their lamps lit in broad daylight.',
      'Nobody looks at you. At night a lamp burns somewhere in the hull of your own boat, and the lookouts agree there is no lamp.'],
    stained_victory: ['You sailed home with every order carried out. The boat will never again be quiet at night.'],
    court_martial: ['There is an inquiry. The order you refused is on file, in a hand that the clerk cannot name.'],
    returned_under_a_cloud: ['You come home. The staff will have questions about the log, and some of the answers are in it.'],
    returned: ['You come home. There is nothing in the log that can be used against you.'],
    hollow_victory: ['The missions are done. There are too few left aboard to sail her out again.'],
    mission_failed: ['The patrol is entered as unsuccessful. The boat and the men are returned to the pool.'],
  };
  const SILENCE = ['The hydrophones go quiet. Not the quiet of an empty sea; the quiet of something that has stopped listening.'];

  function classifyEnding(w, initialCrew) {
    const s = w.ship, f = s.flags;
    const survivors = w.active_crew().length;
    if (s.hull <= 0 || survivors === 0) return w.vigil_ticks > 0 ? 'derelict' : 'lost_with_all_hands';
    if (f.has('deposed')) return 'deposed';
    if (f.has('aborted')) return 'turned_back';
    if (f.has('offering_made')) return 'the_price';
    if (f.has('home_unaccounted')) return 'home_unaccounted';
    if (f.has('peace_known') && f.has('left_station')) return 'forgotten_post';
    const done = w.results.filter((r) => r.outcome === 'success' || r.outcome === 'altered').length;
    if (f.has('fishermen_sunk')) return 'the_lamp';
    if (f.has('civilian_sunk') || f.has('neutral_sunk')) return 'stained_victory';
    const onRecord = !f.has('orders_unrecorded');
    if (f.has('orders_defied') && onRecord) return 'court_martial';
    if (done >= 3) {
      if (s.cohesion < 0.3 || survivors < initialCrew * 0.6) return 'hollow_victory';
      if (f.has('orders_bent') && onRecord) return 'returned_under_a_cloud';
      return 'returned';
    }
    return 'mission_failed';
  }

  function debriefDocuments(w) {
    const official = [], log = [];
    const byId = new Map(w.missions.map((m) => [m.id, m]));
    for (const r of w.results) {
      const m = byId.get(r.mission);
      official.push(`${m.title}: ${r.outcome}. Orders: ${m.mundane_origin}`);
      log.push(`${m.title}: ${r.outcome}. Orders: ${m.uncanny_origin}`);
    }
    for (const f of w.fired) {
      const ev = w.engine.byId.get(f.id);
      if (ev.beat || ev.mission || ev.radio) {
        const day = Math.floor(f.tick / 24) + 1;
        official.push(`Day ${day}: ${ev.mundane_cause}`);
        log.push(`Day ${day}: ${ev.uncanny_cause}`);
      }
    }
    const sh = w.ship, n = sh.log_true + sh.log_soft + sh.log_blank;
    if (n) {
      official.push(`The deck log was kept in good order: ${n} entr${n === 1 ? 'y' : 'ies'}.`);
      log.push(`${sh.log_true} written as it happened, ${sh.log_soft} softened, ${sh.log_blank} left blank. Somebody else wrote the rest.`);
    }
    return { official, log };
  }

  // ---------------------------------------------------------------- the people's side (dread/people.py)
  function listenRadio(w) {
    const s = w.ship;
    if (!(s.surfaced || s.scope_up)) return 'The antenna is under water. Raise the periscope or surface.';
    if (!w.active_crew().some((c) => c.role === 'radio')) return 'There is no radio man to listen.';
    if (s.flags.has('fault_radio')) return 'The set is dead.';
    w.lose_hours(1.0);
    s.attention = clamp(s.attention + 0.01);
    const allr = w.engine.events.filter((e) => e.radio);
    const err = roleError(w, 'radio');
    const ready = allr.filter((e) => w.engine.radioReady(e, w));
    if (w.rng.random() < 0.35 || !ready.length) return 'Static. Under it, something that might be music, or someone counting.';
    let pool = ready;
    if (w.rng.random() < err * 0.8) { pool = allr; w.log.push(`${tag(w.tick_no)} The clerk reads it twice, and the second reading is not the first.`); }
    const ev = w.rng.choices1(pool, pool.map((e) => (e.weight !== undefined ? e.weight : 1.0)));
    w.engine.fire(ev, w);
    return 'The radio man hands you a slip.';
  }
  function officersOf(w) {
    const out = [], live = w.active_crew();
    const first = (role) => live.find((c) => c.role === role) || null;
    for (const [title, c] of [['first officer', w.crew.length && w.crew[0].active ? w.crew[0] : null], ['chief engineer', first('engine')], ['doctor', first('medic')]]) {
      if (c !== null && out.every((o) => o[1] !== c)) out.push([title, c]);
    }
    return out;
  }
  function honestAdvice(w, title) {
    const s = w.ship, live = w.active_crew(), n = Math.max(1, live.length);
    const fatigue = fsum(live.map((c) => c.fatigue)) / n, fear = fsum(live.map((c) => c.fear)) / n;
    if (title === 'chief engineer') {
      if (s.hull < 0.7) return `She is hurt, sir. At this state I would not take her below ${crushDepth(s.hull) - 30} metres.`;
      if (s.battery < 0.3) return 'We have to charge, sir, and soon.';
      if (s.spares < 0.3) return 'We are nearly out of things to mend her with.';
      return 'The engines are sound.';
    }
    if (title === 'doctor') {
      const ill = live.filter((c) => c.ill).length;
      if (ill) return `${ill === 1 ? 'One man is' : ill + ' men are'} sick, sir, and some of them are hiding it.`;
      if (fear > 0.5) return 'It is fear, sir. Not fever.';
      return 'They will do.';
    }
    if (fatigue > 0.6) return 'The men are close to the end, sir. Let them sleep.';
    if (s.orders_doubt > 0.3) return 'I would like those orders verified, sir.';
    if (s.moral_debt > 0.3) return 'They are not sleeping, sir. Not since the steamer.';
    return 'Steady, sir. Nothing that is not on the board.';
  }
  function callCouncil(w) {
    const s = w.ship, officers = officersOf(w);
    if (!officers.length) return 'There is nobody to ask.';
    w.lose_hours(0.5);
    const look = new PyRandom(w.tick_no * 8101 + 13);
    for (const [title, c] of officers) {
      const p = Math.max(0.0, Math.min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)));
      const said = look.random() < p ? honestAdvice(w, title) : 'Whatever you think best, sir.';
      w.log.push(`${tag(w.tick_no)} ${c.name}, ${title}: "${said}"`);
      c.trust = clamp(c.trust + (c.trust > 0.5 ? 0.02 : -0.02));
    }
    s.flags.add('council_recent');
    w.flag_expiry.set('council_recent', w.tick_no + 24);
    return 'The officers are called to the wardroom.';
  }
  function healthTick(w) {
    const s = w.ship, live = w.active_crew();
    const illN = live.filter((c) => c.ill && !c.isolated).length;
    for (const c of live) {
      if (!c.ill) {
        const p = 0.0015 + ((s.food < 0.4 || s.water < 0.4) ? 0.004 : 0.0) + (s.co2 > 0.03 ? 0.003 : 0.0) + 0.002 * illN;
        if (w.rng.random() < p) { c.ill = true; c.ill_ticks = 0; c.hides = c.candor < 0.5 && c.trust < 0.6; }
      } else {
        c.ill_ticks += 1;
        c.fatigue = clamp(c.fatigue + 0.008);
        c.fear = clamp(c.fear + 0.002);
        if (c.ill_ticks > 40 && w.rng.random() < 0.02) {
          c.alive = false;
          w.log.push(`${tag(w.tick_no)} ${c.name} does not wake. The medic says what it was; nobody remembers the word.`);
        } else if (w.rng.random() < 0.01) { c.ill = false; c.hides = false; }
      }
    }
  }
  function sickCall(w) {
    const live = w.active_crew();
    if (!live.some((c) => c.role === 'medic')) return 'There is no medic. You do what you can, and it is not much.';
    w.lose_hours(0.5);
    const sick = live.filter((c) => c.ill);
    if (!sick.length) return 'Every man is fit, or says so.';
    const cured = [];
    for (const c of sick) { c.hides = false; if (w.rng.random() < 0.7) { c.ill = false; cured.push(c.name); } }
    w.log.push(`${tag(w.tick_no)} The medic goes berth by berth. ` + (cured.length ? `${cured.join(', ')} ${cured.length === 1 ? 'is' : 'are'} treated.` : 'He can do nothing.'));
    return `${sick.length} sick found.`;
  }
  function writeLog(w) {
    const s = w.ship;
    if (w.tick_no - s.last_log < 24) return 'Not yet. The page is still wet from the last entry.';
    s.last_log = w.tick_no;
    const mk = (key, text, tags, cost, effects) => ({ key, text, tags, cost, effects });
    w.pending = { event_id: 'log_entry', text: 'The day\'s entry. Three things happened that you would rather not have written down.', target_id: null, choices: [
      mk('true', 'Write what happened, as it happened.', ['care'], 'It is on record. So is the rest.', [{ op: 'log_entry', kind: 'true' }, { op: 'ship', stat: 'moral_debt', value: -0.03 }, { op: 'crew', who: 'all', stat: 'trust', value: 0.01 }]),
      mk('soft', 'Soften it. A rough night, a difficult man.', ['comply'], 'Easier. The page will be read, someday.', [{ op: 'log_entry', kind: 'soft' }, { op: 'ship', stat: 'moral_debt', value: 0.02 }]),
      mk('blank', 'Leave the page blank.', ['silence'], 'The men notice what the captain does not write.', [{ op: 'log_entry', kind: 'blank' }, { op: 'crew', who: 'all', stat: 'trust', value: -0.01 }]),
    ] };
    return 'You open the log.';
  }

  // ---------------------------------------------------------------- the living sea (dread/sea.py)
  const hourOf = (w) => (6 + w.tick_no) % 24;
  const isNight = (w) => { const h = hourOf(w); return h >= 20 || h < 5; };
  function visibility(w) {
    let v = 12.0;
    if (isNight(w)) v *= 0.4;
    if (w.ship.flags.has('fog')) v *= 0.25;
    if (w.ship.surfaced) v *= 1.2 - 0.6 * roleError(w, 'deck');
    return v;
  }
  function updateTraffic(w) {
    for (const o of w.traffic.slice()) {
      o.x += o.vx; o.y += o.vy; o.age += 1;
      if (o.age >= o.life) w.traffic.splice(w.traffic.indexOf(o), 1);
    }
    if (w.engagement === null && w.traffic.length < 3 && w.rng.random() < 0.05) {
      const [bx, by] = trueXY(w);
      const d = DIRS[Math.trunc(w.rng.random() * 8)];
      const dist = 12 + Math.trunc(w.rng.random() * 14);
      const v = DIRS[Math.trunc(w.rng.random() * 8)];
      const speed = 4 + w.rng.random() * 4;
      const kind = w.rng.random() < 0.6 ? 'merchant' : 'fishing';
      const flag = w.rng.random() < 0.5 ? 'neutral' : 'enemy';
      const life = 12 + Math.trunc(w.rng.random() * 18);
      w.traffic_id += 1;
      w.traffic.push({ id: w.traffic_id, kind, flag, x: bx + d[0] * dist, y: by + d[1] * dist, vx: v[0] * speed, vy: v[1] * speed, age: 0, life });
    }
  }
  function trafficRange(w, o) { const [bx, by] = trueXY(w); return Math.hypot(o.x - bx, o.y - by) * 0.9; }
  function trafficNear(w) { return w.engagement !== null ? 0 : w.traffic.filter((o) => trafficRange(w, o) <= 7.0).length; }
  function takeFix(w) {
    const s = w.ship;
    let factor, how;
    if (s.surfaced) {
      if (isNight(w)) { factor = 0.15; how = 'the stars'; }
      else if (w.active_crew().some((c) => c.role === 'radio') && !s.flags.has('fault_radio')) { factor = 0.5; how = 'radio bearings'; }
      else return 'No stars, and no radio to take bearings on.';
    } else if (s.scope_up) {
      if (visibility(w) < 4.0) return 'There is nothing to take a bearing on in this visibility.';
      factor = 0.4; how = 'the coast through the periscope';
      s.attention = clamp(s.attention + 0.01);
    } else return 'A fix needs the periscope or the surface.';
    s.dr_error = Math.max(0.3, s.dr_error * factor);
    s.last_fix = w.tick_no;
    w.lose_hours(1.0);
    return `Fix by ${how}. We are within about ${s.dr_error.toFixed(1)} nm of where we think we are.`;
  }
  const eyeLies = (w, o) => periscope(w, 0).distortions.length > 0 && (o.id + w.tick_no) % 3 === 0;
  function trafficAct(w, action) {
    const s = w.ship;
    const near = w.traffic.filter((o) => trafficRange(w, o) <= 7.0);
    if (!near.length) { w.log.push(`${tag(w.tick_no)} There is nothing there now.`); return; }
    let o = near[0];
    for (const x of near) if (trafficRange(w, x) < trafficRange(w, o)) o = x;
    const kind = o.kind === 'merchant' ? 'steamer' : 'fishing boat';
    if (action === 'pass') w.log.push(`${tag(w.tick_no)} The ${kind} crosses and goes on about her business.`);
    else if (action === 'shadow') {
      w.lose_hours(3.0);
      s.attention = clamp(s.attention + 0.02);
      const seen = !eyeLies(w, o) ? o.flag : (o.flag === 'neutral' ? 'enemy' : 'neutral');
      w.log.push(`${tag(w.tick_no)} Three hours on her quarter. She wears ${seen === 'neutral' ? "a neutral's stripes" : 'an enemy ensign'}.`);
    } else if (action === 'sink') {
      const n = Math.min(2, s.torpedoes);
      if (n === 0) { w.log.push(`${tag(w.tick_no)} There is nothing left to fire.`); return; }
      for (let k = 0; k < n; k++) spendOne(w);
      s.noise = clamp(s.noise + 0.2);
      w.traffic.splice(w.traffic.indexOf(o), 1);
      if (o.flag === 'neutral' || o.kind === 'fishing') {
        s.moral_debt = clamp(s.moral_debt + 0.35);
        for (const c of w.active_crew()) { c.guilt = clamp(c.guilt + 0.15); c.trust = clamp(c.trust - 0.06); }
        s.flags.add('neutral_sunk');
        w.log.push(`${tag(w.tick_no)} The ${kind} goes down by the stern. There is a flag on the surface, and it is not the one you were told to expect.`);
      } else {
        for (const c of w.active_crew()) { c.trust = clamp(c.trust + 0.03); c.guilt = clamp(c.guilt + 0.03); }
        s.flags.add('enemy_sunk');
        w.log.push(`${tag(w.tick_no)} The ${kind} breaks in two. Nobody cheers, and nobody looks at the others.`);
      }
    }
  }

  // ---------------------------------------------------------------- the lookout (dread/nav.py)
  function sightingLine(name, kind, rel, dist) {
    const a = Math.abs(rel);
    const where = a < 20 ? 'dead ahead' : a < 60 ? (rel > 0 ? 'on the starboard bow' : 'on the port bow') : a < 120 ? (rel > 0 ? 'on the starboard beam' : 'on the port beam')
      : a < 160 ? (rel > 0 ? 'on the starboard quarter' : 'on the port quarter') : 'astern';
    const n = Math.max(1, Math.round(dist));
    return `${name}, lookout: a ${kind} ${where}, about ${n} mile${n > 1 ? 's' : ''}.`;
  }
  function lookout(w) {
    const s = w.ship;
    if (!s.surfaced) return [];
    const deck = w.active_crew().filter((c) => c.role === 'deck');
    if (!deck.length) return ['Nobody is posted on the bridge.'];
    const man = deck[0], look = new PyRandom(w.tick_no * 5233 + 19);
    const candor = Math.max(0.0, Math.min(1.0, man.candor * man.trust * (0.6 + 0.4 * s.cohesion)));
    const heading = where(w).heading, me = trueXY(w), vis = visibility(w), seen = [], run = w.run;
    const ch = run !== null && run.outcome === null ? run.mission.chart : null;
    const tgt = ch ? ch.target : null;
    if (tgt && run.acts_done >= 1) {
      const dist = Math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9;
      if (dist <= vis) {
        const kind = { capital: 'warship', convoy: 'smudge of smoke, several ships', steamer: 'steamer' }[(ch.sight || {}).kind] || 'steamer';
        seen.push([bearing(me, tgt), dist, kind]);
      }
    }
    for (const o of w.traffic) {
      const dist = Math.hypot(o.x - me[0], o.y - me[1]) * 0.9;
      if (dist <= vis) seen.push([bearing(me, [o.x, o.y]), dist, o.kind === 'merchant' ? 'steamer' : 'fishing boat']);
    }
    const lines = [];
    for (const [brg, dist, kind] of seen) if (look.random() < candor) lines.push(sightingLine(man.name, kind, wrap180(brg - heading), dist));
    if (look.random() < roleError(w, 'deck') * 0.6) {
      const brg = Math.trunc(look.random() * 360);
      lines.push(sightingLine(man.name, 'sail', wrap180(brg - heading), 4 + (brg % 5)));
    }
    return lines;
  }

  // ---------------------------------------------------------------- navigation and instruments (dread/nav.py)
  const COLUMNS = 'ABCDEFGHIJK', BASE = [100.0, 12.0, 'Base'], RETURN_TICKS = 18;
  const gridRef = (x, y) => `${COLUMNS[Math.max(0, Math.min(10, Math.floor(x / 10)))]}-${Math.max(1, Math.min(8, Math.floor(y / 10) + 1))}`;
  const lerp2 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const bearing = (a, b) => ((Math.round(Math.atan2(b[0] - a[0], a[1] - b[1]) * 180 / Math.PI) % 360) + 360) % 360;
  const ceilDiv = (x) => Math.max(1, Math.ceil(x));

  function where(w) {
    const s = w.ship, run = w.run;
    const ch = run !== null ? run.mission.chart : null;
    const pts = ch ? [ch.from].concat(ch.points) : [];
    let pos, heading = 0, nxt = '', rng = 0.0;
    if (!pts.length) {
      pos = [BASE[0], BASE[1]];
    } else if (run.mission.kind === 'hold') {
      const st = pts[pts.length - 1];
      pos = [st[0], st[1]];
      if (s.returning) {
        const t = 1.0 - w.travel_left / RETURN_TICKS;
        pos = lerp2(st, BASE, Math.max(0.0, Math.min(1.0, t)));
        heading = bearing(st, BASE); nxt = 'Base';
        rng = Math.hypot(BASE[0] - pos[0], BASE[1] - pos[1]) * 0.9;
      }
    } else {
      const n = pts.length - 1;
      let i = Math.min(run.acts_done, n - 1), t = 0.0;
      if (run.working !== null) t = 1.0 - run.work_left / run.mission.acts[run.working].hours;
      if (run.acts_done >= n) { i = n - 1; t = 1.0; }
      pos = lerp2(pts[i], pts[i + 1], t);
      heading = bearing(pts[i], pts[i + 1]);
      nxt = pts[i + 1][2];
      rng = Math.hypot(pts[i + 1][0] - pos[0], pts[i + 1][1] - pos[1]) * 0.9;
    }
    return { pos, heading, nxt, rng };
  }
  const DIRS = [[1.0, 0.0], [0.7, 0.7], [0.0, 1.0], [-0.7, 0.7], [-1.0, 0.0], [-0.7, -0.7], [0.0, -1.0], [0.7, -0.7]];
  const trueXY = (w) => { const p = where(w).pos; return [Math.round(p[0] * 10) / 10, Math.round(p[1] * 10) / 10]; };
  function navigation(w) {
    const s = w.ship, run = w.run;
    const { pos, heading, nxt, rng } = where(w);
    const off = s.dr_error / 0.9, d = DIRS[(Math.floor(w.tick_no / 12) * 5 + 3) % 8];
    const est = [Math.max(0.0, Math.min(109.9, pos[0] + d[0] * off)), Math.max(0.0, Math.min(79.9, pos[1] + d[1] * off))];
    const moving = s.returning || (w.working !== null && !w.work_blocked);
    let speed;
    if (s.surfaced) speed = moving ? 11.0 : 4.0;
    else if (s.returning) speed = 9.0;
    else if (moving) speed = SPEEDS[s.speed_order][1] * Math.min(1.0, s.readiness) * ENGINE_FACTOR[systemState(w, 'engine room')];
    else speed = 2.5;
    if (s.battery <= 0 && !s.surfaced) speed = 0.0;
    if (s.silent_running && !s.surfaced) speed = Math.min(speed, 3.0);
    return {
      x: Math.round(est[0] * 10) / 10, y: Math.round(est[1] * 10) / 10, grid: gridRef(est[0], est[1]), heading, err_nm: Math.round(s.dr_error * 10) / 10,
      speed: Math.round(speed * 10) / 10, depth: depthM(w), keel: underKeel(w), range_nm: Math.round(rng), next: nxt,
      eta_h: run !== null && run.working !== null ? ceilDiv(run.work_left) : null, noise: s.noise,
    };
  }
  function hullReport(w) {
    return COMPARTMENTS.map((c) => {
      const integrity = Math.max(0.0, Math.min(1.0, 1.0 - 2.0 * w.ship.damage[c]));
      return { name: c, integrity, state: integrity < 0.35 ? 'flooding' : integrity < 0.7 ? 'damaged' : 'sound' };
    });
  }
  // the scope (dread/nav.py: contacts)
  const SCOPE_NM = 30;
  const LABEL_POOL = ['single screw, steady', 'heavy screws, slow', 'many screws, slow', 'faint screws, irregular', 'fast screws, closing', 'no screw count', 'heavy screws, steady'];
  function sonarReports(w) {
    const s = w.ship, look = new PyRandom(w.tick_no * 104729 + 5), out = [];
    if (s.flags.has('fault_sonar')) return [];
    for (const p of w.deck.phantoms) {
      for (const cid of Array.from(p.audible_to).sort((a, b) => a - b)) {
        const c = w.crew_by_id(cid);
        if (!c || !c.active) continue;
        const candor = Math.max(0.0, Math.min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)));
        if (look.random() < candor) out.push({ p, line: `${c.name} reports: “${p.text}”` });
        else if (p.audible_to.size >= 2) out.push({ p: null, line: 'The sonar room has gone quiet around the headphones.' });
        break;
      }
    }
    return out;
  }
  function contactRows(w) {
    const s = w.ship, run = w.run;
    if (!(s.sonar_on || s.surfaced) || s.flags.has('fault_sonar')) return [];
    const raw = [], me = trueXY(w);
    const tgt = run !== null && run.outcome === null && run.mission.chart ? run.mission.chart.target : null;
    const drop = new PyRandom(w.tick_no * 3571 + 11).random() < 0.12;
    if (tgt && run.acts_done >= 1 && !drop) {
      const dist = Math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9;
      if (dist <= SCOPE_NM) raw.push([bearing(me, tgt), dist, tgt[2], true]);
    }
    if (s.flags.has('in_combat')) {
      const k = Math.floor(w.tick_no / 5), n = w.engagement !== null ? w.engagement.escorts : 1;
      for (let i = 0; i < n; i++) raw.push([(k * 83 + 17 + i * 71) % 360, 3 + (k * 7 + i * 5) % 6, 'fast screws, closing', true]);
    }
    for (const o of w.traffic) {
      const dist = Math.hypot(o.x - me[0], o.y - me[1]) * 0.9;
      if (dist <= SCOPE_NM) raw.push([bearing(me, [o.x, o.y]), dist, o.kind === 'merchant' ? LABEL_POOL[0] : LABEL_POOL[3], true]);
    }
    if (s.sonar_on) {
      for (const r of sonarReports(w)) {
        const p = r.p;
        if (p !== null && p.kind === 'echo') raw.push([(p.id * 97 + 41 + p.age * 2) % 360, 4 + (p.id * 53 + p.age) % 22, LABEL_POOL[(p.id * 7) % LABEL_POOL.length], false]);
      }
    }
    raw.sort((a, b) => a[0] - b[0]);
    return raw;
  }
  /** Real and false contacts, drawn alike: nothing here says which is which. */
  function contacts(w) {
    return contactRows(w).map((r, i) => ({ tag: `C${i + 1}`, bearing: Math.trunc(r[0]), range_nm: Math.round(r[1] * 10) / 10, label: r[2] }));
  }

  // torpedoes and the periscope (dread/nav.py)
  const YARDS_PER_NM = 2025, TORPEDO_KNOTS = 30, VIS_NM = 12, FIELD_DEG = 50;
  const TUBE_STATES = ['empty', 'loaded', 'flooded', 'open'];
  const DISTORTIONS = ['figures_on_rail', 'cross_on_hull', 'second_hull', 'lamp', 'wake_wrong'];
  const wrap180 = (d) => ((((d % 360) + 360) % 360 + 180) % 360) - 180;
  function roomError(crew) {
    if (!crew.length) return 0.6;
    const strain = fsum(crew.map((c) => (c.fear + c.fatigue) / 2)) / crew.length;
    return Math.max(0.0, Math.min(0.6, 1.2 * strain - 0.2));
  }
  function solutionError(w) {
    const s = w.ship, pRoom = roomError(w.active_crew().filter((c) => c.role === 'torpedo'));
    if (s.surfaced || s.scope_up) {
      const ps = periscope(w, 0);
      if (ps.ship !== null) return ps.distortions.length ? 0.5 : pRoom * 0.4;
    }
    return pRoom;
  }
  function weapons(w) {
    const s = w.ship, crew = w.active_crew().filter((c) => c.role === 'torpedo'), stock = s.torpedoes;
    if (!crew.length) return { stock, manned: false, tubes: Array(6).fill('no report'), solutions: [], types: Object.assign({}, s.types), loaded: s.torpedo_type };
    const p = roomError(crew);
    const look = new PyRandom(w.tick_no * 2711 + 3);
    const tubes = s.tubes.map((st) => (look.random() < p ? look.choice(TUBE_STATES.filter((x) => x !== st)) : st));
    const nv = navigation(w), sols = [];
    for (const c of contacts(w)) {
      const jb = look.random(), jr = look.random();
      const brg = (((Math.round(c.bearing + (jb - 0.5) * 2 * p * 20)) % 360) + 360) % 360;
      const rng = c.range_nm * (1 + (jr - 0.5) * p * 0.6);
      sols.push({ tag: c.tag, bearing: brg, range_yd: Math.round(rng * YARDS_PER_NM / 10) * 10, run_s: Math.round(rng / TYPE_KN[s.torpedo_type] * 3600), gyro: wrap180(brg - nv.heading) });
    }
    return { stock, manned: true, tubes, solutions: sols, types: Object.assign({}, s.types), loaded: s.torpedo_type };
  }
  function periscope(w, train) {
    train = train || 0;
    const s = w.ship, nv = navigation(w);
    const centre = (((nv.heading + train) % 360) + 360) % 360;
    if (!(s.surfaced || s.scope_up)) return { mode: 'down', train, centre, ship: null, distortions: [], ghosts: [], others: [], visibility: 0.0 };
    const mode = s.surfaced ? 'bridge' : 'periscope', me = trueXY(w), run = w.run, vis = visibility(w);
    let ship = null;
    const ch = run !== null && run.outcome === null ? run.mission.chart : null;
    const tgt = ch ? ch.target : null;
    if (tgt && run.acts_done >= 1) {
      const dist = Math.hypot(tgt[0] - me[0], tgt[1] - me[1]) * 0.9;
      if (dist <= vis) {
        const brg = bearing(me, tgt), rel = wrap180(brg - centre), sight = ch.sight || {};
        ship = { bearing: brg, rel, range_nm: Math.round(dist * 10) / 10, in_field: Math.abs(rel) <= Math.floor(FIELD_DEG / 2),
          kind: sight.kind || 'steamer', escorts: sight.escorts || 0, ships: sight.ships || 1, markings: !!sight.markings };
      }
    }
    const live = w.active_crew();
    const strain = live.length ? fsum(live.map((c) => (c.fear + c.fatigue) / 2)) / live.length : 1.0;
    const p = Math.max(0.0, Math.min(0.7, strain + 0.3 * s.moral_debt + 0.3 * s.attention - 0.15 + (isNight(w) ? 0.08 : 0.0) + (s.flags.has('fog') ? 0.12 : 0.0)));
    const look = new PyRandom(Math.floor(w.tick_no / 3) * 6733 + 29), kinds = [];
    if (look.random() < p) {
      kinds.push(look.choice(DISTORTIONS));
      if (look.random() < p * 0.5) kinds.push(look.choice(DISTORTIONS));
    }
    const g = new PyRandom(Math.floor(w.tick_no / 3) * 4219 + 7), ghosts = [];
    for (const r of contactRows(w)) {
      if (r[3]) continue;
      const rel = wrap180(r[0] - centre);
      if (Math.abs(rel) <= Math.floor(FIELD_DEG / 2) && g.random() < 0.5) ghosts.push(Math.trunc(rel));
    }
    const others = [];
    for (const o of w.traffic) {
      const dist = Math.hypot(o.x - me[0], o.y - me[1]) * 0.9;
      if (dist <= vis) {
        const brg = bearing(me, [o.x, o.y]), rel = wrap180(brg - centre);
        others.push({ kind: o.kind, bearing: brg, rel, range_nm: Math.round(dist * 10) / 10, in_field: Math.abs(rel) <= Math.floor(FIELD_DEG / 2) });
      }
    }
    return { mode, train, centre, ship, distortions: kinds, ghosts, others, visibility: vis };
  }
  /** Every mission's waypoints, for drawing the chart: those behind, the one under way, those to come. */
  function chartTracks(w) {
    return w.missions.map((m, i) => ({
      id: m.id, state: i < w.mission_i ? 'done' : i === w.mission_i ? 'current' : 'ahead',
      points: m.chart && i <= w.mission_i ? [m.chart.from].concat(m.chart.points) : [],   // orders not yet received are not on the chart
      reached: i < w.mission_i ? 99 : i === w.mission_i && w.run ? w.run.acts_done : 0,
    }));
  }

  const TITLES = { engagement_turn: 'UNDER ATTACK', log_entry: "THE DAY'S ENTRY", council: 'THE OFFICERS' };

  // ---------------------------------------------------------------- the captain's orders menu
  const WAIT_LIMIT = 12;

  /** Same menu as dread/play.py: available_orders(w). */
  function availableOrders(w) {
    const s = w.ship, items = [];
    const add = (id, label, hint, run, needsCrew, kind, why) => items.push({ id, label, hint, run, needsCrew: !!needsCrew, kind: kind || 'order', why: why || '' });
    const st = w.act_status();
    if (w.working !== null) {
      const left = Math.max(1, Math.ceil(w.run.work_left));
      add('act', `Under way: ${w.working.label}`, `about ${left} h more`, () => '', false, 'act', w.work_blocked || 'The hours must pass.');
    } else if (st.act !== null) {
      const a = st.act;
      add('act', a.label, a.hint ? `${a.hours} h; ${a.hint}` : `${a.hours} h`, () => w.do_act(), false, 'act', st.ok ? '' : st.why);
    }
    if (s.sonar_on) add('silence_sonar', 'Silence the sonar', 'the headsets go quiet; so does the warning', () => orders.silence_sonar(w));
    else add('restore_sonar', 'Switch the sonar back on', 'you will hear what they heard', () => orders.restore_sonar(w));
    if (s.rest_cancelled) add('grant_rest', 'Resume normal watches', '', () => orders.grant_rest(w));
    else add('cancel_rest', 'Cancel rest for all hands', 'faster now; slower later', () => orders.cancel_rest(w));
    if (!s.stand_down) add('stand_down', 'Stand down: all hands but a skeleton watch sleep', 'a broken crew recovers; the boat sleeps unwatched', () => orders.stand_down(w));
    add('hold_ritual', 'Mess together: music, cards, a hot meal', 'costs hours of the patrol', () => orders.hold_ritual(w));
    add('address_crew', 'Speak to the crew over the intercom', 'works in proportion to what they still believe', () => orders.address_crew(w));
    add('scrub_air', 'Break out fresh absorbent', `${(s.scrubber * 100).toFixed(0)}% left`, () => orders.scrub_air(w));
    if (s.surfaced) add('dive', 'Dive', '', () => orders.dive(w));
    else add('surface', 'Surface for air', 'air, and the sky can see you', () => orders.surface(w));
    add(s.silent_running ? 'normal_running' : 'silent_running', s.silent_running ? 'Resume normal running' : 'Silent running',
      'quiet in a fight; slow in a race', () => orders.silent_running(w, !s.silent_running));
    add('active_ping', 'One active ping', 'information; and a sound the water carries', () => orders.active_ping(w));
    if (!s.surfaced) add(s.scope_up ? 'lower_periscope' : 'raise_periscope', s.scope_up ? 'Lower the periscope' : 'Raise the periscope', s.scope_up ? '' : 'you see; and you are seen', () => (s.scope_up ? orders.lower_periscope(w) : orders.raise_periscope(w)));
    for (const lv of ['slow', 'standard', 'flank']) {
      if (lv !== s.speed_order) add(`speed_${lv}`, `Ahead ${lv}`, { slow: 'quiet and sparing; the work crawls', standard: '', flank: 'fast; loud, and the batteries go' }[lv], () => orders.set_speed(w, lv));
    }
    if (!s.surfaced) {
      for (const [lv, m] of [['shallow', 60], ['deep', 120], ['test', 180]]) {
        if (lv !== s.depth_order) add(`depth_${lv}`, `Go to ${m} metres`, { shallow: '', deep: 'hidden; the hull speaks', test: 'as deep as she is built for' }[lv], () => orders.set_depth(w, lv));
      }
      if (s.scope_up) add(s.snorkel ? 'snorkel_off' : 'snorkel_on', s.snorkel ? 'Stop the diesels' : 'Run the diesels at snorkel depth', s.snorkel ? '' : 'charges the batteries; loud, and the sea can hear it', () => orders.snorkel(w, !s.snorkel));
    }
    if (s.hull < 0.999 || s.dc_active) add('damage_control', s.dc_active ? 'Stand the damage control party down' : 'Damage control: all hands to the worst compartment', `spares ${(s.spares * 100).toFixed(0)}%`, () => orders.damage_control(w, !s.dc_active));
    add('listen_radio', 'Listen at the radio', 'surfaced or periscope up; an hour at the set', () => orders.listen_radio(w));
    add('call_council', 'Call the officers', 'an hour; they say what they say', () => orders.call_council(w));
    add('sick_call', 'Sick call', 'the medic goes berth by berth', () => orders.sick_call(w));
    add('write_log', "Write the day's entry", 'what you leave out, someone will read', () => orders.write_log(w));
    for (const kind of ['steam', 'electric', 'acoustic']) {
      if (kind !== s.torpedo_type && s.types[kind] > 0 && w.engagement === null) add(`load_${kind}`, `Load ${kind} torpedoes (${s.types[kind]} aboard)`, { steam: 'fast, and it leaves a wake the escorts can follow', electric: 'slow, quiet, no wake', acoustic: 'homes on noise; and not always on the right noise' }[kind], () => orders.load_torpedoes(w, kind));
    }
    add('take_fix', 'Take a fix', 'periscope, stars or radio bearings; an hour', () => orders.take_fix(w));
    if (w.run !== null && !w.run.phase_fired.has('verified')) {
      add('verify_orders', 'Ask headquarters to confirm the orders', 'an answer is not the same as a source', () => orders.verify_orders(w));
    }
    if (w.on_station) {
      const nxt = { 1.0: 0.75, 0.75: 0.5, 0.5: 1.0 }[Math.round(s.rations * 4) / 4];
      add('rations', `Set rations to ${(nxt * 100).toFixed(0)}%`, 'stores last longer; men notice who eats', () => {
        if (nxt < s.rations) for (const c of w.active_crew()) c.trust = Math.max(0.0, c.trust - 0.02);
        s.rations = nxt;
        return `Rations are now ${(nxt * 100).toFixed(0)}%.`;
      });
      add('check_world', 'Surface and listen for the world', 'exposed; and you may hear something', () => w.check_world());
      add('leave_station', 'Set course for base', 'diesel for the passage; the order has not been revoked', () => w.leave_station());
    }
    add('isolate', 'Confine a man', 'cuts a rumor; he will remember', (cid) => orders.isolate(w, cid), true);
    if (w.active_crew().some((c) => c.isolated)) add('release', 'Release a man from confinement', '', (cid) => orders.release(w, cid), true);
    add('force_compartment', 'Order a man into the flooded compartment', 'the job gets done', (cid) => orders.force_compartment(w, cid), true);
    return items;
  }

  // ---------------------------------------------------------------- the game: world + inputs
  const SAYS = [[0.25, 'says he is fine'], [0.45, 'says he is tired'], [0.65, 'says it has been hard'], [1.01, 'says nothing good']];
  const says = (x) => SAYS.find(([cut]) => x < cut)[1];
  const AIR = (co2) => (co2 < 0.01 ? 'clear' : co2 < 0.02 ? 'stale' : co2 < 0.035 ? 'foul' : 'dangerous');

  class Game {
    constructor(seed, opts) {
      this.seed = seed;
      this.opts = opts || {};
      this.w = new World(seed, this.opts);
      this.initial = this.w.crew.length;
      this.inputs = [];
      this.notice = '';
      this.over = false;
      this.ending = null;
    }
    _after() {
      if (this.w.finished && !this.over) { this.over = true; this.ending = classifyEnding(this.w, this.initial); }
    }
    _advance(hours, stopOnNews) {
      const w = this.w, seen = w.log.length;
      for (let i = 0; i < hours; i++) {
        if (w.finished || w.pending !== null) break;
        w.tick();
        if (stopOnNews && (w.pending !== null || w.log.length > seen)) break;
      }
      this._after();
    }
    /** One input from the player. Recorded, so a game can be replayed exactly from its seed. */
    do(input) {
      if (this.over) return;
      const w = this.w;
      const [kind, a, b] = input.split(':');
      this.notice = '';
      if (kind === 'c') {
        if (w.pending === null) return;
        const ch = w.pending.choices[Number(a)];
        if (!ch) return;
        w.choose(ch.key);
        this._after();
      } else if (w.pending !== null) {
        return;                                   // a decision stops the clock: nothing else counts
      } else if (kind === 't') {
        this._advance(1, false);
      } else if (kind === 'w') {
        this._advance(WAIT_LIMIT, true);
      } else if (kind === 'o') {
        const item = availableOrders(w).find((i) => i.id === a);
        if (!item) return;
        if (item.why) { this.notice = item.why; return; }
        this.notice = String(item.run(b !== undefined ? Number(b) : undefined) || '');
      } else {
        return;
      }
      this.inputs.push(input);
    }
    serialize() { return { seed: this.seed, inputs: this.inputs.slice() }; }
    static restore(saved, opts) {
      const g = new Game(saved.seed, opts);
      for (const i of saved.inputs) g.do(i);
      return g;
    }

    /** Where the mission stands, as steps ordered; same wording as dread/hud.py step_line. */
    _step() {
      const w = this.w, run = w.run, acts = run.mission.acts;
      if (!acts.length) return { text: 'Station: nothing is asked of you but to stay.', n: 0, of: 0, working: false };
      if (run.acts_done >= acts.length) return { text: 'Every step ordered. What remains is not up to the sea.', n: acts.length, of: acts.length, working: false };
      const a = acts[run.acts_done];
      const state = run.working !== null ? `under way, ${Math.max(1, Math.ceil(run.work_left))} h more` : 'waiting for your order';
      return { text: `Step ${run.acts_done + 1} of ${acts.length}: ${a.label} (${state})`, n: run.acts_done, of: acts.length, working: run.working !== null };
    }

    /** Everything the screen may show. Hidden values are not in here, so they cannot leak. */
    view() {
      const w = this.w, s = w.ship;
      const day = Math.floor(w.tick_no / 24) + 1, hour = (6 + w.tick_no) % 24;
      const live = w.active_crew().length;
      const share = live / 12;
      const rows = new Map(w.report().map((r) => [r.id, r]));
      const men = w.crew.filter((c) => c.alive).map((c) => {
        if (c.missing) return { id: c.id, name: c.name, role: c.role, missing: true, says: '', seen: [], confined: false };
        const r = rows.get(c.id);
        return { id: c.id, name: c.name, role: c.role, missing: false, says: says(r.says), seen: r.symptoms, confined: c.isolated };
      });
      const look = new PyRandom(w.tick_no * 104729 + 5);
      const reports = [];
      for (const p of w.deck.phantoms) {
        for (const cid of Array.from(p.audible_to).sort((a, b) => a - b)) {
          const c = w.crew_by_id(cid);
          if (!c || !c.active) continue;
          const candor = Math.max(0.0, Math.min(1.0, c.candor * c.trust * (0.6 + 0.4 * s.cohesion)));
          if (look.random() < candor) reports.push(`${c.name} reports: “${p.text}”`);
          else if (p.audible_to.size >= 2) reports.push('The sonar room has gone quiet around the headphones.');
          break;
        }
      }
      const m = w.run ? w.run.mission : null;
      const pending = w.pending ? {
        id: w.pending.event_id, text: w.pending.text,
        title: TITLES[w.pending.event_id] || w.pending.event_id.replace(/^m\d_/, '').replace(/_/g, ' ').toUpperCase(),
        choices: w.pending.choices.map((c) => ({ label: c.text, cost: c.cost })),
      } : null;
      const v = {
        over: this.over, ending: this.ending, notice: this.notice, tick: w.tick_no, day, hour,
        clocks: {
          drift: s.flags.has('clock_drift'),
          calendar: w.on_station && w.vigil_ticks >= 24 ? { log: day, chrono: day + Math.floor(w.vigil_ticks / 24) } : null,
        },
        mission: m ? { title: m.title, briefing: m.briefing, provenance: provenanceLine(m), index: w.mission_i + 1, total: w.missions.length, step: this._step() } : null,
        ledger: {
          hull: s.hull, fuel: s.fuel, food: s.food, water: s.water, scrubber: s.scrubber, rations: s.rations,
          co2: s.co2, air: AIR(s.co2), men: live, torpedoes: s.torpedoes, battery: s.battery, spares: s.spares,
          food_day: 0.0036 * share * s.rations * 24 * 100, water_day: 0.0042 * share * s.rations * 24 * 100,
        },
        men, sonar: { on: s.sonar_on, reports: s.sonar_on ? reports.slice(0, 3) : [] },
        surfaced: s.surfaced, on_station: w.on_station,
        helm: { speed: s.speed_order, depth: s.depth_order, snorkel: s.snorkel, dc: s.dc_active, lag: s.helm_pending !== null },
        lookout: lookout(w), nav: navigation(w), hull: hullReport(w), contacts: contacts(w), weapons: weapons(w), tracks: chartTracks(w), base: { x: BASE[0], y: BASE[1] },
        log: w.log.filter((l) => l.trim()),
        pending,
        orders: pending || this.over ? [] : availableOrders(w).map((i) => ({ id: i.id, label: i.label, hint: i.hint, needsCrew: i.needsCrew, kind: i.kind, why: i.why })),
        pickable: {
          isolate: w.active_crew().map((c) => ({ id: c.id, name: c.name, role: c.role })),
          force_compartment: w.active_crew().map((c) => ({ id: c.id, name: c.name, role: c.role })),
          release: w.active_crew().filter((c) => c.isolated).map((c) => ({ id: c.id, name: c.name, role: c.role })),
        },
      };
      if (this.over) {
        const docs = debriefDocuments(w);
        v.epilogue = (ENDING_TEXT[this.ending] || ['The patrol is over.']).concat(SILENCE);
        v.reports = docs;
      }
      return v;
    }
  }

  const api = {
    PyRandom, World, Game, setData, navigation, hullReport, contacts, weapons, periscope, visibility, lookout, seabedAt, crushDepth, classifyEnding, availableOrders, orders, fsum, debriefDocuments,
    get DATA() { return DATA; },
  };
  return api;
});
