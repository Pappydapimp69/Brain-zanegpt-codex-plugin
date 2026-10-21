"""Loop: rebuild the hallucinated-voice budget on PUBLISHED numbers, after the
review of seven E58 (budget was a readout of an assumed masking width, E69).
Inputs (from a research digest this session; review papers checked on PMC):
 - 2 same-sex talkers at equal level, co-located, ~60% correct (Brungart 2001,
   via Bronkhorst 2015 review, PMC4469089). Used as the calibration point.
 - a 4-5 dB worse threshold ~ tripling the number of interfering talkers
   (Bronkhorst 2015) -> ~1.5 dB per doubling of talkers (applied beyond 1).
 - spatial release from masking with speech maskers: ~6-12 dB with 2-3
   maskers, ~3-6 dB with many (Marrone 2008, Glyde 2013 via PMC5023537);
   lost entirely in mono playback.
ASSUMED: psychometric slope 10 percentage points per dB at the midpoint
(logistic), and that a game voice line can be raised above the others by a
'duck' of D dB.
Intelligibility of the line that must land, with N other voices at equal level:
 margin = D + SRM(N, device) - 1.5*log2(N)    (dB, relative to the 2-talker case)
 p = logistic(k*margin + c), with c so that N=1, mono, D=0 gives 0.60.
"""
import math

K = 4 * 0.10      # logistic slope at midpoint = k/4 -> 10 %/dB


def srm(n, device, low=False):
    if device == "mono":
        return 0.0
    if n <= 3:
        return 6.0 if low else 9.0
    return 3.0 if low else 4.5


C = math.log(0.6 / 0.4)   # logit(0.60) at margin 0


def p_land(n, device, duck=0.0, low=False):
    margin = duck + srm(n, device, low) - 1.5 * math.log2(n)
    return 1 / (1 + math.exp(-(K * margin + C)))


def budget(device, thresh, duck=0.0, low=False):
    ok = [n for n in range(1, 13) if p_land(n, device, duck, low) >= thresh]
    return (max(ok) + 1) if ok else 1     # voices total = N others + the target line


def main():
    for dev in ("mono", "headphones"):
        print(f"{dev:10s}: p(line lands) with 1..6 other voices: " +
              ", ".join(f"{p_land(n, dev):.2f}" for n in range(1, 7)))
    b = {(dev, th, d): budget(dev, th, d) for dev in ("mono", "headphones") for th in (0.5, 0.8) for d in (0, 6)}
    for (dev, th, d), v in b.items():
        print(f"  {dev:10s} must-land {th:.0%} duck {d} dB: most voices in the scene {v}")
    low_hp = budget("headphones", 0.8, 0, low=True)
    checks = [
        ("mono, no duck: a line that must land 80% fits no competing voice at all (budget 1)", b[("mono", 0.8, 0)] == 1),
        ("headphones give a bigger 80% budget than mono at the same duck", b[("headphones", 0.8, 0)] > b[("mono", 0.8, 0)]),
        ("a 6 dB duck lets mono carry at least 3 voices at 80%", b[("mono", 0.8, 6)] >= 3),
        ("break case: at the low end of published release (6 / 3 dB) headphones still beat mono at 80%",
         low_hp > b[("mono", 0.8, 0)]),
    ]
    held = sum(ok for _, ok in checks)
    for n, ok in checks:
        print(("held   " if ok else "MISSED ") + n)
    print(f"RESULT: {'PASS' if held == len(checks) else 'FAIL'} {held}/{len(checks)}; 80% budgets mono {b[('mono', 0.8, 0)]} "
          f"headphones {b[('headphones', 0.8, 0)]} (low-release {low_hp}); with 6 dB duck mono {b[('mono', 0.8, 6)]} "
          f"headphones {b[('headphones', 0.8, 6)]}; 50% budgets mono {b[('mono', 0.5, 0)]} headphones {b[('headphones', 0.5, 0)]}")


if __name__ == "__main__":
    main()
