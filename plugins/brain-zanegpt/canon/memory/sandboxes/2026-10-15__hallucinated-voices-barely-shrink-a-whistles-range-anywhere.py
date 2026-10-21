"""Train kernel (apply): OUTDOOR-ACOUSTICS/forest-propagation (in woods a linear
excess attenuation, ~23 dB/100 m (Embleton 1963), sets a whistle's range, not
spreading) + seven E88 (maskers add by power: +3 dB per doubling of equal
voices) + seven E73 (a must-land signal needs ~6 dB over the other voices).
Question for SEVEN: as hallucinated voices pile up, how much range does a real
whistle lose - in dense woods vs a clearing?
Exact arithmetic (bisection), no rng. ASSUMED as in the kernel: whistle 100 dB
at 1 m, air absorption 1.3 dB/100 m, night band background 20 dB; each
hallucinated voice adds 20 dB in the whistle's band (equal to the background);
heard at 0 dB SNR, must-land at +6 dB (E73). Voices n = 0, 1, 2, 4, 8.
PREDICTION (written before running): each doubling of voices (+3 dB) costs
the open-ground range about a quarter to a third, but costs the woods (23 dB/
100 m) only ~10 m (under 10%) - so in dense woods hallucinated voices barely
change how far a whistle carries, and in a clearing they halve it by 8 voices;
the +6 dB must-land margin costs the woods ~25 m and the open ground ~half.
Break case: excess attenuation of 4 dB/100 m (the 2016 model figure) - the
woods then behave much more like open ground (>= 20% loss per doubling).
"""
import math, sys
print("python", sys.version.split()[0])
L0, ABS, BG, VOICE = 100.0, 1.3, 20.0, 20.0
def masker(n): return 10 * math.log10(10 ** (BG / 10) + n * 10 ** (VOICE / 10))
def reach(excess, thr):
    lo, hi = 1.0, 100000.0
    for _ in range(200):
        m = (lo + hi) / 2
        lev = L0 - 20 * math.log10(m) - (ABS + excess) * m / 100
        lo, hi = (m, hi) if lev >= thr else (lo, m)
    return lo
R = {}
for nm, ex in (("open", 0.0), ("woods 23", 23.0), ("woods 4", 4.0)):
    R[nm] = [reach(ex, masker(n)) for n in (0, 1, 2, 4, 8)]
    land = reach(ex, masker(0) + 6)
    print(f"{nm:8s}: range by voices 0/1/2/4/8 = " + " / ".join(f"{r:.0f}" for r in R[nm]) + f" m; must-land +6 dB with no voices {land:.0f} m (loses {R[nm][0]-land:.0f} m, {1-land/R[nm][0]:.0%})")
def per_doubling(rs): return [1 - b / a for a, b in zip(rs[1:], rs[2:])]
pd_open, pd_w23, pd_w4 = per_doubling(R["open"]), per_doubling(R["woods 23"]), per_doubling(R["woods 4"])
print("fractional loss per doubling (1->2, 2->4, 4->8): open", [f"{x:.2f}" for x in pd_open], "woods23", [f"{x:.2f}" for x in pd_w23], "woods4", [f"{x:.2f}" for x in pd_w4])
c = [all(0.25 <= x <= 0.34 for x in pd_open), all(x < 0.10 for x in pd_w23),
     R["open"][4] / R["open"][0] <= 0.5, all(x >= 0.20 for x in pd_w4)]
print("checks:", c)
print(f"RESULT: {'PASS' if all(c) else 'FAIL'} {sum(c)}/4; 8 voices shrink range open {R['open'][0]:.0f}->{R['open'][4]:.0f} m, woods23 {R['woods 23'][0]:.0f}->{R['woods 23'][4]:.0f} m, woods4 {R['woods 4'][0]:.0f}->{R['woods 4'][4]:.0f} m; per doubling open {pd_open[0]:.2f}, woods23 {pd_w23[0]:.2f}, woods4 {pd_w4[0]:.2f}")
