"""Rebuild of seven E66 (sound-to-sight curve: avoid 50/50 at any stage, it is least readable;
banded 0/0.1/0.5/0.9 reads 0.470 bits vs linear 0.541; move chest-deep to ~0.3 or 0.7).
Own fixture: UNEQUAL time per band (players spend most time shallow: 0.4/0.3/0.2/0.1) as well as
equal, and readability measured two ways: mutual information of one episode, and the accuracy of
guessing the band from a run of 5 episodes (MAP over the band posterior), which E66 named but
did not test.
Predictions written before running:
 P1 moving chest-deep from 0.5 to 0.3 or 0.7 raises one-episode bits under both time splits.
 P2 one of the moved curves beats linear on one-episode bits under equal time (E66's Fix implies it).
 P3 with 5 episodes the banded curve's band-guess accuracy is within 0.05 of linear (sequences rescue it).
"""
from math import comb, log2

CURVES = {"linear": (0, 1/3, 2/3, 1), "banded": (0, 0.1, 0.5, 0.9), "band0.3": (0, 0.1, 0.3, 0.9),
          "band0.7": (0, 0.1, 0.7, 0.9), "step": (0, 0, 1, 1), "flat": (0.45,) * 4}
SPLITS = {"equal": (0.25,) * 4, "shallow-heavy": (0.4, 0.3, 0.2, 0.1)}

def h(x): return 0 if x in (0, 1) else -(x * log2(x) + (1 - x) * log2(1 - x))

def mi(curve, w):
    pv = sum(wi * c for wi, c in zip(w, curve))
    return h(pv) - sum(wi * h(c) for wi, c in zip(w, curve))

def acc(curve, w, n=5):
    tot = 0.0
    for k in range(n + 1):  # k visual episodes out of n
        joint = [wi * comb(n, k) * c ** k * (1 - c) ** (n - k) for wi, c in zip(w, curve)]
        tot += max(joint)
    return tot

res = {}
for s, w in SPLITS.items():
    for c, cv in CURVES.items():
        res[(s, c)] = (mi(cv, w), acc(cv, w))
    print(s + ": " + "  ".join(f"{c} {res[(s,c)][0]:.3f}b/{res[(s,c)][1]:.3f}" for c in CURVES))
p1 = all(res[(s, m)][0] > res[(s, "banded")][0] for s in SPLITS for m in ("band0.3", "band0.7"))
p2 = max(res[("equal", "band0.3")][0], res[("equal", "band0.7")][0]) > res[("equal", "linear")][0]
p3 = abs(res[("equal", "banded")][1] - res[("equal", "linear")][1]) <= 0.05
checks = [("P1 moving off 0.5 raises bits", p1), ("P2 a moved curve beats linear", p2), ("P3 5-episode accuracy within 0.05 of linear", p3)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
e = lambda c: f"{res[('equal', c)][0]:.3f}/{res[('equal', c)][1]:.3f}"
print(f"RESULT: {'PASS' if held == 3 else 'FAIL'} {held}/3; equal-time bits/5-ep accuracy linear {e('linear')} banded {e('banded')} "
      f"band0.3 {e('band0.3')} band0.7 {e('band0.7')} step {e('step')}; shallow-heavy banded {res[('shallow-heavy','banded')][0]:.3f}b")
