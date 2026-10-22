"""The JavaScript engine in web/engine.js must be the Python engine, not an approximation.

Both play the same fuzzed patrols (a fixed integer sequence picks orders and choices, so the
inputs are identical) and must write the same log, reach the same ending, and agree on the
ledger as it goes. The JavaScript side reproduces CPython's random numbers, so equality is
exact, not statistical.
"""
import json
import os
import shutil
import subprocess

import pytest

from dread import orders as O
from dread.endings import classify_ending
from dread.nav import contacts, hull_report, lookout, navigation, periscope, weapons
from dread.play import available_orders
from dread.world import DreadWorld
from dread.state import clamp  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")

SEEDS = list(range(0, 24)) + [101, 777, 2024, 31337]


def fuzz(seed, max_steps=2500):
    w = DreadWorld(seed=seed)
    state = (seed * 2654435761) % 2 ** 32

    def nxt():
        nonlocal state
        state = (state * 1664525 + 1013904223) % 2 ** 32
        return state >> 8

    digest, nav, dmg, cts, eye, steps = [], [], [], [], [], 0
    while not w.finished and steps < max_steps:
        steps += 1
        if w.pending:
            w.choose(w.pending.choices[nxt() % len(w.pending.choices)].key)
            continue
        if nxt() % 3 == 0:
            w.do_act()
        if nxt() % 11 == 0:
            O.load_torpedoes(w, ["steam", "electric", "acoustic"][nxt() % 3])
        if nxt() % 7 == 0:
            O.set_depth(w, ["shallow", "deep", "test"][nxt() % 3])
        if nxt() % 13 == 0:
            O.dive(w) if w.ship.surfaced else O.surface(w)
        if nxt() % 9 == 0:
            if not w.ship.surfaced:
                O.raise_periscope(w)
            O.take_fix(w)                                   # most of the time a captain does carry the mission out
        if nxt() % 5 == 0:
            items = available_orders(w)
            item = items[nxt() % len(items)]
            if item.needs_crew:
                pool = w.active_crew()
                if item.label.startswith("Release"):
                    pool = [c for c in pool if c.isolated]
                if pool:
                    c = pool[nxt() % len(pool)]
                    {"Confine": O.isolate, "Release": O.release, "Order": O.force_compartment}[item.label.split()[0]](w, c.id)
            else:
                item.run()
        if w.pending:
            continue                                       # an order (the radio, the log) can raise a decision of its own
        w.tick()
        if steps % 3 == 0:
            wp, ps = weapons(w), periscope(w, 0)
            eye.append([",".join(wp["tubes"]), wp["stock"], [[x["bearing"], x["range_yd"], x["run_s"], x["gyro"]] for x in wp["solutions"]], ps["mode"], ([ps["ship"]["bearing"], ps["ship"]["range_nm"], ps["ship"]["kind"]] if ps["ship"] else None), ",".join(ps["distortions"]), ",".join(str(x) for x in ps["ghosts"]), len(ps["others"]), ps["visibility"], "|".join(lookout(w))])
            cts.append([[c["bearing"], c["range_nm"]] for c in contacts(w)])
        if steps % 25 == 0:
            live = w.active_crew()
            digest.append([w.tick_no, w.ship.hull, w.ship.food, w.ship.water, w.ship.fuel, w.ship.co2,
                           w.ship.attention, w.ship.cohesion, w.dread(),
                           sum(c.fear for c in live) / len(live) if live else 0])
            n = navigation(w)
            nav.append([n["x"], n["y"], n["heading"], n["speed"], n["depth"], n["range_nm"], w.ship.battery, w.ship.spares, n["err_nm"], len(w.traffic), [[o["kind"], o["flag"], int(round(o["x"] * 10)), int(round(o["y"] * 10))] for o in w.traffic], n["keel"], f'{w.ship.torpedo_type}:{json.dumps(w.ship.types, separators=(",", ":"))}:{w.ship.depth_extra}'])
            dmg.append([h["integrity"] for h in hull_report(w)])
    return {"seed": seed, "log": w.log, "results": w.results, "ending": classify_ending(w, 12),
            "tick": w.tick_no, "steps": steps, "digest": digest, "nav": nav, "dmg": dmg, "cts": cts, "eye": eye}


@pytest.fixture(scope="module")
def js_runs():
    out = subprocess.run(["node", os.path.join(ROOT, "web", "parity.js"), *map(str, SEEDS)],
                         capture_output=True, text=True, check=True, timeout=300)
    return {r["seed"]: r for r in json.loads(out.stdout)}


@pytest.mark.parametrize("seed", SEEDS)
def test_same_patrol_same_log(seed, js_runs):
    py, js = fuzz(seed), js_runs[seed]
    assert py["tick"] == js["tick"], (py["tick"], js["tick"])
    assert py["ending"] == js["ending"]
    first_diff = next((i for i, (a, b) in enumerate(zip(py["log"], js["log"])) if a != b), None)
    assert first_diff is None, f"logs diverge at line {first_diff}:\n py: {py['log'][first_diff]}\n js: {js['log'][first_diff]}"
    assert len(py["log"]) == len(js["log"])
    assert py["results"] == js["results"]


@pytest.mark.parametrize("seed", SEEDS[:8])
def test_the_ledger_agrees_as_it_goes(seed, js_runs):
    py, js = fuzz(seed), js_runs[seed]
    assert len(py["digest"]) == len(js["digest"])
    for row_py, row_js in zip(py["digest"], js["digest"]):
        for a, b in zip(row_py, row_js):
            assert a == pytest.approx(b, abs=1e-9)


