"""Sandbox: live tag-count meter vs written range rule, and where a meter stops helping.
Deterministic, stdlib only. Claims tested:
 - ideas:PROMPT-ENGINEERING/.../budget-meter-beats-a-written-length-rule: live band feedback beats a rule read once
 - ideas:SONGWRITING/suno-prompting/five-to-eight-specific-style-tags...: 5-8 tags good, >10 contradict
 - local-suno/E34: v6 rewrite drops anything the style does not name (inventory audit needed)
"""
LO, HI, FIGHT = 5, 8, 10
# deterministic population: (habitual tag count, meter-obedience radius: how far from band a nudge still moves them)
POP = [(h, r) for h in range(2, 16) for r in (0, 2, 4)]

def in_band(n): return LO <= n <= HI

def written_rule(h, r):
    return h  # rule read once, no feedback: habit decides

def live_meter(h, r):
    # meter shows zone every edit; user within radius r of the band follows the nudge, never blocked
    d = LO - h if h < LO else (h - HI if h > HI else 0)
    if d == 0: return h
    if d <= r: return min(max(h, LO), HI)
    return h  # soft: still allowed to ignore it

def quality(n):  # specificity/contradiction model from the kernel
    if n < LO: return n / LO
    if n <= HI: return 1.0
    if n <= FIGHT + 2: return 1.0 - 0.15 * (n - HI)
    return max(0.0, 1.0 - 0.15 * (n - HI) - 0.2 * (n - FIGHT - 2))

def score(policy):
    ns = [policy(h, r) for h, r in POP]
    return sum(map(in_band, ns)) / len(ns), sum(map(quality, ns)) / len(ns), ns

b1, q1, _ = score(written_rule)
b2, q2, ns2 = score(live_meter)
print(f"S1 written rule : in-band {b1:.3f} mean quality {q1:.3f}")
print(f"S2 live meter   : in-band {b2:.3f} mean quality {q2:.3f}")
# S3: soft not hard - the meter must never block going past the band
blocked = sum(1 for (h, r), n in zip(POP, ns2) if h > FIGHT and r == 0 and n != h)
unblocked_overshoot = sum(1 for (h, r), n in zip(POP, ns2) if h > HI and n > HI)
print(f"S3 soft band    : zero-obedience users unchanged={blocked==0}, still past band={unblocked_overshoot}")

# S4 (BREAK): count meter satisfied, but E34 rewrite drops elements not named in style
BRACKETS = {"cornet", "brushed snare", "organ", "baritone", "southern voice", "deadpan mood"}
def v6_rewrite_keeps(style): return {e for e in BRACKETS if e in style}
style_counted = ["cornet", "brushed snare", "baritone", "indie", "lofi", "warm", "mid-tempo"]  # 7 tags, in band
kept = v6_rewrite_keeps(style_counted)
dropped_counted = len(BRACKETS - kept)
style_inventory = sorted(BRACKETS) + ["lofi"]  # 7 tags, in band, full inventory
dropped_inv = len(BRACKETS - v6_rewrite_keeps(style_inventory))
print(f"S4 break        : 7 tags both, in_band={in_band(7)}; dropped by counted-only={dropped_counted}, by inventory style={dropped_inv}")
# S5: inventory larger than band -> conflict between kernels
big = BRACKETS | {"vinyl", "stutter cuts", "call-and-response", "pitched-down"}
print(f"S5 conflict     : full inventory = {len(big)} tags, in_band={in_band(len(big))}, quality={quality(len(big)):.2f}")
ok = b2 > b1 and q2 > q1 and blocked == 0 and dropped_counted > 0 and dropped_inv == 0 and not in_band(len(big))
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" meter lifts in-band {b1:.2f}->{b2:.2f} and quality {q1:.2f}->{q2:.2f}; but a 7-tag in-band style still lost {dropped_counted} of 6 bracket elements; full inventory needs {len(big)} tags (outside 5-8)")
