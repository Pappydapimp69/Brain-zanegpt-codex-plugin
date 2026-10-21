"""Sandbox (train edge): codex-visual-snapshots E1 (update visual snapshots
only after a browser render pass) composed with sandbox-edges E29 (a harness
snapshotting a continuously moving system must capture at event time; sweep
the timing parameter to confirm the lag is structural).
Claim under test: for an ANIMATED generated page, 'after a render pass' is
not enough; the baseline and the check differ by an amount set by capture
timing unless the page's clock is frozen.
Model, exact, no RNG: one animated element, x(t) = (speed * t) mod 600 px.
The baseline is captured at load + d_base ms, the check at load + d_check ms,
where each delay is render time plus an enumerated jitter of 0..4 frames
(16 ms each). The pixel diff is |x_base - x_check| (wrapped). Frozen clock:
t is pinned to 0 for capture.
"""
W, FRAME = 600, 16


def x(speed, t):
    return (speed * t / 1000.0) % W


def diff(speed, db, dc, frozen):
    tb, tc = (0, 0) if frozen else (db, dc)
    d = abs(x(speed, tb) - x(speed, tc))
    return min(d, W - d)


def sweep(speed, frozen, render=120):
    delays = [render + j * FRAME for j in range(5)]
    pairs = [(a, b) for a in delays for b in delays]
    ds = [diff(speed, a, b, frozen) for a, b in pairs]
    flaky = sum(d >= 1.0 for d in ds) / len(ds)
    return flaky, max(ds)


def main():
    rows = {}
    for speed in (30, 60, 120, 240):
        rows[speed] = (sweep(speed, False), sweep(speed, True))
        (fu, mu), (ff, mf) = rows[speed]
        print(f"speed {speed:3d} px/s: unfrozen flaky pairs {fu:.2f}, max diff {mu:.2f}px | frozen flaky {ff:.2f}, max {mf:.2f}px")
    still = sweep(0, False)
    print(f"speed 0 (static page): unfrozen flaky {still[0]:.2f}")
    checks = [
        ("unfrozen: at least 0.75 of capture pairs differ by >= 1px at 120 px/s", rows[120][0][0] >= 0.75),
        ("frozen clock: zero differing pairs at every speed", all(r[1][0] == 0 for r in rows.values())),
        ("the max diff grows with speed (structural, per the timing sweep)",
         all(rows[a][0][1] < rows[b][0][1] for a, b in ((30, 60), (60, 120), (120, 240)))),
        ("break case: a static page needs no frozen clock (0 differing pairs)", still[0] == 0),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; unfrozen flaky@120 "
          f"{rows[120][0][0]:.2f} max {rows[120][0][1]:.2f}px; frozen 0; static 0")


if __name__ == "__main__":
    main()
