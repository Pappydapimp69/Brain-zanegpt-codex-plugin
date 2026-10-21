"""Compose sandbox-comedy-escalation/E1 (escalating absurdity: habituation h = exp(-0.2 X),
X += 1/(1+I/5) per beat, response level-driven I/C, ceiling C 10, start 2, six beats) with
COMEDY-CRAFT/benign-violation (a beat needs a violation AND a reason it is ok at the same
moment) and COMEDY/dark-humor (severe harm needs distance, mild harm needs closeness:
McGraw et al. 2012). Distance gate (assumed, stated): benign factor
g = exp(-((d - I/C) / 0.25)^2), i.e. the right psychological distance d (0 close .. 1
far) grows with severity I/C. Beat response = escalation response x g.
Schedules: flat at the ceiling, linear 2->10, geometric 2->10, rule-of-three (2, 6, 10 then
10, 10, 10). Framing: FIXED distance d = 0.3 (a grounded, realistic sketch), or MATCHED
(d rises with each beat's severity: surreal framing as the dial).
PREDICTION (written before running): without the gate the escalation lesson's result holds
(flat-at-ceiling scores highest); with FIXED d = 0.3 the ranking flips and a schedule that
stays mild wins, with every beat above I = 6 scoring under 0.2 of its ungated value; with
MATCHED distance flat-at-ceiling wins again."""
import math
C = 10.0
SCHED = {"flat": [10] * 6, "linear": [2 + 8 * k / 5 for k in range(6)],
         "geometric": [2 * 5 ** (k / 5) for k in range(6)], "three": [2, 6, 10, 10, 10, 10],
         "mild": [3, 3.5, 4, 4, 4.5, 5]}
def score(seq, framing):
    X, tot, beats = 0.0, 0.0, []
    for I in seq:
        h = math.exp(-0.2 * X); base = h * (I / C)
        if framing == "none": g = 1.0
        else:
            d = 0.3 if framing == "fixed" else I / C
            g = math.exp(-((d - I / C) / 0.25) ** 2)
        beats.append((I, base, base * g)); tot += base * g
        X += 1 / (1 + I / 5)
    return tot, beats
res = {f: {n: score(s, f) for n, s in SCHED.items()} for f in ("none", "fixed", "matched")}
for f in res:
    print(f"{f:7s} " + "  ".join(f"{n}: {v[0]:.2f}" for n, v in res[f].items()))
best = {f: max(res[f], key=lambda n: res[f][n][0]) for f in res}
high_ratio = max(b[2] / b[1] for n in SCHED for b in res["fixed"][n][1] if b[0] > 6)
ok = best["none"] == "flat" and best["fixed"] not in ("flat",) and high_ratio < 0.2 and best["matched"] == "flat"
print(f"RESULT: {'PASS' if ok else 'FAIL'} best schedule: no gate {best['none']}, fixed distance {best['fixed']}, matched distance {best['matched']}; "
      f"fixed-distance beats above I=6 keep at most {high_ratio:.2f} of their ungated value")
