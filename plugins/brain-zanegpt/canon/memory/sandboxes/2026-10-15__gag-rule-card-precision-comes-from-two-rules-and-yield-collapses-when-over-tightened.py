"""Sandbox: does a Chuck-Jones-style rule card turn a premise into a gag machine?

Candidate gags are the full cross product of beat attributes. An independent
audience model (benign-violation: a violation and a benign reading at once)
scores each beat funny or not. We then measure, for the rule card and for
ablations of it: yield (surviving beats), distinct (tool, location) setups,
and precision (share of survivors the audience model calls funny).
Deterministic, stdlib only.
"""
from itertools import product

SOURCES = ["tool_backfire", "ineptitude", "gravity", "outside_force", "target_strikes"]
SELF = {"tool_backfire", "ineptitude", "gravity"}
TOOLS = ["rocket_skates", "anvil", "catapult", "dynamite", "magnet", "giant_spring", "bird_seed_trap", "painted_tunnel"]
PLACES = ["cliff_edge", "desert_road", "canyon_floor", "rope_bridge"]
OUTCOMES = ["humiliated", "maimed", "wins_prize", "quits"]
DIALOGUE = [False, True]
SEVERITY = {"humiliated": 1, "maimed": 3, "wins_prize": 0, "quits": 0}


def funny(beat, want=True):
    """Benign-violation audience model (independent of the card's wording)."""
    src, tool, place, outcome, talk = beat
    # violation: the lead's attempt at the want visibly fails
    violation = want and outcome in ("humiliated", "maimed")
    sev = SEVERITY[outcome]
    # benign: low stakes, or high stakes seen at distance (a long-shot fall)
    benign = sev <= 1 or (outcome == "maimed" and src == "gravity")
    return violation and benign


RULES = {
    "R1_who_can_hurt": lambda b: b[0] in SELF,
    "R2_never_quits": lambda b: b[3] != "quits",
    "R3_never_wins": lambda b: b[3] != "wins_prize",
    "R4_no_dialogue": lambda b: not b[4],
    "R5_humiliated_not_harmed": lambda b: b[3] != "maimed",
}


def run(rules, want=True, sources=SOURCES, tools=TOOLS, places=PLACES):
    beats = list(product(sources, tools, places, OUTCOMES, DIALOGUE))
    kept = [b for b in beats if all(RULES[r](b) for r in rules)]
    good = sum(funny(b, want) for b in kept)
    setups = len({(b[1], b[2]) for b in kept if funny(b, want)})
    prec = good / len(kept) if kept else 0.0
    return len(beats), len(kept), good, prec, setups


ALL = list(RULES)
NEED = 12  # assumed gags per short, an unverified working figure
checks = []

total, k, g, p, s = run([])
print(f"no card: candidates={total} funny={g} precision={p:.3f}")
base_p = p
_, k_full, g_full, p_full, s_full = run(ALL)
print(f"full card: yield={k_full} funny={g_full} precision={p_full:.3f} distinct_setups={s_full}")
checks.append(("full card precision 1.0", p_full == 1.0))
checks.append(("full card yield >= NEED", s_full >= NEED))

print("ablation (drop one rule from the full card):")
for r in ALL:
    rest = [x for x in ALL if x != r]
    _, k2, g2, p2, s2 = run(rest)
    print(f"  without {r:26s} yield={k2:4d} funny={g2:4d} precision={p2:.3f}")

print("single rule on its own:")
single = {}
for r in ALL:
    _, k2, g2, p2, s2 = run([r])
    single[r] = p2
    print(f"  only {r:26s} yield={k2:4d} precision={p2:.3f} (base {base_p:.3f})")

# Does R1 (who can hurt whom) add precision on top of R3+R5? And without R5?
_, _, _, p35, _ = run(["R3_never_wins", "R5_humiliated_not_harmed"])
_, _, _, p135, _ = run(["R1_who_can_hurt", "R3_never_wins", "R5_humiliated_not_harmed"])
_, _, _, p3, _ = run(["R3_never_wins", "R2_never_quits"])
_, _, _, p13, _ = run(["R1_who_can_hurt", "R3_never_wins", "R2_never_quits"])
print(f"R3+R5 precision={p35:.3f}; +R1 -> {p135:.3f}")
print(f"R2+R3 precision={p3:.3f}; +R1 (no R5) -> {p13:.3f}")
checks.append(("R1 adds 0 precision once R5 present", abs(p135 - p35) < 1e-12))
checks.append(("R1 adds precision when R5 absent", p13 > p3))
_, _, _, p_no4, _ = run([x for x in ALL if x != "R4_no_dialogue"])
checks.append(("R4 no-dialogue adds 0 precision", abs(p_no4 - p_full) < 1e-12))

# BREAK 1: the card without a want for the lead
_, kw, gw, pw, sw = run(ALL, want=False)
print(f"BREAK want absent: yield={kw} funny={gw} precision={pw:.3f}")
checks.append(("no want -> 0 funny despite full yield", gw == 0 and kw == k_full))

# BREAK 2: over-tightened card (push until the machine stops)
print("over-tightening (full card plus narrower worlds):")
ladder = [
    ("full", SOURCES, TOOLS, PLACES),
    ("gravity-only", ["gravity"], TOOLS, PLACES),
    ("gravity, 3 tools", ["gravity"], TOOLS[:3], PLACES),
    ("gravity, 3 tools, 2 places", ["gravity"], TOOLS[:3], PLACES[:2]),
    ("gravity, 1 tool, 1 place", ["gravity"], TOOLS[:1], PLACES[:1]),
]
first_fail = None
for name, srcs, tl, pl in ladder:
    _, kk, gg, pp, ss = run(ALL, sources=srcs, tools=tl, places=pl)
    ok = ss >= NEED
    print(f"  {name:28s} yield={kk:3d} distinct_setups={ss:3d} precision={pp:.3f} enough={ok}")
    if not ok and first_fail is None:
        first_fail = name
checks.append(("over-tightening eventually starves the short", first_fail is not None))

for name, ok in checks:
    print(f"  check {name}: {ok}")
allok = all(ok for _, ok in checks)
print(f"RESULT: {'PASS' if allok else 'FAIL'} card precision {base_p:.3f}->{p_full:.3f} with {s_full} setups; "
      f"precision comes from R3+R5 (R1 adds 0 once R5 holds, R4 adds 0); no want -> 0/{kw} funny; "
      f"starves (<{NEED} setups) first at '{first_fail}'")
