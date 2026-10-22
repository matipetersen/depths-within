/* Plays the same fuzzed patrol as tests/test_web_parity.py and prints it as JSON.
 *   node web/parity.js SEED [SEED...]
 * The "captain" is a fixed integer sequence that picks orders and choices without touching the
 * world's dice, so the Python and JavaScript engines face identical inputs. */
'use strict';
const fs = require('fs');
const path = require('path');
const Dread = require('./engine.js');

const data = {
  events: JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'events.json'), 'utf8')).events,
  missions: JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'missions.json'), 'utf8')).missions,
};
Dread.setData(data);

function fuzz(seed, maxSteps) {
  const w = new Dread.World(seed);
  let state = (seed * 2654435761) % 4294967296;
  const nxt = () => { state = (state * 1664525 + 1013904223) % 4294967296; return Math.floor(state / 256); };
  const digest = [], nav = [], dmg = [], cts = [], eye = [];
  let steps = 0;
  while (!w.finished && steps < maxSteps) {
    steps += 1;
    if (w.pending) {
      w.choose(w.pending.choices[nxt() % w.pending.choices.length].key);
      continue;
    }
    if (nxt() % 3 === 0) { const act = w.next_act(); const k = nxt(); w.do_act(act && act.methods.length ? act.methods[k % act.methods.length].id : undefined); }
    if (nxt() % 4 === 0) { const st = Dread.site(w); if (st !== null && !Dread.atSite(w) && !w.ship.returning) Dread.setCourse(w, st[0], st[1], st[2]); }
    if (nxt() % 29 === 0) { const cx = nxt() % 100, cy = nxt() % 70; Dread.setCourse(w, cx, cy, ''); }
    if (nxt() % 17 === 0) Dread.allStop(w);
    if (nxt() % 11 === 0) Dread.orders.load_torpedoes(w, ['steam', 'electric', 'acoustic'][nxt() % 3]);
    if (nxt() % 7 === 0) Dread.orders.set_depth(w, ['shallow', 'deep', 'test'][nxt() % 3]);
    if (nxt() % 13 === 0) { if (w.ship.surfaced) Dread.orders.dive(w); else Dread.orders.surface(w); }
    if (nxt() % 9 === 0) { if (!w.ship.surfaced) Dread.orders.raise_periscope(w); Dread.orders.take_fix(w); }
    if (nxt() % 5 === 0) {
      const items = Dread.availableOrders(w);
      const item = items[nxt() % items.length];
      if (item.needsCrew) {
        let pool = w.active_crew();
        if (item.id === 'release') pool = pool.filter((c) => c.isolated);
        if (pool.length) item.run(pool[nxt() % pool.length].id);
      } else {
        item.run();
      }
    }
    if (w.pending) continue;                       // an order (the radio, the log) can raise a decision of its own
    w.tick();
    if (steps % 3 === 0) { const wp = Dread.weapons(w), ps = Dread.periscope(w, 0); eye.push([wp.tubes.join(','), wp.stock, wp.solutions.map((x) => [x.bearing, x.range_yd, x.run_s, x.gyro]), ps.mode, ps.ship ? [ps.ship.bearing, ps.ship.range_nm, ps.ship.kind] : null, ps.distortions.join(','), ps.ghosts.join(','), ps.others.length, ps.visibility, Dread.lookout(w).join('|'), Dread.advice(w).map((t) => `${t.order || ''}:${t.text}`).join('|')]); }
    if (steps % 3 === 0) cts.push(Dread.contacts(w).map((c) => [c.bearing, c.range_nm]));
    if (steps % 25 === 0) {
      const live = w.active_crew();
      digest.push([w.tick_no, w.ship.hull, w.ship.food, w.ship.water, w.ship.fuel, w.ship.co2, w.ship.attention,
        w.ship.cohesion, w.dread(), live.length ? Dread.fsum(live.map((c) => c.fear)) / live.length : 0]);
      const nv = Dread.navigation(w);
      nav.push([nv.x, nv.y, nv.heading, nv.speed, nv.depth, nv.range_nm, w.ship.battery, w.ship.spares, nv.err_nm, w.traffic.length, w.traffic.map((o) => [o.kind, o.flag, Math.round(o.x * 10), Math.round(o.y * 10)]), nv.keel, w.ship.torpedo_type + ':' + JSON.stringify(w.ship.types) + ':' + w.ship.depth_extra, nv.eta_h, nv.at_site, nv.dest]);
      dmg.push(Dread.hullReport(w).map((h) => h.integrity));
    }
  }
  return { seed, log: w.log, results: w.results, ending: Dread.classifyEnding(w, 12), tick: w.tick_no, steps, digest, nav, dmg, cts, eye };
}

const seeds = process.argv.slice(2).map(Number);
const out = seeds.map((s) => fuzz(s, 2500));
process.stdout.write(JSON.stringify(out));
