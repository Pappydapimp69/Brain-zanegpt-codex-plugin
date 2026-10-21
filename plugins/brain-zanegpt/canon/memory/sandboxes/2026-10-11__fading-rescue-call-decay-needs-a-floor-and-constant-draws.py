"""Sandbox (composed): the fading night call (seven E22's fix) meets
loot-pity E1 (uniform multiplicative decay converges: unfloored -> zero) and
waiting-city E17 / constant roll count (a forced branch that skips a draw
desyncs everything after it).

Claim under test: a call that fades by a multiplier per night missing will
(a) become effectively silent unless floored, turning the SPATIAL rescue window
into a hidden TIME window, and (b) if coded the obvious way, consume a
different number of rng draws per night depending on who is missing/found.

Deterministic: exact expected values plus a scripted counting RNG. No timing.
"""

C0, DECAY, FLOOR, SILENT = 0.9, 0.6, 0.25, 0.05


def call_p(n, floored):
    p = C0 * DECAY ** n
    return max(p, FLOOR) if floored else p


def p_heard_by(nights, floored):
    # probability at least one call heard over nights n..n+1 (2-night window)
    out = []
    for n in range(nights):
        a, b = call_p(n, floored), call_p(n + 1, floored)
        out.append(1 - (1 - a) * (1 - b))
    return out


class CountingRng:
    def __init__(self):
        self.n = 0
        self.x = 12345

    def random(self):
        self.n += 1
        self.x = (1103515245 * self.x + 12345) % 2 ** 31
        return self.x / 2 ** 31


def night_naive(rng, missing, found):
    # obvious code: only roll what is "needed"
    if not missing or found:
        return
    rng.random()          # drift
    rng.random()          # does the call happen
    rng.random()          # bearing noise


def night_constant(rng, missing, found):
    d, c, b = rng.random(), rng.random(), rng.random()   # always three
    if not missing or found:
        return
    _ = (d, c, b)


def draws(fn, missing, found):
    r = CountingRng()
    fn(r, missing, found)
    return r.n


def main():
    nights = 10
    unf = [call_p(n, False) for n in range(nights)]
    flo = [call_p(n, True) for n in range(nights)]
    print("night  call_p unfloored  floored")
    for n in range(nights):
        print(f"  {n}      {unf[n]:.4f}        {flo[n]:.4f}")
    first_silent = next((n for n, p in enumerate(unf) if p < SILENT), None)
    heard_unf = p_heard_by(nights, False)
    heard_flo = p_heard_by(nights, True)
    print(f"first night unfloored call < {SILENT}: {first_silent}")
    print(f"P(heard over 2 nights) night 6: unfloored {heard_unf[6]:.3f} floored {heard_flo[6]:.3f}")
    cases = [(False, False), (True, False), (True, True)]
    naive = [draws(night_naive, m, f) for m, f in cases]
    const = [draws(night_constant, m, f) for m, f in cases]
    print(f"draws per night (none missing / missing / found): naive {naive} constant {const}")
    checks = [
        (f"unfloored call is silent (<{SILENT}) by night 6 (got {first_silent})",
         first_silent is not None and first_silent <= 6),
        ("floored call never drops below the floor", min(flo) >= FLOOR),
        (f"floored 2-night hear chance stays >= 0.40 forever (night 6: {heard_flo[6]:.3f})",
         min(heard_flo) >= 0.40),
        ("naive night step varies its draw count across the 3 cases", len(set(naive)) > 1),
        ("constant night step draws the same count in every case", len(set(const)) == 1),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"unfloored silent at night {first_silent}; floored night-6 hear {heard_flo[6]:.3f}; "
          f"naive draws {naive} vs constant {const}")


if __name__ == "__main__":
    main()
