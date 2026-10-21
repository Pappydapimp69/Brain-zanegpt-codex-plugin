# Sandbox: escalation model + distance gate (escalation-needs-matching-distance/E1)
# + absurd-premise wrong-cue/safe-cue checklist. Stdlib only, deterministic.
import math
C = 10.0; BEATS = 6
def scheds():
    return {"flat": [10]*6, "linear": [2,4,6,8,10,10], "geometric": [1,2,4,8,10,10],
            "three": [2,2,2,6,6,10], "mild": [3,3,4,4,5,5]}
def run(sched, d, c=0.0, wrong_on=True):
    """d = psychological distance, c = competing-norm safe cue (0..1).
    wrongness W=I/C. safe = distance gate widened by competing norm c.
    value = habituation * W (violation present) * safe."""
    X = 0.0; total = 0.0
    for I in sched:
        W = I / C
        hab = math.exp(-0.2 * X)
        gate = math.exp(-((max(0.0, W - d - c)) / 0.25) ** 2)   # excess wrongness beyond safe cues
        viol = W if wrong_on else 0.0
        total += hab * viol * gate * 10
        X += 1 / (1 + I / 5)
    return total
S = scheds()
def best(**k):
    r = {n: run(s, **k) for n, s in S.items()}
    b = max(r, key=r.get); return b, r
res = {}
# 1) fixed grounded distance, no safe cue (reproduces E1)
b1, r1 = best(d=0.3); res[1] = (b1, r1)
# 2) same distance + competing-norm safe cue 0.7
b2, r2 = best(d=0.3, c=0.7); res[2] = (b2, r2)
# 3) BREAK: strong safe cue, no violation (wrong cue absent)
b3, r3 = best(d=1.0, c=1.0, wrong_on=False); res[3] = (b3, r3)
# 4) matched distance, violation present (E1 control)
b4, r4 = best(d=1.0); res[4] = (b4, r4)
for k, (b, r) in res.items():
    print(k, b, {n: round(v, 2) for n, v in r.items()})
ok = (b1 == "mild" and r1["flat"] < 0.05
      and b2 == "flat" and r2["flat"] > 4.0
      and max(r3.values()) == 0.0
      and b4 == "flat")
print(f"RESULT: {'PASS' if ok else 'FAIL'} fixed d0.3 best={b1} flat={r1['flat']:.2f} mild={r1['mild']:.2f}; +safe cue 0.7 best={b2} flat={r2['flat']:.2f}; no-violation max={max(r3.values()):.2f}; matched best={b4} flat={r4['flat']:.2f}")
