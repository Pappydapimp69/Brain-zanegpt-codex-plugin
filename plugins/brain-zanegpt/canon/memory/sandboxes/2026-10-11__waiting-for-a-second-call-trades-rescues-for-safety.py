"""Sandbox: answer the first night call, or wait for a second call from a
consistent direction (seven E23's tell, at 8 heard directions per seven E25)?
Exact enumeration over call patterns, no RNG.
Real world: a member is missing from night 0; calls on night n with
0.9*0.6^n (owner's fade, no floor, seven E27); lost after night 6. Real pairs
are consistent with 1.0 at 8 directions (E25). A night out finds with 0.9.
False world (nobody missing): false calls at 0.106 per night (E23); a pair of
false calls looks consistent 0.375 of the time (E25).
Strategies: FIRST goes out on every call until found; WAIT goes out only on a
call whose previous night also had a consistent call.
Weights: prior M = 0.15 real world vs 0.85 false world per episode.
"""
from itertools import product

M, F, FIND, N = 0.15, 0.106, 0.9, 6
CONS_REAL, CONS_FALSE = 1.0, 0.375


def episode(real, strat):
    rescues = nights_out = 0.0
    for pattern in product((0, 1), repeat=N):
        p = 1.0
        for n, c in enumerate(pattern):
            pc = 0.9 * 0.6 ** n if real else F
            p *= pc if c else 1 - pc
        # consistency of consecutive pairs (independent per pair, simple model)
        pairs = [n for n in range(1, N) if pattern[n] and pattern[n - 1]]
        for mask in product((0, 1), repeat=len(pairs)):
            q = 1.0
            cons = set()
            for pn, m in zip(pairs, mask):
                pr = CONS_REAL if real else CONS_FALSE
                q *= pr if m else 1 - pr
                if m:
                    cons.add(pn)
            if q == 0:
                continue
            w = p * q
            found_p, out = 0.0, 0.0
            alive = 1.0
            for n in range(N):
                go = pattern[n] and (strat == "first" or n in cons)
                if go:
                    out += 1
                    if real:
                        found_p += alive * FIND
                        alive *= 1 - FIND
            rescues += w * found_p
            nights_out += w * out
    return rescues, nights_out


def main():
    res = {}
    for s in ("first", "wait"):
        r_res, r_out = episode(True, s)
        f_res, f_out = episode(False, s)
        rescue = r_res
        wasted = f_out
        eff = (M * r_res) / (M * r_out + (1 - M) * f_out)
        res[s] = (rescue, wasted, eff, r_out)
        print(f"{s:5s}: P(rescue | missing) {rescue:.3f}  wasted nights (nobody missing) {wasted:.3f}  "
              f"rescues per night out {eff:.3f}")
    eff_ratio = res["wait"][2] / res["first"][2]
    loss = 1 - res["wait"][0] / res["first"][0]
    checks = [
        (f"waiting raises rescues per night out >= 1.3x (got {eff_ratio:.2f})", eff_ratio >= 1.3),
        (f"waiting cuts rescue chance by >= 0.20 (got {loss:.3f})", loss >= 0.20),
        ("waiting cuts wasted nights by more than half", res["wait"][1] < res["first"][1] / 2),
        ("break case: first-call rescue chance stays >= 0.85 despite the fade", res["first"][0] >= 0.85),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"rescue first {res['first'][0]:.3f} wait {res['wait'][0]:.3f}; wasted first {res['first'][1]:.3f} "
          f"wait {res['wait'][1]:.3f}; efficiency ratio {eff_ratio:.2f}")


if __name__ == "__main__":
    main()
