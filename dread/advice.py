"""What the boat needs, as the captain can see it (DESIGN.md 17.2).

Everything here comes from the exact ledger and from what the men visibly show; no hidden value is used.
Each tip names the order that answers it, so a screen can offer it in one tap.
"""
from typing import Dict, List


def advice(w) -> List[Dict]:
    s, run = w.ship, w.run
    tips: List[Dict] = []
    add = lambda text, order=None: tips.append({"text": text, "order": order})

    a, ok, why = w.act_status()
    from . import nav
    blocked = w.work_blocked if w.working is not None else ("" if ok else why)
    if w.working is None and not nav.at_site(w):
        blocked = ""                                         # the sailing has its own tip, below
    if blocked:
        order = ("take_fix" if "Take a fix" in blocked else "restore_sonar" if "listening" in blocked
                 else "dive" if "surface" in blocked.lower() else "snorkel_on" if "batteries are flat" in blocked.lower() else None)
        add(blocked, order)
    if not s.surfaced and s.battery < 0.35 and not s.snorkel:
        add("The batteries are low. Charge them: the periscope up and the diesels on the snorkel, or surface.",
            "snorkel_on" if s.scope_up else "raise_periscope")
    if s.dr_error >= 3.0 and not any(t["order"] == "take_fix" for t in tips):
        add(f"We are not sure where we are: within {s.dr_error:.0f} nm. Take a fix (periscope, stars or the radio).", "take_fix")
    if s.hull < 0.75 and s.spares > 0.1 and not s.dc_active:
        add("The hull is damaged. Put a damage control party on it.", "damage_control")
    if s.co2 >= 0.02:
        add("The air is going foul. Break out fresh absorbent, or surface.", "scrub_air")
    if min(s.food, s.water) < 0.3:
        add("The stores are running low." + (" Ration them, or think about going home." if w.on_station else ""), "rations" if w.on_station else None)
    rows = w.report()
    worn = sum(1 for r in rows if r["says"] >= 0.45 or {"errors at station", "microsleeps"} & set(r["symptoms"]))
    if worn >= 3 and not s.stand_down:
        add("The men look worn out. Let them sleep, or have them eat together.", "stand_down")
    if any("feverish" in r["symptoms"] for r in rows):
        add("A man is feverish. Hold a sick call.", "sick_call")
    st = nav.site(w)
    if st is not None and w.working is None and not nav.at_site(w) and not s.returning:
        est = nav.estimate(w, (s.x, s.y))
        nm = nav.dist2(st[0], st[1], est[0], est[1]) * nav.NM_PER_UNIT
        if nm / nav.NM_PER_UNIT <= nav.SITE_R:
            add(f"By the reckoning we are at {st[2]}, but we cannot be sure of it. Take a fix.", "take_fix")
        elif s.dest is not None and s.dest[2] == st[2]:
            add(f"Under way for {st[2]}, {nm:.0f} nm. Let the hours pass.", None)
        else:
            add(f"Next step: be at {st[2]} ({nm:.0f} nm). Set course for it.", "course_site")
    elif ok and a is not None and w.working is None:
        add(f"Next step: {a.label}. Pick how to do it.", "act")
    elif w.working is not None and not blocked:
        add(f"Under way: {w.working.label}. Let the hours pass; watch the men.", None)
    elif w.on_station:
        add("Hold position. Nothing is asked of you but to stay; watch the men, the stores and the sea.", None)
    if run is not None and run.acts_done == 0 and run.working is None and "verified" not in run.phase_fired and run.mission.kind != "hold":
        add("New orders, from a source you cannot name. You may ask for confirmation; it costs time, and an answer is not a source.", "verify_orders")
    return tips[:4]
