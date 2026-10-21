"""Sandbox: can the spatial find model (seven E22) be TUNED to a designer's
target find rate per depth while keeping a visible skill gap, or is it, as the
tension claims, harder to tune than a weighted roll?
Exact, no RNG. Ring of 24 sectors, person at sector 0, heard bearing offset is a
discretised normal with sigma s (via erf). A skilled search covers the H sectors
nearest the heard bearing; naive covers H at random (H/24). Knobs per depth:
sigma in [1, 4] (capped, seven E22) and hours H in [1, 12].
Targets: depth 0..3 -> 0.90, 0.70, 0.50, 0.35. Pick the (sigma, H) closest to the
target with sigma rising with depth, requiring skill gap >= 0.20.
"""
import math

S = 24


def offset_probs(sigma):
    def cdf(x):
        return 0.5 * (1 + math.erf(x / (sigma * math.sqrt(2))))
    raw = {k: cdf(k + 0.5) - cdf(k - 0.5) for k in range(-12, 12)}
    tot = sum(raw.values())
    return {k: v / tot for k, v in raw.items()}


def skilled(sigma, h):
    probs = offset_probs(sigma)
    p = 0.0
    for off, w in probs.items():
        heard = off  # person at 0, heard bearing at off
        order = sorted(range(S), key=lambda s: (min(abs(s - heard) % S, S - abs(s - heard) % S), s))
        if 0 in order[:h]:
            p += w
    return p


def main():
    targets = [0.90, 0.70, 0.50, 0.35]
    sigmas = [1.0 + 0.25 * i for i in range(13)]
    prev_sigma = 0.0
    out = []
    for d, t in enumerate(targets):
        best = None
        for s in sigmas:
            if s < prev_sigma:
                continue
            for h in range(1, 13):
                p = skilled(s, h)
                gap = p - h / S
                if gap < 0.20:
                    continue
                err = abs(p - t)
                # v2: v1 tie-broke toward the NOISIEST sigma, which forced sigma 4 at every
                # depth; prefer the least noise that hits the target, then the larger gap
                key = (round(err, 2), s, -gap)
                if best is None or key < best[0]:
                    best = (key, s, h, p, gap)
        _, s, h, p, gap = best
        prev_sigma = s
        out.append((d, t, s, h, p, gap))
        print(f"depth {d}: target {t:.2f} -> sigma {s:.2f} hours {h} find {p:.3f} gap {gap:.3f}")
    worst = max(abs(p - t) for _, t, _, _, p, _ in out)
    checks = [
        (f"all four targets hit within 0.05 (worst {worst:.3f})", worst <= 0.05),
        ("every depth keeps a skill gap >= 0.20", all(g >= 0.20 for *_, g in out)),
        ("difficulty can rise with depth through noise, not only hours",
         out[-1][2] > out[0][2]),
        ("break case: the deepest target is reached with fewer search hours than depth 0",
         out[-1][3] < out[0][3]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)} predictions held; "
          + "; ".join(f"d{d} s{s:.2f} h{h} p{p:.3f} gap{g:.3f}" for d, t, s, h, p, g in out))


if __name__ == "__main__":
    main()
