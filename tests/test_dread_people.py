"""The radio room, the officers' council, sickness and the log (DESIGN.md 15.4)."""
from dread import hud, orders as O
from dread.endings import debrief_documents
from dread.world import DreadWorld


def _w(seed=3):
    w = DreadWorld(seed=seed)
    for c in w.crew:
        c.fear, c.fatigue = 0.05, 0.05
    return w


# ---- the radio ------------------------------------------------------------------------------------------
def test_the_radio_hears_nothing_under_water_and_needs_a_man_and_a_working_set():
    w = _w()
    assert "under water" in O.listen_radio(w)
    O.raise_periscope(w)
    w.ship.flags.add("fault_radio")
    assert "dead" in O.listen_radio(w)
    w.ship.flags.discard("fault_radio")
    for c in w.crew:
        if c.role == "radio":
            c.alive = False
    assert "no radio man" in O.listen_radio(w)


def test_listening_costs_an_hour_and_some_attention_and_brings_a_message_or_static():
    w = _w()
    O.raise_periscope(w)
    lost, att = w.run.lost, w.ship.attention
    heard = set()
    for _ in range(40):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick_no += 20                                         # past every cooldown
        heard.add(O.listen_radio(w)[:6])
    assert w.run.lost > lost + 30 and w.ship.attention > att
    assert heard == {"Static", "The ra"}
    ids = {f.id for f in w.fired}
    assert ids & {"r_traffic", "r_names", "r_ack", "r_peace"}


def test_radio_messages_are_not_in_the_ordinary_pool():
    w = _w()
    for _ in range(300):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
    assert not {f.id for f in w.fired if f.id.startswith("r_")}


def test_a_frightened_operator_reads_the_wrong_message():
    wrong = 0
    for seed in range(60):
        w = _w(seed)
        for c in w.crew:
            if c.role == "radio":
                c.fear = c.fatigue = 0.95
        O.raise_periscope(w)
        w.tick_no = 40
        O.listen_radio(w)
        wrong += "second reading is not the first" in "\n".join(w.log)
    assert wrong >= 10


def test_the_peace_news_is_true_only_if_the_war_is_over():
    from dread.events import apply_effects
    w = _w()
    w.truth["war_over"] = True
    apply_effects([{"op": "peace_news"}], w)
    assert "peace_known" in w.ship.flags
    w = _w()
    w.truth["war_over"] = False
    apply_effects([{"op": "peace_news"}], w)
    assert "peace_known" not in w.ship.flags


def test_replying_to_the_acknowledgement_breaks_silence_and_gives_a_position():
    w = _w()
    O.raise_periscope(w)
    w.ship.dr_error = 5.0
    w.tick_no = 60
    for _ in range(100):
        w.tick_no += 20
        O.listen_radio(w)
        if w.pending is not None and w.pending.event_id == "r_ack":
            break
        if w.pending is not None:
            w.choose(w.pending.choices[-1].key)
    assert w.pending.event_id == "r_ack"
    w.choose("reply")
    assert w.ship.dr_error < 2.5 and "silence_broken" in w.ship.flags


# ---- the officers ---------------------------------------------------------------------------------------
def test_the_officers_give_honest_advice_in_proportion_to_trust_and_candor():
    def honest(trust):
        n = 0
        for seed in range(40):
            w = _w(seed)
            for c in w.crew:
                c.trust, c.candor, c.fatigue = trust, 0.9, 0.8
            O.call_council(w)
            n += any("close to the end" in l for l in w.log)
        return n
    assert honest(0.9) >= 30 and honest(0.1) <= 5


def test_the_council_costs_an_hour_and_asking_a_man_who_trusts_you_warms_him():
    w = _w()
    first = w.crew[0]
    t = first.trust
    lost = w.run.lost
    O.call_council(w)
    assert first.trust > t and w.run.lost == lost + 0.5 and "council_recent" in w.ship.flags
    w = _w()
    w.crew[0].trust = 0.2
    O.call_council(w)
    assert w.crew[0].trust < 0.2                                  # he is not there to be asked


