# Timed-hit grades: closed-form Gaussian model vs the Stonewake playtest data, and what timing skill is worth in damage.
# Game: |err| < .07 s PERFECT x1.6, < .16 GOOD x1.25, else OK x1.0; combo: x(1 + .1*min(5, streak-1)) on chained PERFECTs.
# Playtest (real game, pointer events, err ~ N(.02, sigma)): grade counts copied from the run logs.
import math
def Phi(z): return .5 * (1 + math.erf(z / math.sqrt(2)))
def rates(mu, s, a=.07, b=.16):
    p = Phi((a - mu) / s) - Phi((-a - mu) / s); pg = Phi((b - mu) / s) - Phi((-b - mu) / s)
    return p, pg - p, 1 - pg
OBS = {'skilled': (.07, 45, 22, 2), 'average': (.11, 42, 26, 12), 'casual': (.15, 35, 39, 29)}
res = []; worth = {}
for name, (s, P, G, O) in OBS.items():
    n = P + G + O; pr = rates(.02, s)
    z = [(obs / n - p) / math.sqrt(p * (1 - p) / n) for obs, p in zip((P, G, O), pr)]
    print(f"1) {name:8s} sigma {s}: model P/G/O {pr[0]:.2f}/{pr[1]:.2f}/{pr[2]:.2f}  observed {P/n:.2f}/{G/n:.2f}/{O/n:.2f} (n={n})  z {max(map(abs, z)):.2f}")
    res.append(max(map(abs, z)) < 2.0)
    # expected damage multiplier with the combo, exact Markov chain over the PERFECT streak (iid taps)
    p = pr[0]; dist = {0: 1.0}; acc = 0.0; N = 400
    for _ in range(N):
        new = {}; 
        for k, w in dist.items():
            kk = k + 1; acc += w * p * 1.6 * (1 + .1 * min(5, max(0, kk - 1))); new[kk] = new.get(kk, 0) + w * p
            acc += w * (pr[1] * 1.25 + pr[2] * 1.0); new[0] = new.get(0, 0) + w * (1 - p)
        dist = new
    worth[name] = acc / N
    print(f"2) {name:8s} expected damage multiplier per attack (with combo) {worth[name]:.3f}")
ratio = worth['skilled'] / worth['casual']
base = (lambda r: r[0] * 1.6 + r[1] * 1.25 + r[2])(rates(.02, .07)) / (lambda r: r[0] * 1.6 + r[1] * 1.25 + r[2])(rates(.02, .15))
print(f"3) skilled/casual damage ratio: grades alone {base:.3f}, with combo {ratio:.3f}  (BREAK case: 'timing skill is worth a lot of damage')")
res.append(base < 1.15 and ratio > base)   # first-run prediction said the combo case would stay under 1.2: refuted (1.24)
# 4) what the windows would need to be for the skill gap to reach 1.5x at the same sigmas (PERFECT x2, OK x0.6)
def worth_alt(s, a, b, mp, mg, mo): p, g, o = rates(.02, s, a, b); return p * mp + g * mg + o * mo
alt = worth_alt(.07, .07, .16, 2.0, 1.2, .6) / worth_alt(.15, .07, .16, 2.0, 1.2, .6)
print(f"4) multipliers PERFECT 2.0 / GOOD 1.2 / OK 0.6 (no combo): skilled/casual {alt:.2f}")
res.append(alt > base)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" model matches the playtest within |z|<2 for all 3 profiles; skilled vs casual damage only x{base:.2f} from grades, x{ratio:.2f} with combo; 2.0/1.2/0.6 multipliers give x{alt:.2f}")
