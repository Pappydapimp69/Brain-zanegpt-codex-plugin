"""Sandbox: should a missing person's find-chance be a dice roll or emerge from a
hidden position plus a noisy call bearing?

Model (toy, assumed constants, structure only):
- An area is a ring of SECTORS sectors. The missing person wandered off from
  camp (sector 0) and keeps drifting: each night out adds a random-walk step.
- At night they call. The player hears a BEARING with Gaussian noise whose
  sigma grows with depth (hallucination zone) -- the call names nobody.
- A search spends HOURS hours; each hour covers one sector.
- Policies: SKILLED searches the sectors nearest the heard bearing;
  NAIVE searches random sectors.
- DICE model: p = base * nights_decay * depth_decay * same_night_bonus,
  rolled independently -- the policy cannot change it by construction.

Metric: skill gap = P(find | skilled) - P(find | naive).
Deterministic: fixed seeds, stdlib only.
"""
import math
import random

SECTORS = 24
HOURS = 4
TRIALS = 20000


def wrap(s):
    return s % SECTORS


def sector_dist(a, b):
    d = abs(a - b) % SECTORS
    return min(d, SECTORS - d)


def spatial_trial(rng, nights_out, depth, policy):
    # night 0 = same-night search: they are still near where they wandered off
    pos = wrap(round(rng.gauss(0, 2.0)))
    for _ in range(nights_out):
        pos = wrap(pos + round(rng.gauss(0, 3.0)))
    sigma = 1.0 + 3.0 * depth           # depth 0..3 -> sigma 1..10 sectors
    heard = pos + rng.gauss(0, sigma)
    if policy == "skilled":
        order = sorted(range(SECTORS), key=lambda s: (sector_dist(s, round(heard)), s))
        searched = set(order[:HOURS])
    else:
        searched = set(rng.sample(range(SECTORS), HOURS))
    return pos in searched


def dice_p(nights_out, depth):
    p = 0.85 * (0.6 ** nights_out) * (0.8 ** depth)
    return min(p, 1.0)


def dice_trial(rng, nights_out, depth, policy):
    return rng.random() < dice_p(nights_out, depth)   # policy ignored


def rate(fn, nights_out, depth, policy, seed):
    rng = random.Random(seed)
    return sum(fn(rng, nights_out, depth, policy) for _ in range(TRIALS)) / TRIALS


def main():
    print("nights depth | spatial skilled naive gap | dice skilled naive gap")
    table = {}
    for depth in range(4):
        for n in range(4):
            ss = rate(spatial_trial, n, depth, "skilled", 1000 + 10 * depth + n)
            sn = rate(spatial_trial, n, depth, "naive", 2000 + 10 * depth + n)
            ds = rate(dice_trial, n, depth, "skilled", 3000 + 10 * depth + n)
            dn = rate(dice_trial, n, depth, "naive", 3000 + 10 * depth + n)
            table[(n, depth)] = (ss, sn, ds, dn)
            print(f"  {n}     {depth}   |   {ss:.3f}  {sn:.3f} {ss - sn:+.3f} |"
                  f"  {ds:.3f}  {dn:.3f} {ds - dn:+.3f}")

    checks = []
    # P1 dice gap exactly zero (same seed, policy ignored)
    checks.append(("dice skill gap is 0 everywhere",
                   all(abs(v[2] - v[3]) < 1e-12 for v in table.values())))
    # P2 spatial gap >= 0.30 at nights 0, depth 0
    g = table[(0, 0)][0] - table[(0, 0)][1]
    checks.append((f"spatial skill gap at n0 d0 >= 0.30 (got {g:.3f})", g >= 0.30))
    # P3 skilled find rate decreases with nights out at shallow depth
    sk = [table[(n, 0)][0] for n in range(4)]
    checks.append(("skilled find rate falls with nights out at d0 "
                   + "/".join(f"{x:.2f}" for x in sk),
                   all(a > b for a, b in zip(sk, sk[1:]))))
    # P4 (built to BREAK the claim) deepest call noise -> gap < 0.10, i.e. coin-flip
    g3 = table[(0, 3)][0] - table[(0, 3)][1]
    checks.append((f"deep noise collapses skill gap below 0.10 at n0 d3 (got {g3:.3f})",
                   g3 < 0.10))
    # P5 same-night skilled shallow search >= 0.75
    checks.append((f"same-night shallow skilled >= 0.75 (got {table[(0, 0)][0]:.3f})",
                   table[(0, 0)][0] >= 0.75))
    held = sum(ok for _, ok in checks)
    for name, ok in checks:
        print(("held   " if ok else "MISSED ") + name)
    verdict = "PASS" if held == len(checks) else "FAIL"
    print(f"RESULT: {verdict} {held}/{len(checks)} predictions held; "
          f"spatial gap n0d0={g:.3f}, n0d3={g3:.3f}; dice gap 0")


if __name__ == "__main__":
    main()
