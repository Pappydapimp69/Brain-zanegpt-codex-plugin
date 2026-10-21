"""Sandbox (follow-up to the blind rebuild of seven E67): how steep must recovery damping be to cancel a sanity competence penalty?
Original rebuild header follows. Claim: making recovery easier at
low sanity does not undo a sanity penalty on competence; collapse stays far
above a perception-only meter.
Exact Markov chain, no RNG. Sanity 0..6 (0 absorbing = collapse), start 6,
20 encounters. Fail -> sanity -1. Success -> +1 with recovery r(s).
PERCEPTION: fail 0.28 flat, recovery 0.25 flat.
PENALTY:    fail 0.28 + 0.06*(6-s), recovery 0.25 flat.
DAMPED x:   fail as PENALTY, recovery 0.25 + x*(6-s) (capped at 1), x in {0.05, 0.10, 0.20}.
PREDICTION (written before running): every damped variant still collapses at
least x2 the perception-only rate; even x = 0.20 stays above x1.5.
"""


def collapse(fail, rec, enc=20, top=6):
    dist = [0.0] * (top + 1)
    dist[top] = 1.0
    for _ in range(enc):
        nd = [0.0] * (top + 1)
        nd[0] += dist[0]
        for s in range(1, top + 1):
            f, r = fail(s), min(rec(s), 1.0)
            nd[s - 1] += dist[s] * f
            nd[min(s + 1, top)] += dist[s] * (1 - f) * r
            nd[s] += dist[s] * (1 - f) * (1 - r)
        dist = nd
    return dist[0]


def needed(pen, base):
    for x in [i / 100 for i in range(0, 101)]:
        if collapse(lambda s, p=pen: 0.28 + p * (6 - s), lambda s, x=x: 0.25 + x * (6 - s)) <= base:
            return x
    return None


def main():
    base = collapse(lambda s: 0.28, lambda s: 0.25)
    rows = {p: needed(p, base) for p in (0.03, 0.06, 0.10)}
    for p, x in rows.items():
        print(f"penalty {p:.2f}/level: recovery must rise {x if x is not None else 'n/a (impossible)'} per level to match perception-only")
    checks = [
        ("a mild penalty (0.03) can be cancelled by damping", rows[0.03] is not None),
        ("cancelling needs damping at least 3x the penalty slope (0.03 and 0.06)",
         all(rows[p] is not None and rows[p] >= 3 * p for p in (0.03, 0.06))),
        ("break case: a 0.10 penalty cannot be cancelled with recovery capped at 1", rows[0.10] is None),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; damping needed "
          + "; ".join(f"pen {p}: {x}" for p, x in rows.items()))


if __name__ == "__main__":
    main()
