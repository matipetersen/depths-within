from dread.advice import advice
from dread.world import DreadWorld


def test_a_fresh_patrol_always_says_what_to_do():
    w = DreadWorld(seed=3)
    tips = advice(w)
    assert 1 <= len(tips) <= 4
    assert all(t["text"] for t in tips)


def test_low_batteries_are_flagged():
    w = DreadWorld(seed=3)
    w.ship.surfaced = False
    w.ship.battery = 0.2
    assert any("batteries" in t["text"].lower() for t in advice(w))


def test_lost_position_asks_for_a_fix():
    w = DreadWorld(seed=3)
    w.ship.dr_error = 6.0
    assert any(t["order"] == "take_fix" for t in advice(w))


def test_advice_is_capped_at_four_and_never_names_hidden_values():
    w = DreadWorld(seed=3)
    s = w.ship
    s.surfaced, s.battery, s.dr_error, s.hull, s.co2, s.food = False, 0.1, 9.0, 0.3, 0.05, 0.1
    tips = advice(w)
    assert len(tips) <= 4
    for t in tips:
        assert "attention" not in t["text"].lower() and "moral_debt" not in t["text"]
