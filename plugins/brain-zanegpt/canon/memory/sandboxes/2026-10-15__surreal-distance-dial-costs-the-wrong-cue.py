"""Bridge: dark-humor distance dial + escalation-needs-matching-distance E1 + premise-design
(an absurd premise needs a wrong cue AND a safe cue; weirdness alone is not a joke).

E1's model, re-implemented from its stored sandbox: habituation h = exp(-0.2 X),
X += 1/(1 + I/5) per beat, response I/C (C = 10), six beats, benign gate
g = exp(-((d_safe - I/C)/0.25)^2). E1 treats distance only as a SAFE cue.
Premise-design kernel adds: the WRONG cue must also be perceived. Dark-humor kernel says
far-away harm stops mattering ("too far to care"). Assumed form: perceived wrongness
care(d) = 1 - kappa * d, so surreal/AI framing that adds distance also mutes the violation.
Beat = h * (I/C) * care(d) * g.
A non-distance safe cue n (competing norm, e.g. an in-world rule that the victim respawns)
adds to the gate's distance but NOT to care: d_safe = d + n, care uses d only.
PREDICTION (written before running): kappa = 0 reproduces E1 (matched: flat best, 5.11);
flat-at-ceiling under matched distance stops being best at kappa near 0.5; with kappa 0.6
a competing-norm cue n = 0.4 (distance lowered to max(0, s - n)) makes flat best again;
mild beats on full surreal distance (d = 1) score under 0.3 of their matched value."""
import math

C = 10.0
SCHED = {"flat": [10] * 6, "linear": [2 + 8 * k / 5 for k in range(6)],
         "geometric": [2 * 5 ** (k / 5) for k in range(6)], "three": [2, 6, 10, 10, 10, 10],
         "mild": [3, 3.5, 4, 4, 4.5, 5]}


def total(seq, kappa, framing, n=0.0):
    X, tot = 0.0, 0.0
    for I in seq:
        s = I / C
        h = math.exp(-0.2 * X)
        if framing == "matched":
            d = s
        elif framing == "norm":  # competing-norm safe cue carries n, distance covers the rest
            d = max(0.0, s - n)
        elif framing == "surreal":
            d = 1.0
        else:
            d = float(framing)
        g = math.exp(-((d + (n if framing == "norm" else 0.0) - s) / 0.25) ** 2)
        care = max(0.0, 1 - kappa * d)
        tot += h * s * care * g
        X += 1 / (1 + I / 5)
    return tot


ok = True
# S1: kappa = 0 must reproduce E1's matched result exactly
r0 = {k: total(v, 0.0, "matched") for k, v in SCHED.items()}
print("S1 kappa=0 matched:", {k: round(v, 2) for k, v in r0.items()})
ok &= max(r0, key=r0.get) == "flat" and abs(r0["flat"] - 5.11) < 0.005

# S2 (built to BREAK E1's 'matched distance restores going big'): sweep kappa
flip = None
for i in range(0, 11):
    kap = i / 10
    r = {k: total(v, kap, "matched") for k, v in SCHED.items()}
    best = max(r, key=r.get)
    print(f"S2 kappa={kap:.1f} matched: best {best} ({r[best]:.2f}), flat {r['flat']:.2f}, "
          f"three {r['three']:.2f}, mild {r['mild']:.2f}")
    if flip is None and best != "flat":
        flip = (kap, best, r[best], r["flat"])
print(f"   flat stops winning at kappa={flip[0]} (best {flip[1]} {flip[2]:.2f} vs flat {flip[3]:.2f})")

# S3: competing-norm safe cue at kappa 0.6
k3 = 0.6
rm = {k: total(v, k3, "matched") for k, v in SCHED.items()}
rn = {k: total(v, k3, "norm", n=0.4) for k, v in SCHED.items()}
print("S3 kappa=0.6 matched:", {k: round(v, 2) for k, v in rm.items()})
print("   kappa=0.6 norm n=0.4:", {k: round(v, 2) for k, v in rn.items()})
best_n = max(rn, key=rn.get)
ok &= best_n == "flat"

# S3b (added after the first run, which showed flat was still best under matched at kappa 0.6):
# at kappa 0.9, where matched distance already lost to mild, does the norm cue restore going big?
r9m = {k: total(v, 0.9, "matched") for k, v in SCHED.items()}
r9n = {k: total(v, 0.9, "norm", n=0.4) for k, v in SCHED.items()}
print("S3b kappa=0.9 matched:", {k: round(v, 2) for k, v in r9m.items()})
print("    kappa=0.9 norm n=0.4:", {k: round(v, 2) for k, v in r9n.items()})
best9 = max(r9n, key=r9n.get)
ok &= best9 == "flat"

# S4: weirdness alone -- mild beats pushed to full surreal distance (d = 1)
mild_sur = total(SCHED["mild"], k3, "surreal")
mild_mat = total(SCHED["mild"], k3, "matched")
print(f"S4 mild schedule kappa=0.6: surreal d=1 {mild_sur:.3f} vs matched {mild_mat:.3f} "
      f"(ratio {mild_sur / mild_mat:.3f})")
ok &= mild_sur / mild_mat < 0.3
ok &= flip is not None

print(f"RESULT: {'PASS' if ok else 'FAIL'} kappa=0 reproduces E1 (matched flat {r0['flat']:.2f}); "
      f"flat-at-ceiling stops winning under matched distance at kappa={flip[0]} ({flip[1]} {flip[2]:.2f} vs flat "
      f"{flip[3]:.2f}); at kappa 0.6 a competing-norm cue n=0.4 lifts flat {rn['flat']:.2f} vs matched "
      f"{rm['flat']:.2f}; at kappa 0.9 it restores flat as best ({r9n['flat']:.2f} vs matched mild {r9m['mild']:.2f}); mild on full surreal distance keeps {mild_sur / mild_mat:.3f} of matched")
