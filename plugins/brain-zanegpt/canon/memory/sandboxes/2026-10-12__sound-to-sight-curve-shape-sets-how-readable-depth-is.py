"""Loop 1 (owner's 'sound first, then sight as sanity falls' kernel): how should
the share of VISUAL episodes rise as sanity falls, so the player can read how
deep they are from what they experience, without a HUD?
Exact, no RNG. Sanity bands 0..3 (shore, wading, chest-deep, undercurrent),
equal time in each. Mapping v(b) = P(an episode is visual | band b):
  LINEAR   0.0, 0.33, 0.67, 1.0
  STEP     0.0, 0.0, 1.0, 1.0      (hard switch at chest-deep)
  BANDED   0.0, 0.10, 0.50, 0.90   (the owner's shore -> undercurrent shape)
  FLAT     0.45 everywhere          (SEVEN today, roughly: voices 0.20 for the player,
                                     treated here as 0.55 non-voice visual-ish share; control)
Readability = mutual information (bits) between the band and the modality of ONE
episode, and the posterior P(band >= 2 | visual). Also early visual spend =
expected visual episodes in bands 0-1 per 20 episodes (seven E56: visuals wear
out, so early spend is wasted surprise).
"""
import math

MAPS = {"linear": [0.0, 1 / 3, 2 / 3, 1.0], "step": [0.0, 0.0, 1.0, 1.0],
        "banded": [0.0, 0.10, 0.50, 0.90], "flat": [0.45] * 4}


def mi(v):
    pb = 0.25
    pv = sum(pb * x for x in v)
    h = 0.0
    for b in range(4):
        for vis in (1, 0):
            pj = pb * (v[b] if vis else 1 - v[b])
            if pj > 0:
                h += pj * math.log2(pj / (pb * (pv if vis else 1 - pv)))
    return h


def deep_given_visual(v):
    num = sum(v[2:])
    den = sum(v)
    return num / den if den else 0.0


def early_visual(v, n=20):
    return n * 0.25 * (v[0] + v[1])


def main():
    rows = {}
    for k, v in MAPS.items():
        rows[k] = (mi(v), deep_given_visual(v), early_visual(v))
        print(f"{k:7s}: readability {rows[k][0]:.3f} bits; P(deep | visual) {rows[k][1]:.3f}; "
              f"visual episodes spent before chest-deep per 20: {rows[k][2]:.2f}")
    checks = [
        ("flat mix carries no depth information (0 bits)", rows["flat"][0] < 1e-12),
        ("the owner's banded curve beats linear on readability", rows["banded"][0] > rows["linear"][0]),
        ("banded spends at most a third of linear's early visuals", rows["banded"][2] <= rows["linear"][2] / 3),
        ("break case: a hard step is the most readable of all (1 bit)", abs(rows["step"][0] - 1.0) < 1e-9),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; bits linear {rows['linear'][0]:.3f} "
          f"step {rows['step'][0]:.3f} banded {rows['banded'][0]:.3f} flat {rows['flat'][0]:.3f}; early visuals "
          f"linear {rows['linear'][2]:.2f} banded {rows['banded'][2]:.2f}")


if __name__ == "__main__":
    main()
