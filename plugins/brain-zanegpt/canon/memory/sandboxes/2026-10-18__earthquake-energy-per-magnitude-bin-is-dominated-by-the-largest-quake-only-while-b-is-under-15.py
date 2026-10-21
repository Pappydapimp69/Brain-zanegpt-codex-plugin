# Seed domain SEISMOLOGY. Real source: the USGS magnitude FAQ: each whole magnitude step is 10x the recorded wave
# amplitude and about 31.6x (10^1.5) the energy (Gutenberg-Richter energy relation log10 E = 1.5 M + 4.8, E in joules),
# and the Gutenberg-Richter frequency law log10 N(>=M) = a - b*M with b near 1.0 for most regions.
# Question: where does a region's released energy come from? With counts per magnitude bin N(m) = 10^(b*(8-m)) (one M8)
# and energy per event 10^(1.5 m), bin energy is proportional to 10^((1.5-b)*m).
# PREDICTION (before run): at b 1.0 the M8 bin holds 68.4% of the total energy of bins M2..M8 (ratio 10^-0.5 = 0.316 a
# step, geometric sum) and the combined energy is equal to one quake of magnitude 8.11; at b 1.5 (BREAK) every bin holds
# the same 1/7 = 14.3%; at b 2.0 the M2 bin dominates (more than 60%), so "the largest quake dominates the energy" is
# true only while b < 1.5; also one M7 equals 31.6 M6 and 1000 M5 in energy.
import math
def energy(m): return 10 ** (1.5 * m + 4.8)
def shares(b, lo=2, hi=8):
    e = {m: 10 ** (b * (hi - m)) * energy(m) for m in range(lo, hi + 1)}
    tot = sum(e.values()); return {m: v / tot for m, v in e.items()}, tot
def mag_of(E): return (math.log10(E) - 4.8) / 1.5
ratio = energy(7) / energy(6); m5 = energy(7) / energy(5)
res = {}
for b in (0.8, 1.0, 1.5, 2.0):
    sh, tot = shares(b)
    res[b] = (sh, mag_of(tot))
    print(f"b {b}: M8 bin {sh[8]*100:.1f}%, M2 bin {sh[2]*100:.1f}%, combined energy = one M{mag_of(tot):.2f}")
print(f"one M7 = {ratio:.1f} x M6 = {m5:.0f} x M5 in energy")
ok = (abs(res[1.0][0][8] - 0.684) < 0.005 and abs(res[1.0][1] - 8.11) < 0.01 and all(abs(v - 1 / 7) < 1e-9 for v in res[1.5][0].values())
      and res[2.0][0][2] > 0.60 and abs(ratio - 31.6) < 0.1 and abs(m5 - 1000) < 1)
print(f"RESULT: {'PASS' if ok else 'FAIL'} b 1.0: M8 bin {res[1.0][0][8]*100:.1f}% of energy, total = one M{res[1.0][1]:.2f}; b 1.5: every bin {res[1.5][0][5]*100:.1f}%; b 2.0: M2 bin {res[2.0][0][2]*100:.1f}%; M7 = {ratio:.1f} x M6 = {m5:.0f} x M5")
