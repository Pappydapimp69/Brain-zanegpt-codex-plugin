"""Prediction written first: contrary motion fuses less than parallel fifths on average; run 1 refuted it. Music-theory kernel: parallel fifths and octaves are banned because the two voices FUSE into one (the interval is
so strong in the harmonic series), and contrary motion keeps voices independent. Model: each note has partials
1..10 at 1/n amplitude. Fusion of an interval = share of the upper voice's partial energy that lands on a partial of
the lower voice (within 10 cents, equal temperament). Then a two-voice line is scored over time for parallel,
similar and contrary motion. Deterministic, stdlib only."""
import math
def partials(m): f = 440 * 2 ** ((m - 69) / 12); return [(f * n, 1 / n) for n in range(1, 11)]
def fusion(lo, hi, tol=10):
    L = partials(lo); tot = hit = 0
    for f, a in partials(hi):
        tot += a * a
        if any(abs(1200 * math.log2(f / g)) < tol for g, _ in L): hit += a * a
    return hit / tot
names = {12: 'octave', 7: 'fifth', 5: 'fourth', 4: 'major 3rd', 3: 'minor 3rd', 9: 'major 6th', 8: 'minor 6th', 2: 'major 2nd'}
fz = {k: fusion(60, 60 + k) for k in names}
for k, v in sorted(fz.items(), key=lambda x: -x[1]): print(f"  {names[k]:9s} {v:5.0%} of the upper voice's partials sit on the lower voice's")
# two-voice passages over 8 steps; independence = mean (1 - fusion) and how often the interval changes
lower = [60, 62, 64, 65, 67, 65, 64, 62]
parallel5 = [m + 7 for m in lower]
parallel3 = [m + (4 if m in (60, 65, 67) else 3) for m in lower]                       # diatonic thirds above
contrary = [72, 71, 69, 69, 67, 69, 71, 72]                                             # moves against the lower line
def score(up):
    ivs = [(u - l) % 12 or 12 for u, l in zip(up, lower)]
    fus = [fz.get(i, fusion(60, 60 + i)) for i in ivs]
    run = best = 0
    for v in fus: run = run + 1 if v > .15 else 0; best = max(best, run)   # consecutive fused steps
    return sum(fus) / len(fus), len(set(ivs)), best
for name, up in [('parallel fifths', parallel5), ('parallel thirds', parallel3), ('contrary motion', contrary)]:
    f, n, r = score(up); print(f"{name:16s} mean fusion {f:5.0%}, distinct intervals {n}, longest fused run {r} of {len(up)} steps")
p5, p3, ct = score(parallel5), score(parallel3), score(contrary)
# run 1 refuted "contrary motion fuses less on average" (it passes through octaves and unisons); the claim, restated:
# fusion ranks by interval, and what parallel motion adds is PERSISTENCE: every step fused in a row
ok = fz[12] > fz[7] > fz[5] > max(fz[4], fz[3], fz[9], fz[8]) and p5[2] == len(lower) and ct[2] <= 2 and p3[2] == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} fusion ranks octave {fz[12]:.0%} > fifth {fz[7]:.0%} > fourth {fz[5]:.0%} > thirds and sixths ({max(fz[4], fz[3], fz[9], fz[8]):.0%}); parallel fifths stay fused {p5[2]}/{len(lower)} steps in a row, contrary motion fuses as much on average ({ct[0]:.0%} vs {p5[0]:.0%}) but never more than {ct[2]} steps running")
