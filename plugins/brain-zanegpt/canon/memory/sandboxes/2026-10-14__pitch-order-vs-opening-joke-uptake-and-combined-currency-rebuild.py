"""Rebuild of the pitch opening-joke order claim, own fixture.
Prediction (before first run):
 P1 no joke: uptake change-first > agenda-first > product-first in every cell.
 P2 attentive audience (a0=0.95): an opening joke never lets product-first beat change-first in uptake (0 cases).
 P3 cold audience (a0=0.30) with a strong refill gain (0.5): at least one cell where product-first+joke beats change-first+joke.
 P4 combined currency warmth + W*uptake: with W=0.5 some joke-on-product-first beats no-joke-change-first; with W=8 none does."""
import itertools

ORD = {"change": "CCCAAPPPPP", "agenda": "AACCCPPPPP", "product": "PPPPPCCCAA"}
VAL = {"C": 3.0, "A": 2.0, "P": 1.0}
REF = {"C": 0.15, "A": 0.05, "P": 0.0}
DECAY, Z = 0.85, 20.0

def run(order, a0, joke, gain, warm=1.0, cred_cost=0.10):
    a = min(1.0, a0 + (gain if joke else 0.0))
    absorbed = 0.0
    for ch in ORD[order]:
        absorbed += a * VAL[ch]
        a = min(1.0, a * DECAY + REF[ch])
    cred = 1.0 - (cred_cost if joke else 0.0)
    uptake = min(1.0, absorbed / Z) * cred
    return uptake, (warm if joke else 0.0)

A0 = [0.30, 0.60, 0.95]
GAIN = [0.0, 0.2, 0.5]
COST = [0.0, 0.10, 0.25]
ok = True

# P1
p1 = all(run("change", a, False, 0)[0] > run("agenda", a, False, 0)[0] > run("product", a, False, 0)[0] for a in A0)
print("P1", p1, [round(run(o, 0.6, False, 0)[0], 3) for o in ORD])

# P2 / P3 : reversal = product+joke uptake > change+joke uptake
def rev(a, g, c):
    return run("product", a, True, g, cred_cost=c)[0] > run("change", a, True, g, cred_cost=c)[0]
att = [(g, c) for g in GAIN for c in COST if rev(0.95, g, c)]
cold = [(g, c) for g in GAIN for c in COST if rev(0.30, g, c)]
print("P2 attentive reversals:", len(att), "of", len(GAIN) * len(COST))
print("P3 cold reversals:", len(cold), cold)
# the 'strong refill' requirement: cold + gain 0.5 specifically
p3 = any(rev(0.30, 0.5, c) for c in COST)
# P4
def beats(W, a, g, c):
    jp = run("product", a, True, g, cred_cost=c)
    nc = run("change", a, False, 0)
    return (jp[1] + W * jp[0]) > (nc[1] + W * nc[0])
low = sum(beats(0.5, a, g, c) for a in A0 for g in GAIN for c in COST)
high = sum(beats(8.0, a, g, c) for a in A0 for g in GAIN for c in COST)
print("P4 low-W wins", low, "high-W wins", high, "of", len(A0) * len(GAIN) * len(COST))
ok = p1 and len(att) == 0 and p3 and low > 0 and high == 0
print("RESULT:", "PASS" if ok else "FAIL",
      f"P1={p1} attentive_reversals={len(att)} cold_reversals={len(cold)} lowW_wins={low} highW_wins={high}")
