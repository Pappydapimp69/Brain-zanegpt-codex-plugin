"""Sandbox: must a replacement (doppelganger) be exposed before the real missing
person can be rescued, or should the rescue itself expose it?

Toy model, assumed constants, structure only. One disappearance: the real member
is out on the map, a same-name, same-skill fake sits at the fire.
- PARTY = 4 at the fire (fake among them). Deduction accuracy picking the fake
  out of N candidates: Q_N = 0.45 for 1-of-4, Q_2 = 0.80 for 1-of-2 (a fresh
  duplicate with a shared memory log is easier to compare against).
- Window = 2 nights (this area or next). A night search finds them with S = 0.6.
  A pylon test (expose attempt) costs one day of the window.
- PYLONS = 2 available for this problem.
Rules:
  A expose-first : searching is impossible until the fake is exposed by pylon.
  B rescue-exposes: finding the real one makes the fake vanish for free.
  C two-at-fire  : finding the real one brings a SECOND person with the same
                   name to the fire; the player must light a pylon with the one
                   they doubt (1-of-2 deduction). Wrong pick: nothing happens,
                   pylon spent, may retry with the other if a pylon remains.
Metrics: P(real back at fire, fake gone), mean pylons spent, and deduction
share = of the cases resolved, the fraction where a player deduction decided it.
"""
import random

Q_N, Q_2, S, PYLONS, WINDOW, TRIALS = 0.45, 0.80, 0.6, 2, 2, 40000


def rule_a(rng):
    nights, pylons, cands, deduced = WINDOW, PYLONS, 4, False
    while pylons and nights:
        pylons -= 1
        nights -= 1
        if rng.random() < (Q_N if cands == 4 else 1 / cands + (Q_N - 0.25)):
            deduced = True
            break
        cands -= 1
    if not deduced:
        return False, PYLONS - pylons, False
    for _ in range(nights):
        if rng.random() < S:
            return True, PYLONS - pylons, True
    return False, PYLONS - pylons, True


def rule_b(rng):
    for _ in range(WINDOW):
        if rng.random() < S:
            return True, 0, False      # resolved by the rescue, no deduction
    return False, 0, False


def rule_c(rng):
    for _ in range(WINDOW):
        if rng.random() < S:
            pylons = PYLONS
            pylons -= 1
            if rng.random() < Q_2:
                return True, 1, True
            if pylons:                 # second pylon on the other one: certain
                return True, 2, True
            return False, 1, True
    return False, 0, False


def run(fn, seed):
    rng = random.Random(seed)
    back = spent = ded = resolved = 0
    for _ in range(TRIALS):
        ok, p, d = fn(rng)
        back += ok
        spent += p
        if ok:
            resolved += 1
            ded += d
    return back / TRIALS, spent / TRIALS, (ded / resolved if resolved else 0.0)


def main():
    res = {k: run(f, s) for k, f, s in (("A", rule_a, 11), ("B", rule_b, 12), ("C", rule_c, 13))}
    for k, (b, p, d) in res.items():
        print(f"rule {k}: real back {b:.3f}  pylons spent {p:.3f}  deduction share {d:.3f}")
    checks = [
        ("A has the lowest real-back rate", res["A"][0] < min(res["B"][0], res["C"][0])),
        ("B deduction share < 0.30 (rescue bypasses investigation)", res["B"][2] < 0.30),
        ("C real-back within 0.05 of B", res["B"][0] - res["C"][0] <= 0.05),
        ("C deduction share >= 0.50", res["C"][2] >= 0.50),
        ("C spends < 1.5 pylons on average (break case: pylon drain)", res["C"][1] < 1.5),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          + "; ".join(f"{k} back={v[0]:.3f} pylons={v[1]:.3f} ded={v[2]:.3f}" for k, v in res.items()))


if __name__ == "__main__":
    main()
