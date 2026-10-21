"""Endings, epilogues and the two reports (DESIGN.md section 8).

The game ends without a fight. What decides the ending is the state the patrol
left behind (moral debt, trust, what was named, whether orders are on record),
read once, at the end. The last screen sets two documents side by side: the
official report, where everything has an explanation, and the log, where
nothing does. No arbiter is offered.
"""
from typing import Dict, List

from .missions import provenance_line

ENDING_TEXT: Dict[str, List[str]] = {
    "lost_with_all_hands": ["The pressure hull gives. It is quick, and no one is left to be surprised."],
    "derelict": ["She is found drifting, with every hatch dogged from the inside.",
                 "The log is kept up to the last page. The last pages are in a hand that is not the captain's."],
    "deposed": ["You are relieved of command in the control room, politely, by men you trained.",
                "They bring the boat home themselves. It is not recorded who gave the order."],
    "turned_back": ["You break off and turn for home. The patrol is entered as abandoned."],
    "the_price": ["The sea is flat to the horizon. The radio gives a single tone, then an order to return to base.",
                  "The boat goes home with fewer men than it left with. Everyone agrees on the number, and nobody on the names."],
    "home_unaccounted": ["The pier is there. The count on the gangway does not match the roll.",
                         "The harbour master says the boat is expected. He does not say by whom."],
    "forgotten_post": ["You come home to a peace that began a year ago. No one ever cancelled your orders;",
                       "there was no one left to cancel them. The station is a footnote in a closed file."],
    "the_lamp": ["You come home with every order carried out. The quay is full of fishing boats with their lamps lit in broad daylight.",
                 "Nobody looks at you. At night a lamp burns somewhere in the hull of your own boat, and the lookouts agree there is no lamp."],
    "stained_victory": ["You sailed home with every order carried out. The boat will never again be quiet at night."],
    "court_martial": ["There is an inquiry. The order you refused is on file, in a hand that the clerk cannot name."],
    "returned_under_a_cloud": ["You come home. The staff will have questions about the log, and some of the answers are in it."],
    "returned": ["You come home. There is nothing in the log that can be used against you."],
    "hollow_victory": ["The missions are done. There are too few left aboard to sail her out again."],
    "mission_failed": ["The patrol is entered as unsuccessful. The boat and the men are returned to the pool."],
}

# the ending text always closes the same way: the instruments stop
SILENCE = ["", "The hydrophones go quiet. Not the quiet of an empty sea; the quiet of something that has stopped listening."]


def classify_ending(w, initial_crew: int) -> str:
    s = w.ship
    survivors = len(w.active_crew())
    if s.hull <= 0 or survivors == 0:
        return "derelict" if w.vigil_ticks > 0 else "lost_with_all_hands"
    if "deposed" in s.flags:
        return "deposed"
    if "aborted" in s.flags:
        return "turned_back"
    # The endgame verdicts outrank the rest: they read the whole patrol.
    if "offering_made" in s.flags:
        return "the_price"
    if "home_unaccounted" in s.flags:
        return "home_unaccounted"
    if "peace_known" in s.flags and "left_station" in s.flags:
        return "forgotten_post"
    done = sum(1 for r in w.results if r["outcome"] in ("success", "altered"))
    if "fishermen_sunk" in s.flags:
        return "the_lamp"                    # twelve men who could not have hurt anyone
    if "civilian_sunk" in s.flags:
        return "stained_victory"             # the crew knows, whatever HQ's ledger says
    # Disobedience only counts if the orders are on record. Sometimes there is no
    # record at all (m4_unrecorded): nobody can court-martial you for an order
    # that, as far as anyone can prove, was never given.
    on_record = "orders_unrecorded" not in s.flags
    if "orders_defied" in s.flags and on_record:
        return "court_martial"
    if done >= 3:
        if s.cohesion < 0.3 or survivors < initial_crew * 0.6:
            return "hollow_victory"
        if "orders_bent" in s.flags and on_record:
            return "returned_under_a_cloud"    # HQ will have questions about the log
        return "returned"
    return "mission_failed"


def epilogue(ending: str) -> List[str]:
    return list(ENDING_TEXT.get(ending, ["The patrol is over."])) + SILENCE


def debrief_documents(w) -> Dict[str, List[str]]:
    """Two parallel reports of the same patrol, row for row: the official one and the log."""
    official = ["REPORT OF PROCEEDINGS"]
    log = ["CAPTAIN'S LOG"]
    by_id = {m.id: m for m in w.missions}
    for r in w.results:
        m = by_id[r["mission"]]
        official.append(f"{m.title}: {r['outcome']}. Orders: {m.mundane_origin}")
        log.append(f"{m.title}: {r['outcome']}. Orders: {m.uncanny_origin}")
    for f in w.fired:
        ev = w.engine.events[f.id]
        if ev.get("beat") or ev.get("mission"):
            official.append(f"Day {f.tick // 24 + 1}: {ev['mundane_cause']}")
            log.append(f"Day {f.tick // 24 + 1}: {ev['uncanny_cause']}")
    return {"official": official, "log": log}