def test_the_fuzz_reaches_every_part_of_the_story(js_runs):
    """A parity test that never leaves the first mission proves little."""
    endings = {r["ending"] for r in js_runs.values()}
    text = "\n".join(l for r in js_runs.values() for l in r["log"])
    for marker in ("Mission 'Sink the battleship'", "ORDERS: Hold the sector", "Setting course for base",
                   "> ", "Mission 'Return by the northern lane'"):
        assert marker in text, marker
    assert len(endings) >= 4, endings


def test_the_random_numbers_are_cpythons(tmp_path):
    """The foundation: same seed, same stream, for every method the engine uses."""
    import random
    script = tmp_path / "r.js"
    script.write_text(
        "const D=require(%r);const out=[];"
        "for (const seed of [0,1,7,12345,2**32+5,4294967296*3+11]) {"
        "const r=new D.PyRandom(seed);"
        "out.push([r.random(),r.random(),r.choice([10,20,30,40,50]),r.randint(50,150),r.uniform(0.25,0.85),"
        "r.choices1(['a','b','c'],[1.0,2.0,3.0]),r.random()]);}"
        "console.log(JSON.stringify(out));" % os.path.join(ROOT, "web", "engine.js"))
    got = json.loads(subprocess.run(["node", str(script)], capture_output=True, text=True, check=True).stdout)
    for seed, row in zip([0, 1, 7, 12345, 2 ** 32 + 5, 4294967296 * 3 + 11], got):
        r = random.Random(seed)
        want = [r.random(), r.random(), r.choice([10, 20, 30, 40, 50]), r.randint(50, 150),
                r.uniform(0.25, 0.85), r.choices(["a", "b", "c"], weights=[1.0, 2.0, 3.0], k=1)[0], r.random()]
        assert row == want, (seed, row, want)


def test_compensated_float_sum_matches_python():
    script = (
        "const D=require(%r);"
        "const xs=[0.1,0.2,0.3,0.1,0.7,1e-17,0.123456789,0.987654321,0.5,0.25,3.3,0.0001,0.9999,0.05,0.07];"
        "console.log(JSON.stringify([D.fsum(xs),D.fsum(xs.slice(0,5)),D.fsum([0.1]),D.fsum([])]));"
        % os.path.join(ROOT, "web", "engine.js"))
    got = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    xs = [0.1, 0.2, 0.3, 0.1, 0.7, 1e-17, 0.123456789, 0.987654321, 0.5, 0.25, 3.3, 0.0001, 0.9999, 0.05, 0.07]
    assert got == [sum(xs), sum(xs[:5]), sum([0.1]), sum([])]


@pytest.mark.parametrize("seed", SEEDS)
def test_the_instruments_and_the_hull_agree(seed, js_runs):
    py, js = fuzz(seed), js_runs[seed]
    assert len(py["nav"]) == len(js["nav"]) and len(py["dmg"]) == len(js["dmg"])
    for a, b in zip(py["nav"], js["nav"]):
        assert all(abs(x - y) <= 0.11 for x, y in zip(a[:2] + a[3:5], b[:2] + b[3:5])), (a, b)
        assert abs(a[2] - b[2]) % 360 in (0, 1, 359) and abs(a[5] - b[5]) <= 1, (a, b)
        assert abs(a[6] - b[6]) < 1e-9 and abs(a[7] - b[7]) < 1e-9, (a, b)
        assert abs(a[8] - b[8]) <= 0.11 and a[9] == b[9], (a, b)
        assert (a[11] is None) == (b[11] is None) and (a[11] is None or abs(a[11] - b[11]) <= 1) and a[12] == b[12], (a, b)
        assert len(a[10]) == len(b[10]) and all(x[:2] == y[:2] and abs(x[2] - y[2]) <= 1 and abs(x[3] - y[3]) <= 1 for x, y in zip(a[10], b[10])), (a, b)
    for a, b in zip(py["dmg"], js["dmg"]):
        assert all(abs(x - y) < 1e-9 for x, y in zip(a, b)), (a, b)


@pytest.mark.parametrize("seed", SEEDS)
def test_the_scope_agrees(seed, js_runs):
    py, js = fuzz(seed), js_runs[seed]
    assert all(len(a) == len(b) and all(abs(x[0] - y[0]) % 360 in (0, 1, 359) and abs(x[1] - y[1]) <= 0.21 for x, y in zip(a, b))
               for a, b in zip(py["cts"], js["cts"]))


@pytest.mark.parametrize("seed", SEEDS)
def test_the_torpedo_room_and_the_periscope_agree(seed, js_runs):
    py, js = fuzz(seed), js_runs[seed]
    assert len(py["eye"]) == len(js["eye"])
    for a, b in zip(py["eye"], js["eye"]):
        assert a[0] == b[0] and a[1] == b[1] and a[3] == b[3] and a[5] == b[5] and a[6] == b[6] and a[7] == b[7] and a[8] == b[8] and a[9] == b[9], (a, b)
        assert len(a[2]) == len(b[2])
        for x, y in zip(a[2], b[2]):
            assert abs(x[0] - y[0]) % 360 in (0, 1, 359) and abs(x[1] - y[1]) <= 260 and abs(x[2] - y[2]) <= 15, (x, y)   # a 0.1 nm rounding step
        assert (a[4] is None) == (b[4] is None)
        if a[4]:
            assert abs(a[4][0] - b[4][0]) <= 1 and abs(a[4][1] - b[4][1]) <= 0.11 and a[4][2] == b[4][2]
