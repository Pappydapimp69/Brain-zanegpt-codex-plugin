"""Blind rebuild of seven E67 (own fixture). Claim: making recovery easier at
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


def main():
    base = collapse(lambda s: 0.28, lambda s: 0.25)
    pen = collapse(lambda s: 0.28 + 0.06 * (6 - s), lambda s: 0.25)
    rows = {x: collapse(lambda s: 0.28 + 0.06 * (6 - s), lambda s, x=x: 0.25 + x * (6 - s)) for x in (0.05, 0.10, 0.20)}
    print(f"perception-only {base:.4f}; penalty {pen:.4f} (x{pen / base:.2f})")
    for x, v in rows.items():
        print(f"damped recovery +{x:.2f}/level: {v:.4f} (x{v / base:.2f})")
    checks = [
        ("every damped variant still collapses >= x2 perception-only", all(v / base >= 2 for v in rows.values())),
        ("even the strongest damping (+0.20/level) stays above x1.5", rows[0.20] / base > 1.5),
        ("damping does reduce collapse versus the bare penalty", all(v < pen for v in rows.values())),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; base {base:.4f} penalty x{pen / base:.2f}; "
          + "; ".join(f"damped {x} x{v / base:.2f}" for x, v in rows.items()))


if __name__ == "__main__":
    main()