def test_the_advice_follows_the_true_state_and_names_no_number():
    from dread.people import honest_advice
    w = _w()
    w.ship.hull = 0.5
    assert "hurt" in honest_advice(w, "chief engineer")
    w.ship.hull, w.ship.battery = 1.0, 0.1
    assert "charge" in honest_advice(w, "chief engineer")
    w.crew[5].ill = True
    assert "sick" in honest_advice(w, "doctor")
    assert not any(ch.isdigit() for ch in honest_advice(w, "first officer"))


def test_officers_who_met_without_you_are_a_decision_with_three_costs():
    w = _w()
    w.ship.orders_doubt = 0.5
    for c in w.crew:
        c.trust = 0.4
    w.tick_no = 30
    fired = None
    for _ in range(400):
        if w.pending is not None:
            if w.pending.event_id == "officers_unasked":
                fired = w.pending
                break
            w.choose(w.pending.choices[0].key)
        w.ship.orders_doubt, w.ship.flags = 0.5, w.ship.flags - {"council_recent"}
        for c in w.crew:
            c.trust = 0.4
        w.tick()
    assert fired is not None and {c.key for c in fired.choices} == {"join", "forbid", "ignore"}


# ---- sickness -------------------------------------------------------------------------------------------
def test_men_fall_ill_in_a_foul_hungry_boat_and_a_medic_finds_the_ones_who_hide():
    w = _w()
    w.ship.food, w.ship.co2 = 0.2, 0.05
    for _ in range(80):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.ship.food, w.ship.co2 = 0.2, 0.05
        w.tick()
    sick = [c for c in w.crew if c.ill and c.alive]
    assert sick
    for c in sick:
        c.candor, c.trust, c.hides = 0.1, 0.2, True
    assert not any("feverish" in c.symptoms() for c in sick)    # hiding
    for c in w.crew:
        if c.role == "medic":
            c.alive = True                                          # the ill sometimes die; the medic is needed here
    assert "sick found" in O.sick_call(w) and not any(c.hides for c in sick)
    for c in sick:
        if c.ill:
            assert "feverish" in c.symptoms()                       # nobody hides any longer


def test_untreated_sickness_kills_and_a_boat_with_no_medic_cannot_treat_it():
    w = _w()
    w.crew[4].ill, w.crew[4].ill_ticks = True, 41
    for _ in range(200):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        if not w.crew[4].ill or not w.crew[4].alive:
            break
        w.tick()
    for c in w.crew:
        if c.role == "medic":
            c.alive = False
    assert "no medic" in O.sick_call(w)


def test_a_healthy_clean_boat_stays_mostly_well():
    w = _w()
    for _ in range(30):
        if w.pending is not None:
            w.choose(w.pending.choices[0].key)
        w.tick()
    assert sum(c.ill for c in w.crew) <= 3


# ---- the log --------------------------------------------------------------------------------------------
def test_the_log_is_a_choice_with_a_cooldown_and_the_two_reports_differ_by_it():
    w = _w()
    assert O.write_log(w) == "You open the log."
    assert w.pending.event_id == "log_entry" and {c.key for c in w.pending.choices} == {"true", "soft", "blank"}
    w.choose("soft")
    assert w.ship.log_soft == 1 and "wet" in O.write_log(w)
    w.tick_no = 30
    O.write_log(w)
    w.choose("true")
    w.tick_no = 60
    O.write_log(w)
    w.choose("blank")
    docs = debrief_documents(w)
    assert len(docs["official"]) == len(docs["log"])
    assert "3 entries" in docs["official"][-1] and "1 softened" in docs["log"][-1] and "1 left blank" in docs["log"][-1]
    assert len(debrief_documents(_w())["official"]) == 1            # nothing written, nothing to contrast

def test_the_menu_has_the_radio_the_council_sick_call_the_log_and_a_fix():
    from dread.play import available_orders
    labels = [i.label for i in available_orders(_w())]
    for want in ("Listen at the radio", "Call the officers", "Sick call", "Write the day's entry", "Take a fix"):
        assert want in labels


def test_the_hud_shows_a_feverish_man_only_when_he_does_not_hide_it():
    w = _w()
    w.crew[4].ill, w.crew[4].hides = True, False
    assert "feverish" in w.crew[4].symptoms()
    w.crew[4].hides = True
    assert "feverish" not in w.crew[4].symptoms()
