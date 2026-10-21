"""Sandbox: is 'the 15 s cut ends on the fixable-fail beat' the same as 'the cut keeps the gap'?

Master 30 s ad as five beats: hook 3, setup 5 (opens the gap: will he make it?),
escalation 12, fail 6, reveal 4 (the fixable-fail payoff). Every 15 s cut-down
keeps each beat trimmed to an integer length 0..full, in order. For every cut:
  content check  (companion lesson): the cut ends on the reveal beat (reveal >= 2 s)
  discourse check (kernel): setup >= 2 s AND reveal >= 2 s AND the gap is held
                  >= HMIN s between the setup's end and the reveal's start
Ending multiplier 1.65 is earned only by the discourse check; crossover against
the 30 s master uses the companion's closed form value = 0.35 e^{-h(L-3)}(1+L/60)M.
Reveal cue timing: anchored to the reveal beat (film E19) vs an absolute cue list
proportionally rescaled from the master (26 s * 15/30 = 13 s).
Deterministic, stdlib only.
"""
from itertools import product
from math import log, exp

BEATS = [("hook", 3), ("setup", 5), ("escalation", 12), ("fail", 6), ("reveal", 4)]
MASTER_REVEAL_T = 26.0
TARGET = 15
MULT = 1.65


def cuts(target=TARGET):
    ranges = [range(0, full + 1) for _, full in BEATS]
    for lens in product(*ranges):
        if sum(lens) == target:
            yield lens


def content_ok(l):
    return l[4] >= 2


def gap_hold(l):
    # seconds between the end of setup and the start of reveal
    return l[2] + l[3]


def discourse_ok(l, hmin):
    return l[1] >= 2 and l[4] >= 2 and gap_hold(l) >= hmin


def h_star(m15, m30=MULT, short=15, long=30):
    # 0.35 e^{-h(S-3)}(1+S/60) m15 = 0.35 e^{-h(L-3)}(1+L/60) m30
    return log(((1 + long / 60) * m30) / ((1 + short / 60) * m15)) / (long - short)


def value(L, h, m):
    return 0.35 * exp(-h * (L - 3)) * (1 + L / 60) * m


all_cuts = list(cuts())
n = len(all_cuts)
content = [c for c in all_cuts if content_ok(c)]
print(f"15 s cut-downs enumerated: {n}; pass content (ends on reveal >= 2 s): {len(content)}")

HMIN = 3
false_pass = [c for c in content if not discourse_ok(c, HMIN)]
no_setup = [c for c in content if c[1] < 2]
short_hold = [c for c in content if c[1] >= 2 and gap_hold(c) < HMIN]
print(f"HMIN={HMIN}: content-pass but gap lost: {len(false_pass)}/{len(content)} "
      f"({len(false_pass)/len(content):.3f}); no setup {len(no_setup)}, hold too short {len(short_hold)}")

print("sensitivity of the false-pass share to the assumed minimum hold:")
shares = {}
for hm in range(0, 9):
    fp = sum(1 for c in content if not discourse_ok(c, hm))
    shares[hm] = fp / len(content)
    print(f"  HMIN={hm}: {fp}/{len(content)} = {shares[hm]:.3f}")

h_kept = h_star(MULT)
h_lost = h_star(1.0)
print(f"crossover h*: gap kept {h_kept:.4f}/s, gap lost {h_lost:.4f}/s")
print("value ratio 15 s cut / 30 s master at decay 1..4%/s, for a content-pass cut that lost the gap:")
ratios = []
for h in (0.01, 0.02, 0.03, 0.04):
    r = value(15, h, 1.0) / value(30, h, MULT)
    ratios.append(r)
    print(f"  h={h:.2f}: {r:.3f}")

# Scenario: same content, reordered discourse (reveal moved before escalation/fail)
canon = (2, 3, 4, 3, 3)
reordered_hold = 0  # reveal now directly follows setup: gap opened and closed at once
print(f"reorder scenario: cut {canon} hold={gap_hold(canon)} discourse_ok={discourse_ok(canon, HMIN)}; "
      f"same beats with reveal moved up: hold={reordered_hold} -> gap kept={reordered_hold >= HMIN}")

# Film E19: reveal cue anchored vs proportionally rescaled absolute cue list
early = late = 0
gap_cuts = [c for c in content if discourse_ok(c, HMIN)]
for c in gap_cuts:
    reveal_start = sum(c[:4])
    scaled = MASTER_REVEAL_T * TARGET / 30.0
    if scaled < reveal_start - 1e-9:
        early += 1  # fires during escalation/fail: spoils the outcome
    elif scaled > reveal_start + 0.5:
        late += 1   # payoff on screen with no caption: dead air
print(f"rescaled cue list over {len(gap_cuts)} gap-keeping cuts: early (spoil) {early}, late >0.5 s {late}; anchored: 0 and 0 by construction")

# Break attempt: a cut where content check FAILS but gap is kept (would the content check be too strict?)
too_strict = [c for c in all_cuts if not content_ok(c) and discourse_ok(c, HMIN)]
print(f"content-fail but discourse-ok cuts: {len(too_strict)}")

checks = [
    ("some content-pass cuts lose the gap", len(false_pass) > 0),
    ("false passes exist even at HMIN=0 (missing setup)", shares[0] > 0),
    ("crossover reproduces companion 0.0122 / 0.0455", round(h_kept, 4) == 0.0122 and round(h_lost, 4) == 0.0455),
    ("a gap-lost cut loses to master at 1-4%/s", all(r < 1 for r in ratios)),
    ("rescaled cue list mistimes some gap-keeping cuts", early + late > 0),
    ("content check never stricter than discourse", len(too_strict) == 0),
]
for name, ok in checks:
    print(f"  check {name}: {ok}")
allok = all(ok for _, ok in checks)
print(f"RESULT: {'PASS' if allok else 'FAIL'} {len(false_pass)}/{len(content)} cut-downs that end on the reveal "
      f"lost the gap at HMIN={HMIN} ({shares[0]:.3f} even at HMIN=0), so their h* is {h_lost:.4f} not {h_kept:.4f}; "
      f"rescaled cue list mistimed {early + late}/{len(gap_cuts)} gap-keeping cuts (early {early}, late {late})")
