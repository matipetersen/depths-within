"""The UI principles from DESIGN.md section 12, as tests."""
import re

import pytest

from dread import hud
from dread.endings import classify_ending
from dread.play import Session, available_orders, main, run_auto
from dread.sim import issue_orders, pick_choice
from dread.world import DreadWorld

# Internal identifiers. (Plain words like "attention" do occur in prose, so they are matched as fields.)
HIDDEN = ("moral_debt", "orders_doubt", "war_over", "notice_at", "names_learned", "name_known",
          "peak_dread", "believers", "candor", "mundane_cause", "uncanny_cause", "mundane_when")
HIDDEN_FIELD = re.compile(r"\b(attention|owed|dread|fear|guilt|trust)\s*[:=]\s*[0-9.]+")


def test_the_ledger_is_exact_and_the_people_are_not():
    w = DreadWorld(seed=1)
    w.ship.hull, w.ship.food, w.ship.co2 = 0.62, 0.35, 0.021
    text = "\n".join(hud.ledger(w))
    assert "62%" in text and "35%" in text and "2.1%" in text
    for c in w.crew:
        c.fear, c.trust, c.guilt, c.fatigue = 0.9, 0.1, 0.8, 0.9
    people = "\n".join(hud.crew(w))
    assert not re.search(r"\d", people)                    # not one number about the men


def test_a_broken_man_who_trusts_nobody_says_he_is_fine():
    w = DreadWorld(seed=1)
    c = w.crew[0]
    c.candor, c.fear, c.fatigue, c.guilt, c.trust = 0.9, 0.95, 0.95, 0.9, 0.05
    row = next(r for r in w.report(observer_skill=1.0) if r["name"] == c.name)
    assert row["says"] < 0.3                               # he reports calm...
    assert "talks to himself" in row["symptoms"] or "microsleeps" in row["symptoms"]   # ...and shows it


def test_no_hidden_value_ever_reaches_the_screen():
    for policy in ("mission_first", "crew_first", "paranoid"):
        text = run_auto(policy, 5, every=6).lower()
        for token in HIDDEN:
            assert token not in text, (policy, token)
        assert not HIDDEN_FIELD.search(text), (policy, HIDDEN_FIELD.search(text).group(0))


def test_looking_at_the_screen_changes_nothing():
    """Rendering must not consume the world's dice."""
    def play(render):
        w = DreadWorld(seed=9)
        while not w.finished:
            if w.pending:
                if render:
                    hud.screen(w, w.pending)
                w.choose(pick_choice("crew_first", w.pending, None, w))
                continue
            issue_orders("crew_first", w)
            w.tick()
            if render:
                hud.screen(w, None, available_orders(w))
        return w.log, w.tick_no
    assert play(False) == play(True)


def test_the_clock_goes_wrong_when_the_event_says_so():
    w = DreadWorld(seed=1)
    assert "control-room clock" not in "\n".join(hud.clock_lines(w))
    w.ship.flags.add("clock_drift")
    assert "control-room clock" in "\n".join(hud.clock_lines(w))


def test_on_station_nobody_agrees_what_day_it_is():
    w = DreadWorld(seed=1)
    w._start_mission(4)
    w.vigil_ticks = 30
    assert "Day by the log" not in "\n".join(hud.clock_lines(DreadWorld(seed=1)))
    assert "Day by the log" in "\n".join(hud.clock_lines(w))


def test_every_order_is_priced():
    w = DreadWorld(seed=1)
    for it in available_orders(w):
        assert it.hint or it.label.startswith(("Dive", "Resume")), it.label
    w._start_mission(4)
    labels = [i.label for i in available_orders(w)]
    assert any("Set course for base" in l for l in labels) and any("listen for the world" in l for l in labels)


def test_a_decision_stops_the_clock_until_it_is_answered():
    s = Session(seed=1)
    s.w.engine.fire(s.w.engine.events["clock_slow"], s.w)
    t = s.w.tick_no
    out = s.handle("")                                     # enter does not advance a pending decision
    assert s.w.tick_no == t and "A decision is waiting" in out
    s.handle("1")
    assert s.w.pending is None
    s.handle("")
    assert s.w.tick_no == t + 1


def test_orders_that_name_a_man_ask_which():
    s = Session(seed=1)
    n = next(i for i, it in enumerate(available_orders(s.w), 1) if it.label.startswith("Confine"))
    assert "Which man?" in s.handle(str(n))
    out = s.handle("1")
    assert s.w.crew[0].isolated and "confined" in hud.crew(s.w)[1]


def test_wait_stops_when_something_happens():
    s = Session(seed=2)
    s.handle("w")
    assert s.w.tick_no <= 12
    for _ in range(40):
        if s.over:
            break
        if s.w.pending:
            s.handle("1")
        else:
            s.handle("w")
    assert s.w.tick_no > 12


def test_unknown_input_is_not_an_error():
    s = Session(seed=1)
    assert "don't understand" in s.handle("xyzzy")
    assert "no order 99" in s.handle("99")


def test_the_last_screen_sets_two_accounts_side_by_side_and_ends_in_silence():
    out = run_auto("crew_first", 3, every=1000)
    tail = out[out.index("END:"):]
    assert "REPORT OF PROCEEDINGS" in tail and "CAPTAIN'S LOG" in tail and " | " in tail
    assert "stopped listening" in tail
    assert "Nobody has been asked to reconcile them" in tail


def test_interactive_loop_reads_commands_and_quits(monkeypatch, capsys):
    inputs = iter(["h", "", "q"])
    monkeypatch.setattr("builtins.input", lambda *_: next(inputs))
    main(["--seed", "1"])
    out = capsys.readouterr().out
    assert "wait one hour" in out and "LEDGER" in out


def test_auto_mode_runs_a_whole_patrol(capsys):
    main(["--auto", "mission_first", "--seed", "2", "--every", "500"])
    assert "END:" in capsys.readouterr().out
