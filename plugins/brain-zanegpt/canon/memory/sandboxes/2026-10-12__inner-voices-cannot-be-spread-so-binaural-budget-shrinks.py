"""Loop 3 sandbox (hallucination phenomenology x seven E55). E55: hallucinated
voices stay intelligible up to ~2 in one place or ~4 spread around the head
(binaural release from masking). But many voice-hearers report voices located
INSIDE the head or 'thought-like' (no external position). An inner voice has
no azimuth to spread, so it masks and is masked by every other voice.
Exact, no RNG. N voices, each talking a fraction d = 0.4 of the time. A share
p of them are inner. Outer voices are spread evenly around the head and mask
only outer neighbours within 60 degrees (as E55). Inner voices mask everyone
and are masked by everyone. Expected share of words that land, averaged over
voices, for N = 4 and the largest N with >= half of words landing.
Fractional p is handled by enumerating the integer number of inner voices
k = round(p * N).
"""


def outer_mask_count(n_outer, width=60.0):
    if n_outer <= 1:
        return 0
    gap = 360.0 / n_outer
    return sum(1 for k in range(1, n_outer) if min(k * gap, 360 - k * gap) <= width)


def landing(n, k_inner, d=0.4):
    n_out = n - k_inner
    vals = []
    for _ in range(k_inner):
        vals.append((1 - d) ** (n - 1))
    for _ in range(n_out):
        m = outer_mask_count(n_out) + k_inner
        vals.append((1 - d) ** m)
    return sum(vals) / n if n else 1.0


def max_half(p):
    best = 1
    for n in range(1, 13):
        if landing(n, round(p * n)) >= 0.5:
            best = n
    return best


def main():
    rows = {}
    for p in (0.0, 0.25, 0.5, 1.0):
        rows[p] = (landing(4, round(p * 4)), max_half(p))
        print(f"inner share {p:.2f}: 4 voices land {rows[p][0]:.3f}; most voices with >= half landing: {rows[p][1]}")
    checks = [
        ("all-outer reproduces E55 (4 voices land 1.000, budget 4)", rows[0.0] == (1.0, 4)),
        ("half inner voices cut the 4-voice landing below 0.5", rows[0.5][0] < 0.5),
        ("all-inner collapses to E55's one-place budget of 2", rows[1.0][1] == 2),
        ("break case: a quarter inner still keeps the budget at 3 or more", rows[0.25][1] >= 3),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; 4-voice landing by inner share "
          + "/".join(f"{rows[p][0]:.3f}" for p in rows) + "; budget " + "/".join(str(rows[p][1]) for p in rows))


if __name__ == "__main__":
    main()
