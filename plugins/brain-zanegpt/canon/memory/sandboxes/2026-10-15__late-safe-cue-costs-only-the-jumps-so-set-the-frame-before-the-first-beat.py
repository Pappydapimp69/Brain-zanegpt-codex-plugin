"""Edge sandbox (stdlib, deterministic): what happens when the safe cue arrives LATE.

Composes three things:
 - local__escalation-needs-matching-distance E1: escalation model (habituation exp(-0.2 X),
   X += 1/(1+I/5), response I/C, ceiling 10, six beats) with distance gate
   g = exp(-((d - I/C)/0.25)^2); matched distance (d = I/C) restores go-big (flat 5.11).
 - COMEDY-CRAFT benign-violation kernel: violation and benign reading must be perceived at the
   SAME moment.
 - COMEDY premise-design kernel: weirdness alone (distance / oddness with no violation) is not a joke.
Question: E1's "matched" dial is matched at the same beat. Real framing (surreal cues, the
reveal that the victim is a cartoon) often catches up one or two beats after the violation.
Lag model: d_t = W_{t-L} (framing tracks severity L beats late); before the frame is set,
d = 0.3 (grounded). frame-first: d before beat 1 is already set to beat 1's severity.
Lead model: d_t = W_{t+L}. Two gate shapes for the lead case: symmetric (too much distance
also kills, "too far to care") and one-sided (surplus distance is free).
PREDICTION (written before running): lag 0 reproduces flat 5.11; at lag 1 without frame-first,
flat loses its opening beat (about 20%) but stays best; rule-of-three loses over 30%;
with frame-first, flat is lag-immune (5.11 at lag 1 and 2) because flat has no jumps;
symmetric lead costs rule-of-three as much as lag, one-sided lead costs 0;
a 'weirdness alone' track (violation 0, distance 1) scores 0.00.
"""
import math

C = 10.0
SCHED = {"flat": [10] * 6, "linear": [2 + 8 * k / 5 for k in range(6)],
         "geometric": [2 * 5 ** (k / 5) for k in range(6)], "three": [2, 6, 10, 10, 10, 10],
         "mild": [3, 3.5, 4, 4, 4.5, 5]}
GROUND = 0.3


def gate(d, w, shape):
    if shape == "sym":
        return math.exp(-((d - w) / 0.25) ** 2)
    return math.exp(-(max(0.0, w - d) / 0.25) ** 2)  # one-sided: surplus distance free


def score(seq, lag=0, lead=0, frame_first=False, shape="sym", force_d=None):
    W = [i / C for i in seq]
    X, tot, both = 0.0, 0.0, 0
    for t, I in enumerate(seq):
        h = math.exp(-0.2 * X)
        if force_d is not None:
            d = force_d
        elif lead:
            d = W[min(t + lead, len(W) - 1)]
        elif t - lag >= 0:
            d = W[t - lag]
        else:
            d = W[0] if frame_first else GROUND
        g = gate(d, W[t], shape)
        v = h * W[t] * g
        if W[t] > 0 and g >= 0.5:
            both += 1
        tot += v
        X += 1 / (1 + I / 5)
    return tot, both


rows = {}
conds = [("lag0", dict(lag=0)), ("lag1", dict(lag=1)), ("lag2", dict(lag=2)),
         ("lag1+ff", dict(lag=1, frame_first=True)), ("lag2+ff", dict(lag=2, frame_first=True)),
         ("lead1 sym", dict(lead=1)), ("lead1 1side", dict(lead=1, shape="one"))]
for cname, kw in conds:
    rows[cname] = {n: score(s, **kw) for n, s in SCHED.items()}
    print(f"{cname:11s} " + "  ".join(f"{n}:{v[0]:.2f}({v[1]}/6)" for n, v in rows[cname].items()))

best = {c: max(rows[c], key=lambda n: rows[c][n][0]) for c in rows}
print("best:", best)
loss = lambda c, n: 1 - rows[c][n][0] / rows["lag0"][n][0]
for n in SCHED:
    print(f"{n:9s} loss lag1 {loss('lag1', n):.2f}  lag2 {loss('lag2', n):.2f}  lag1+ff {loss('lag1+ff', n):.2f}  "
          f"lag2+ff {loss('lag2+ff', n):.2f}  lead1sym {loss('lead1 sym', n):.2f}  lead1one {loss('lead1 1side', n):.2f}")

# weirdness alone: no violation, full distance
weird = score([0] * 6, force_d=1.0)[0]
print(f"weirdness alone (violation 0, distance 1): {weird:.2f}")

checks = [
    ("lag0 reproduces E1 flat 5.11", abs(rows["lag0"]["flat"][0] - 5.11) < 0.01 and best["lag0"] == "flat"),
    ("lag1 flat loses opening beat ~20% but stays best", 0.12 < loss("lag1", "flat") < 0.30 and best["lag1"] == "flat"),
    ("lag1 rule-of-three loses >30%", loss("lag1", "three") > 0.30),
    ("frame-first makes flat lag-immune", abs(loss("lag1+ff", "flat")) < 1e-9 and abs(loss("lag2+ff", "flat")) < 1e-9),
    ("symmetric lead hurts three like lag", loss("lead1 sym", "three") > 0.30),
    ("one-sided lead costs nothing", max(abs(loss("lead1 1side", n)) for n in SCHED) < 1e-9),
    ("weirdness alone scores 0", weird == 0.0),
]
for name, ok in checks:
    print(("ok   " if ok else "FAIL ") + name)
p = sum(ok for _, ok in checks)
print(f"RESULT: {'PASS' if p == len(checks) else 'FAIL'} {p}/{len(checks)}; flat lag0 {rows['lag0']['flat'][0]:.2f} "
      f"lag1 {rows['lag1']['flat'][0]:.2f} lag1+ff {rows['lag1+ff']['flat'][0]:.2f}; three lag0 {rows['lag0']['three'][0]:.2f} "
      f"lag1 {rows['lag1']['three'][0]:.2f} (loss {loss('lag1','three'):.2f}); geometric lag1+ff loss {loss('lag1+ff','geometric'):.2f}; "
      f"weird-alone {weird:.2f}")
