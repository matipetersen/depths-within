"""The captain's bridge inside the real game window (headless: a tcod Console, no SDL context)."""
import random
import re

import pytest

tcod = pytest.importorskip("tcod")
from tcod.event import KeySym as K  # noqa: E402

from dread.sim import issue_orders, pick_choice  # noqa: E402
from engine.game import Game  # noqa: E402
from ui.panels.panel_manager import PanelManager  # noqa: E402

HIDDEN = ("moral_debt", "orders_doubt", "war_over", "notice_at", "names_learned", "name_known",
          "peak_dread", "believers", "candor", "mundane_cause", "uncanny_cause", "mundane_when", "stage:")
HIDDEN_FIELD = re.compile(r"\b(attention|owed|dread|fear|guilt|trust)\s*[:=]\s*[0-9.]+")


@pytest.fixture
def game():
    random.seed(7)
    return Game()


def shot(game, pm=None):
    pm = pm or PanelManager()
    console = tcod.console.Console(160, 60, order="F")
    pm.render(console, game)
    return "\n".join("".join(map(chr, console.ch[:, y])).rstrip() for y in range(60))


def press(game, *keys):
    consumed = []
    for k in keys:
        consumed.append(game.dread_ui.handle_key(game, k))
    return consumed


def test_the_game_starts_with_the_story_and_a_ui(game):
    assert game.dread_ui is not None
    w = game.horror_manager.dread.world
    assert w.run.mission.id == "m1_battleship" and game.target_depth == 60
    assert any("ORDERS: Sink the battleship" in e["text"] for e in game.logger.entries)


def test_the_map_screen_no_longer_shows_the_horror_stage(game):
    text = shot(game)
    assert "Stage:" not in text and "Day 1" in text and "TAB: Captain's bridge" in text


def test_tab_opens_the_bridge_and_it_shows_the_ledger_not_the_numbers(game):
    assert press(game, K.TAB) == [True] and game.dread_ui.open
    text = shot(game)
    for part in ("LEDGER (exact)", "THE MEN", "SONAR:", "ORDERS", "Silence the sonar"):
        assert part in text
    assert press(game, K.ESCAPE) == [True] and not game.dread_ui.open


def test_orders_are_typed_as_a_number_and_enter(game):
    w = game.horror_manager.dread.world
    press(game, K.TAB)
    assert w.ship.sonar_on and w.working is None
    press(game, K.N1, K.RETURN)                  # order 1 is always the mission's next step
    assert w.working is not None and w.working.id == "search"
    assert game.dread_ui.session(game).notice
    press(game, K.N2, K.RETURN)                  # order 2: silence the sonar
    assert not w.ship.sonar_on


def test_enter_and_space_wait_an_hour_through_the_games_own_clock(game):
    press(game, K.TAB)
    t = game.turn
    press(game, K.RETURN)
    assert game.turn == t + 1 and game.horror_manager.dread.world.tick_no == 1
    press(game, K.SPACE)
    assert game.turn == t + 2


def test_w_waits_for_news_and_stops_at_a_decision(game):
    game.wait_for_news()
    assert 1 <= game.turn <= 12
    for _ in range(40):
        if game.decision_manager.pending_decision:
            break
        game.wait_for_news()
    assert game.decision_manager.pending_decision is not None
    n = game.turn
    game.wait_for_news()
    assert game.turn == n                        # nothing moves while a decision is open


def test_a_decision_is_answerable_in_the_graphical_mode_and_stops_the_clock(game):
    w = game.horror_manager.dread.world
    w.engine.fire(w.engine.events["clock_slow"], w)
    game._tick() if False else None
    game.decision_manager.pending_decision = game.horror_manager.dread.pending_decision()
    text = shot(game)
    assert "CAPTAIN: CLOCK SLOW" in text and "answer with the number" in text
    t = game.turn
    assert press(game, K.SPACE, K.UP, K.N9) == [True, True, True]      # nothing else counts
    assert game.turn == t and game.decision_manager.pending_decision is not None
    assert press(game, K.N1) == [True]
    assert game.decision_manager.pending_decision is None and w.pending is None


def test_you_can_still_quit_with_a_decision_open(game):
    w = game.horror_manager.dread.world
    w.engine.fire(w.engine.events["clock_slow"], w)
    game.decision_manager.pending_decision = game.horror_manager.dread.pending_decision()
    assert press(game, K.Q) == [False]            # the game's own handler gets it


def test_naming_a_man_asks_which(game):
    press(game, K.TAB)
    s = game.dread_ui.session(game)
    n = next(i for i, it in enumerate(s.orders(), 1) if it.label.startswith("Confine"))
    for ch in str(n):
        press(game, getattr(K, f"N{ch}"))
    press(game, K.RETURN)
    assert "WHICH MAN?" in shot(game)
    press(game, K.N1, K.RETURN)
    assert game.horror_manager.dread.world.crew[0].isolated


