"""Rebuild of seven E35 (waiting for a second consistent night call trades
rescues for safety) with a correlated bearing model instead of independent
per-pair consistency, and real pairs NOT always consistent.
Own fixture: 6 nights, prior 0.20 someone missing, real call 0.85 x 0.65^k
(fade, no floor), false calls 0.12 per night in both worlds, a night out finds
a missing member with 0.85. A real member has a fixed true bearing; each real
call = true + Gaussian noise sigma 25 deg, heard at 8 directions; false calls
uniform. Consistent = same or adjacent heard direction. If a real and a false
call fall on the same night, one of them (fair coin) is heard.
FIRST: go out on every night a call is heard. WAIT: go out on a call night
only if the call is consistent with some earlier heard call; once out, keep
answering every call. Seeded Monte Carlo (400k worlds). Also an
INDEPENDENT-PAIRS variant: same, but each pair's consistency is drawn
independently (real-real 0.927, any pair with a false call 0.375).
PREDICTIONS (written before running):
 P1 WAIT raises rescues per night out at least 1.3x
 P2 WAIT cuts rescue chance by at least 0.20
 P3 WAIT cuts wasted nights (nobody missing) by more than half
 P4 the independent-pairs variant's WAIT rescue chance is within 0.02 of the
    correlated model (independence per pair does not matter)
"""
import random
NIGHTS, PRIOR, F, FIND, SIG = 6, 0.20, 0.12, 0.85, 25.0
def q8(d): return int(((d % 360) + 22.5)//45) % 8
def cons(a, b): return min((a-b) % 8, (b-a) % 8) <= 1
def sim(policy, indep, seed, T=400000):
    rng = random.Random(seed); rescues = nights_out = wasted = missing_n = 0
    for _ in range(T):
        missing = rng.random() < PRIOR; missing_n += missing
        true = rng.uniform(0, 360); found = False; heard = []; committed = False
        for k in range(NIGHTS):
            real = missing and not found and rng.random() < 0.85*0.65**k
            false = rng.random() < F
            if not (real or false): continue
            src = "r" if real and (not false or rng.random() < 0.5) else "f"
            d = q8(true + rng.gauss(0, SIG)) if src == "r" else rng.randrange(8)
            go = policy == "first" or committed
            if not go:
                for (s0, d0) in heard:
                    if indep:
                        p = 0.927 if (s0 == "r" and src == "r") else 0.375
                        if rng.random() < p: go = True; break
                    elif cons(d0, d): go = True; break
            heard.append((src, d))
            if go:
                committed = True; nights_out += 1
                if not missing: wasted += 1
                if missing and not found and rng.random() < FIND: found = True; rescues += 1
        # end world
    return rescues/missing_n, nights_out, rescues, wasted/(T-missing_n)
r = {}
for pol in ("first", "wait"):
    r[pol] = sim(pol, False, 7)
ri = sim("wait", True, 7)
eff = {p: r[p][2]/r[p][1] for p in r}
print(f"FIRST rescue {r['first'][0]:.3f} wasted/empty-world {r['first'][3]:.3f} eff {eff['first']:.3f}")
print(f"WAIT  rescue {r['wait'][0]:.3f} wasted/empty-world {r['wait'][3]:.3f} eff {eff['wait']:.3f}")
print(f"WAIT independent-pairs rescue {ri[0]:.3f}")
p1 = eff['wait']/eff['first'] >= 1.3
p2 = r['first'][0] - r['wait'][0] >= 0.20
p3 = r['wait'][3] < r['first'][3]/2
p4 = abs(ri[0] - r['wait'][0]) <= 0.02
held = p1 + p2 + p3 + p4
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4 predictions held; rescue first {r['first'][0]:.3f} "
      f"wait {r['wait'][0]:.3f}; wasted first {r['first'][3]:.3f} wait {r['wait'][3]:.3f}; eff ratio "
      f"{eff['wait']/eff['first']:.2f}; indep-pairs wait {ri[0]:.3f}; checks {[p1, p2, p3, p4]}")
