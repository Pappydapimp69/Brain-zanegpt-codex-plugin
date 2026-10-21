"""Sandbox: seven E31 tuned the spatial find-chance on exact 24-sector
bearings. Seven E25 says a player hears at most 8 directions. Does the tuning
(targets 0.90/0.70/0.50/0.35, skill gap >= 0.20, noise rising under a cap of 4)
survive when the searched sectors are chosen from the HEARD direction, rounded
to 8 points (3 sectors each)? Exact, no RNG.
"""
import math

S = 24


def offset_probs(sigma):
    def cdf(x):
        return 0.5 * (1 + math.erf(x / (sigma * math.sqrt(2))))
    raw = {k: cdf(k + 0.5) - cdf(k - 0.5) for k in range(-12, 12)}
    tot = sum(raw.values())
    return {k: v / tot for k, v in raw.items()}


def sdist(a, b):
    d = abs(a - b) % S
    return min(d, S - d)


def skilled(sigma, h, points):
    step = S // points
    p = 0.0
    for off, w in offset_probs(sigma).items():
        heard = round(off / step) * step  # perceived direction centre
        order = sorted(range(S), key=lambda s: (sdist(s, heard), s))
        if 0 in order[:h]:
            p += w
    return p


def tune(points):
    targets = [0.90, 0.70, 0.50, 0.35]
    sigmas = [1.0 + 0.25 * i for i in range(13)]
    prev, out = 0.0, []
    for t in targets:
        best = None
        for s in sigmas:
            if s < prev:
                continue
            for h in range(1, 13):
                p = skilled(s, h, points)
                gap = p - h / S
                if gap < 0.20:
                    continue
                key = (round(abs(p - t), 2), s, -gap)
                if best is None or key < best[0]:
                    best = (key, s, h, p, gap)
        _, s, h, p, gap = best
        prev = s
        out.append((t, s, h, p, gap))
    return out


def main():
    res = {pts: tune(pts) for pts in (24, 8)}
    for pts, rows in res.items():
        print(f"heard at {pts} points: " + "; ".join(
            f"t{t:.2f}->s{s:.2f} h{h} p{p:.3f} gap{g:.3f}" for t, s, h, p, g in rows))
    w8 = max(abs(p - t) for t, _, _, p, _ in res[8])
    hours24 = sum(h for _, _, h, _, _ in res[24])
    hours8 = sum(h for _, _, h, _, _ in res[8])
    checks = [
        (f"8-direction hearing still hits all targets within 0.05 (worst {w8:.3f})", w8 <= 0.05),
        ("8-direction hearing keeps every skill gap >= 0.20", all(g >= 0.20 for *_, g in res[8])),
        (f"8-direction hearing needs more total search hours (24: {hours24}, 8: {hours8})", hours8 > hours24),
        ("break case: the 24-sector tuning reused unchanged at 8 points misses a target by > 0.05",
         any(abs(skilled(s, h, 8) - t) > 0.05 for t, s, h, _, _ in res[24])),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          f"worst miss at 8 points {w8:.3f}; total hours 24pt {hours24} vs 8pt {hours8}")


if __name__ == "__main__":
    main()
