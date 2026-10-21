"""Sandbox: where does the best equal-factor step count for a 1000x dilution switch from
n-1 to n as the pipette small-volume constant a grows, and does 'one more step per
doubling of a' (the fix text of dilution-best-step-count-grows-with-pipette-constant)
hold?
Prediction (written before first run): switch points near 1->2 ~0.0145, 2->3 ~0.3,
3->4 ~0.7, 4->5 ~1.3, 5->6 ~1.8 uL, so consecutive ratios fall from ~20 to ~1.4 and
'one step per doubling' is true only for the late steps. Assumption: same worst-case
model (floor 0.5 pct, a/volume, diluent scaled by its fraction, 1000 uL final).
BREAK scenarios: the whole sweep at 4 resolutions plus the first-vs-second rule."""
def err(a, n):
    f = 1000 ** (1.0 / n)
    v = 1000.0 / f
    d = 1000.0 - v
    per = max(0.005, a / v) + max(0.005, a / d) * d / 1000.0
    return 100 * n * per

def best(a):
    return min(range(1, 9), key=lambda n: (round(err(a, n), 12), n))

GRID = [i / 1000.0 for i in range(1, 20001)]   # a = 0.001 .. 20 uL
bests = [best(a) for a in GRID]
first = {}
for a, b in zip(GRID, bests):
    first.setdefault(b, a)
for n in sorted(first):
    print(f"best step count {n} first appears at a={first[n]:.3f} uL")
peak = max(bests)
a_peak_last = max(a for a, b in zip(GRID, bests) if b == peak)
final = bests[-1]
drops = [(a, b) for a, b, c in zip(GRID, bests, bests[1:]) if c < b]
print(f"peak best step count {peak} (last at a={a_peak_last:.3f}); at a=20 it is {final}")
print("first decrease:", drops[0] if drops else None)
monotone = not drops
print("monotone non-decreasing in a:", monotone)
ok = monotone and abs(first[2] - 0.0145) < 0.002
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" best n is not monotone in a: peak {peak} until a={a_peak_last:.2f}, then {final} at a=20; first decrease at a={drops[0][0] if drops else None}")
