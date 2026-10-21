"""Loop 1 sandbox: Hellblade-style overlapping voices placed around the head.
How many voices can speak before individual words stop landing, and how much
does spreading them in space (binaural placement) buy?
Exact, no RNG. Each voice talks a fraction d of the time, independently (a
phrase is busy with probability d at any instant). A phrase is INTELLIGIBLE if
no masking voice talks over it. Without spatial separation every other voice
masks. With binaural placement, voices are spread evenly around 360 degrees and
only voices within 60 degrees of each other mask (spatial release from masking,
a simplified stand-in for the real binaural effect).
"""


def masking_neighbours(n, width=60.0):
    if n <= 1:
        return 0
    gap = 360.0 / n
    return sum(1 for k in range(1, n) if min(k * gap, 360 - k * gap) <= width)


def intelligible(n, d, spatial):
    m = masking_neighbours(n) if spatial else n - 1
    return (1 - d) ** m


def main():
    d = 0.4
    rows = {}
    for n in (1, 2, 3, 4, 6, 8, 12):
        rows[n] = (intelligible(n, d, False), intelligible(n, d, True))
        print(f"{n:2d} voices: words land {rows[n][0]:.3f} (one place) vs {rows[n][1]:.3f} (spread around the head)")
    max_mono = max(n for n in rows if rows[n][0] >= 0.5)
    max_spat = max(n for n in rows if rows[n][1] >= 0.5)
    print(f"most voices with >= half of words landing: one place {max_mono}, spread {max_spat}")
    checks = [
        ("with all voices in one place, 4 voices land under 0.25 of words", rows[4][0] < 0.25),
        ("spreading voices around the head lets at least 2x as many voices stay half-intelligible", max_spat >= 2 * max_mono),
        ("break case: with 12 voices even spread placement drops below 0.5", rows[12][1] < 0.5),
    ]
    held = sum(ok for _, ok in checks)
    for n_, ok in checks:
        print(("held   " if ok else "MISSED ") + n_)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; 4 voices one place {rows[4][0]:.3f} "
          f"spread {rows[4][1]:.3f}; 12 spread {rows[12][1]:.3f}; max half-intelligible {max_mono} vs {max_spat}")


if __name__ == "__main__":
    main()
