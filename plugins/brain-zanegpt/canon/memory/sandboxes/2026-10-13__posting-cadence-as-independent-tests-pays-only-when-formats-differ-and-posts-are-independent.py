"""Posting cadence as repeated tests. Exact expected hits by enumeration (no RNG).
Formats have per-post hit probabilities q_f. Strategies over n posts:
  repeat  = post one format n times, format chosen uniformly (expected over the choice)
  oracle  = post the best format n times (unknowable in advance)
  explore = post each format once, then keep posting the format that hit (first hit in list order; if no hit, the first format)
  corr    = like explore, but posts of the same format are PERFECTLY correlated within the run (one draw per format:
            a 'shared assumption' - same hook, same audience), so repeats add no information
Hit-ratio of the native-vs-polished pair follows the kernel's 'almost double' (0.04 -> 0.08)."""
from itertools import product
def explore(q, n, corr=False):
    k = len(q); total = 0.0
    for outcome in product((0, 1), repeat=k):
        pr = 1.0
        for o, qi in zip(outcome, q): pr *= qi if o else 1 - qi
        hits = sum(outcome)
        chosen = next((i for i, o in enumerate(outcome) if o), 0)
        rest = n - k
        if corr:   # remaining posts replay that format's single draw
            hits += rest * outcome[chosen]
        else:
            hits += rest * q[chosen]
        total += pr * hits
    return total
def repeat(q, n): return n * sum(q) / len(q)
def oracle(q, n): return n * max(q)
from math import comb
def explore_m(q, n, m):
    """m probe posts per format (independent), then the rest on the format with most probe hits (ties -> lowest index)."""
    k = len(q); rest = n - m * k
    if rest < 0: return None
    pmf = [[comb(m, h) * qi ** h * (1 - qi) ** (m - h) for h in range(m + 1)] for qi in q]
    total = 0.0
    for counts in product(range(m + 1), repeat=k):
        pr = 1.0
        for c, pm in zip(counts, pmf): pr *= pm[c]
        best = max(range(k), key=lambda i: (counts[i], -i))
        total += pr * (sum(counts) + rest * q[best])
    return total
scen = {"varied formats (polished .04, native .08, .02, .06, .03)": [0.04, 0.08, 0.02, 0.06, 0.03],
        "equal formats (BREAK: no variety value)": [0.05] * 5,
        "native best, polished worst": [0.02, 0.08, 0.04]}
out = {}
for name, q in scen.items():
    print(name)
    for n in (30, 90, 300):
        row = {m: explore_m(q, n, m) for m in (1, 3, 6)}
        r = repeat(q, n)
        out[(name, n)] = (r, row, explore(q, n, True), oracle(q, n))
        print(f"  n={n:>3}: repeat {r:6.2f} | probes/format 1: {row[1]:6.2f}  3: {row[3]:6.2f}  6: {row[6]:6.2f} | oracle {oracle(q, n):6.2f} | single-draw-per-format (perfectly correlated) {explore(q, n, True):6.2f}")
v = list(scen)[0]; e = list(scen)[1]
a = out[(v, 300)]; b = out[(v, 30)]; c = out[(e, 300)]
ok = a[1][6] > a[0] and b[1][1] < b[0] and c[1][6] <= c[0] + 1e-9 and a[2] > a[1][6]
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" varied n=300 repeat {a[0]:.2f} probes1 {a[1][1]:.2f} probes6 {a[1][6]:.2f} oracle {a[3]:.2f}; n=30 repeat {b[0]:.2f} probes1 {b[1][1]:.2f}; equal n=300 probes6 {c[1][6]:.2f} vs {c[0]:.2f}")
