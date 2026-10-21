"""Rebuild of seven E10 (own fixture). Claim: a hidden-state game may lie about
the STATE of a thing the player can see but must not conjure the thing; an
affordance that only appears while deceived is a readout of the deception, and
only a DIFF test (prompt identical before/after the hidden flip) can see it.
Model: fire in {none, dead, live}; deceived in {False, True}.
CONJURE: prompt 'feed fire' iff the PERCEIVED world has a lit fire
  (a deceived mind perceives a lit fire everywhere).
NARROWED: prompt iff a fire the player built exists (dead or live), whatever
  the deception; deception only changes how it LOOKS.
"""
FIRES = ("none", "dead", "live")


def conjure(fire, deceived):
    perceived_lit = fire == "live" or deceived
    return "feed fire" if perceived_lit else ""


def narrowed(fire, deceived):
    return "feed fire" if fire in ("dead", "live") else ""


def snapshot_test(fn):
    # the obvious test: while deceived, a fire is offered
    return all(fn(f, True) == "feed fire" for f in ("dead", "live"))


def diff_test(fn):
    return [f for f in FIRES if fn(f, False) != fn(f, True)]


def leak(fn):
    # states where the prompt alone tells the player they are deceived
    out = 0
    for f in FIRES:
        honest, dec = fn(f, False), fn(f, True)
        out += honest != dec
    return out


def main():
    res = {n: (snapshot_test(fn), diff_test(fn), leak(fn)) for n, fn in
           (("conjure", conjure), ("narrowed", narrowed))}
    for n, (snap, diff, lk) in res.items():
        print(f"{n:9s}: snapshot test {'pass' if snap else 'FAIL'}; diff test differs at {diff}; leaking states {lk}")
    checks = [
        ("snapshot test passes BOTH versions", res["conjure"][0] and res["narrowed"][0]),
        ("diff test fails the conjuring version", bool(res["conjure"][1])),
        ("diff test passes the narrowed version", not res["narrowed"][1]),
        ("conjuring leaks deception through the prompt in >= 1 state", res["conjure"][2] >= 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; conjure differs at "
          f"{res['conjure'][1]}, narrowed differs at {res['narrowed'][1]}")


if __name__ == "__main__":
    main()