def test_surface_and_dive_orders_use_the_games_depth(game):
    press(game, K.TAB)
    s = game.dread_ui.session(game)
    surf = next(it for it in s.orders() if it.label.startswith("Surface"))
    surf.run()
    assert game.target_depth == 0
    labels = [it.label for it in s.orders()]
    assert not any("Silent running" in l or "active ping" in l for l in labels)   # those are X and P


def test_no_hidden_value_reaches_the_window_over_a_whole_patrol(game):
    pm = PanelManager()
    press(game, K.TAB)
    seen = []
    for step in range(400):
        if game.dread_over:
            break
        if game.decision_manager.pending_decision:
            seen.append(shot(game, pm))
            game.answer_decision(1)
            continue
        game.dread_ui.session(game).handle("w")
        if step % 25 == 0:
            seen.append(shot(game, pm))
    seen.append(shot(game, pm))
    text = "\n".join(seen).lower()
    for token in HIDDEN:
        assert token not in text, token
    assert not HIDDEN_FIELD.search(text)
    assert "CAPTAIN:" in "\n".join(seen)


def test_a_whole_patrol_ends_in_the_epilogue_and_the_game_stops(game):
    pm = PanelManager()
    for _ in range(3000):
        if game.dread_over:
            break
        pend = game.decision_manager.pending_decision
        if pend:
            w = game.horror_manager.dread.world
            keys = [c.key for c in w.pending.choices]
            pick = keys.index(pick_choice("crew_first", w.pending, None, w)) + 1
            game.answer_decision(pick)
        else:
            w = game.horror_manager.dread.world
            issue_orders("crew_first", w)
            game._tick()
    assert game.dread_over and game.dread_ending
    text = shot(game, pm)
    assert "END:" in text and "REPORT OF PROCEEDINGS" in text
    t = game.turn
    game._tick()
    assert game.turn == t                         # the boat does not move after the end
    assert press(game, K.SPACE, K.N1, K.TAB) == [True, True, True]
    assert press(game, K.Q) == [False]
    game.dread_ui.scroll = 0
    press(game, K.PAGEDOWN)
    assert game.dread_ui.scroll > 0


def test_without_the_story_the_horror_model_still_runs(monkeypatch):
    monkeypatch.setenv("DREAD_MISSIONS", "0")
    random.seed(3)
    g = Game()
    assert g.horror_manager.dread.world.run is None
    for _ in range(30):
        g._tick()
        if g.decision_manager.pending_decision:
            g.answer_decision(1)
    assert not g.dread_over


def _key(sym):
    from tcod.event import KeyDown, Modifier, Scancode
    return KeyDown(scancode=Scancode.UNKNOWN, sym=sym, mod=Modifier.NONE)


def test_the_real_run_loop_routes_keys_to_the_bridge_and_the_modal(monkeypatch):
    """Drive Game.run() itself with real tcod key events and a fake window."""
    import contextlib

    random.seed(11)
    g = Game()
    script = iter([
        [_key(K.TAB)],                    # open the bridge
        [_key(K.N1), _key(K.RETURN)],     # order 1: the mission's next step
        [_key(K.N2), _key(K.RETURN)],     # order 2: silence the sonar
        [_key(K.SPACE)],                  # wait an hour (through the bridge)
        [_key(K.ESCAPE)],                 # back to the map
        [_key(K.W)],                      # wait for news on the map
        [_key(K.Q)],                      # leave
    ])
    frames = []

    class FakeContext:
        def present(self, console):
            frames.append("\n".join("".join(map(chr, console.ch[:, y])).rstrip() for y in range(console.height)))

    @contextlib.contextmanager
    def fake_terminal(*a, **k):
        yield FakeContext()

    monkeypatch.setattr(tcod.context, "new_terminal", fake_terminal)
    monkeypatch.setattr(tcod.event, "wait", lambda *a, **k: next(script))
    monkeypatch.setenv("TW_SW", "160")
    monkeypatch.setenv("TW_SH", "60")
    g.run()
    w = g.horror_manager.dread.world
    assert not w.ship.sonar_on                                  # the orders went through the real loop
    assert w.run.working is not None or w.run.acts_done >= 1    # ...including the mission's step
    assert g.turn >= 2 and w.tick_no >= 2                       # waiting used the game's clock
    assert any("LEDGER (exact)" in f for f in frames)           # the bridge was on screen at some frame
    assert "Stage:" not in "\n".join(frames)
    assert frames[-1].count("LEDGER (exact)") == 0              # ...and gone after ESC
