# Stress test of decaying-safe-cue-flips-go-big-back-to-mild's "restate the cue every second beat":
# its ZaneGPT check asked for a grid over cue strength c0 and distance d plus a refresh that costs something.
# Model as in the lesson (habituation exp(-0.2X), gate exp(-((d-I/C)/0.25)^2), additive cue cover g'=g+c(1-g),
# cue decays by r=0.6 per beat) with refresh every 2 beats resetting c to c0, and each refresh beat
# losing a fraction q of that beat's score (the reminder distracts from the joke).
# PREDICTION (before run): flat-with-refresh beats the best unrefreshed schedule on at least 7 of the 9
# (c0, d) cells at q=0.2; the win vanishes (flat-refresh no longer best) at q about 0.5 for the central cell
# (c0 0.7, d 0.3); the cells that fail at q=0.2 are those with d=0.5 (close to the mild beats, no cue needed).
import math
C = 10.0
SCHED = {"flat": [10]*6, "three": [2,6,10,10,10,10], "mild": [3,3.5,4,4,4.5,5], "linear": [2+8*k/5 for k in range(6)]}
def score(seq, c0, d, r=0.6, refresh=0, q=0.0):
    X = tot = 0.0; age = 0
    for k, I in enumerate(seq):
        c = c0 * r**age
        g = math.exp(-((d - I/C)/0.25)**2); g = g + c*(1-g)
        part = math.exp(-0.2*X) * (I/C) * g
        if refresh and age == 0 and k > 0:
            part *= (1 - q)                      # restating the cue on this beat costs q of it
        tot += part; X += 1/(1+I/5)
        age += 1
        if refresh and age >= refresh: age = 0
    return tot
def best_gap(c0, d, q):
    fr = score(SCHED["flat"], c0, d, refresh=2, q=q)
    other = max(score(s, c0, d) for s in SCHED.values())          # unrefreshed, any schedule
    other_ref = max(score(s, c0, d, refresh=2, q=q) for n, s in SCHED.items() if n != "flat")
    return fr - max(other, other_ref)
wins = {}
for q in (0.0, 0.2, 0.5):
    cells = [(c0, d) for c0 in (0.4, 0.7, 1.0) for d in (0.2, 0.3, 0.5)]
    wins[q] = [(c0, d, round(best_gap(c0, d, q), 2)) for c0, d in cells]
    print("q", q, "gaps", wins[q])
n02 = sum(g > 0 for _, _, g in wins[0.2])
losers02 = [(c0, d) for c0, d, g in wins[0.2] if g <= 0]
central = {q: best_gap(0.7, 0.3, q) for q in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)}
print("central cell gap by q:", {q: round(v, 2) for q, v in central.items()})
flip_q = next((q for q, v in central.items() if v <= 0), None)
ok = n02 >= 7 and flip_q is not None and 0.4 <= flip_q <= 0.6 and all(d == 0.5 for _, d in losers02)
print(f"RESULT: {'PASS' if ok else 'FAIL'} refreshed flat wins {n02}/9 cells at q 0.2, losing cells {losers02}; central cell stops winning at q {flip_q}")
