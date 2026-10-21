"""Loop: seven E66 found that judging depth from ONE episode's modality is weak
(0.470 bits for the owner's banded curve, a 50/50 stage being the worst). With
sound as a continuous bed and visions as brief events, a player can read depth
from TWO channels over a short window: how thick the bed is, and how many
visions arrive. How much of the 2 bits (4 equally likely bands) does that give?
Exact, no RNG. Bands 0..3.
Bed: thickness level t_b = 0, 1, 2, 3 (silence, presence, murmurs, voices);
  the player perceives it with confusion: correct with prob c, else an adjacent
  level (split equally; edges keep the remainder).
Visions: Poisson count in a 2-minute window with rate per band
  lambda = 0, 0.1, 0.5, 1.5 (rare to frequent; the owner's curve).
MI(band; perceived bed, vision count) computed by summing the joint
distribution (vision counts truncated at 12).
"""
import math

LAM = [0.0, 0.1, 0.5, 1.5]


def pois(k, lam):
    if lam == 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * lam ** k / math.factorial(k)


def bed_perceive(t, c):
    out = {t: c}
    nb = [x for x in (t - 1, t + 1) if 0 <= x <= 3]
    for x in nb:
        out[x] = out.get(x, 0) + (1 - c) / len(nb)
    return out


def mi(use_bed, use_vis, c=0.7):
    joint = {}
    for b in range(4):
        beds = bed_perceive(b, c) if use_bed else {0: 1.0}
        for pb, wb in beds.items():
            for k in range(13 if use_vis else 1):
                wk = pois(k, LAM[b]) if use_vis else 1.0
                p = 0.25 * wb * wk
                if p > 0:
                    joint[(b, pb, k)] = joint.get((b, pb, k), 0) + p
    py = {}
    for (b, pb, k), p in joint.items():
        py[(pb, k)] = py.get((pb, k), 0) + p
    return sum(p * math.log2(p / (0.25 * py[(pb, k)])) for (b, pb, k), p in joint.items())


def main():
    rows = {"visions only": mi(False, True), "bed only (c 0.7)": mi(True, False),
            "bed + visions (c 0.7)": mi(True, True), "bed + visions (c 0.5)": mi(True, True, 0.5)}
    for k, v in rows.items():
        print(f"{k:22s}: {v:.3f} of 2 bits")
    checks = [
        ("bed + visions beats either channel alone", rows["bed + visions (c 0.7)"] > max(rows["visions only"], rows["bed only (c 0.7)"])),
        ("bed + visions gives at least 1.2 bits (vs E66's 0.470 for one episode)", rows["bed + visions (c 0.7)"] >= 1.2),
        ("break case: a muddy bed (c 0.5) still beats one-episode modality (0.470)", rows["bed + visions (c 0.5)"] > 0.470),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; bits visions {rows['visions only']:.3f} "
          f"bed {rows['bed only (c 0.7)']:.3f} both {rows['bed + visions (c 0.7)']:.3f} both-muddy {rows['bed + visions (c 0.5)']:.3f}")


if __name__ == "__main__":
    main()
