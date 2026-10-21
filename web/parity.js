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
  const digest = [], nav = [], dmg = [];
  let steps = 0;
  while (!w.finished && steps < maxSteps) {
    steps += 1;
    if (w.pending) {
      w.choose(w.pending.choices[nxt() % w.pending.choices.length].key);
      continue;
    }
    if (nxt() % 3 === 0) w.do_act();
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
    w.tick();
    if (steps % 25 === 0) {
      const live = w.active_crew();
      digest.push([w.tick_no, w.ship.hull, w.ship.food, w.ship.water, w.ship.fuel, w.ship.co2, w.ship.attention,
        w.ship.cohesion, w.dread(), live.length ? Dread.fsum(live.map((c) => c.fear)) / live.length : 0]);
      const nv = Dread.navigation(w);
      nav.push([nv.x, nv.y, nv.heading, nv.speed, nv.depth, nv.range_nm]);
      dmg.push(Dread.hullReport(w).map((h) => h.integrity));
    }
  }
  return { seed, log: w.log, results: w.results, ending: Dread.classifyEnding(w, 12), tick: w.tick_no, steps, digest, nav, dmg };
}

const seeds = process.argv.slice(2).map(Number);
const out = seeds.map((s) => fuzz(s, 2500));
process.stdout.write(JSON.stringify(out));
