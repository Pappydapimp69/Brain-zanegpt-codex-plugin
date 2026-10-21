"""Sandbox: Pythagorean-comma kernel x surveying closure kernel (brainwork/E184).
A 12-note circle of fifths is a closed traverse: misclosure = sum(fifths) - 7 octaves.
Deterministic, stdlib only."""
from fractions import Fraction
from math import log2
c = lambda r: 1200 * log2(r)
ok = True
# S1: kernel numbers
comma = c(Fraction(3, 2) ** 12 / 2 ** 7)
pf = c(1.5); just3 = c(1.25)
syntonic = c(Fraction(81, 80)); qcm = pf - syntonic / 4   # quarter-comma meantone fifth
wolf = lambda fifth: 8400 - 11 * fifth  # 7 octaves minus 11 tempered fifths
clos = lambda n: abs(n * pf - 1200 * round(n * pf / 1200))
print(f"S1 comma={comma:.2f} pyth_wolf={wolf(pf):.2f} et_third_err={400 - just3:.2f} "
      f"qcm_fifth={qcm:.2f} qcm_wolf={wolf(qcm):.2f} closure n12={clos(12):.2f} n41={clos(41):.2f} n53={clos(53):.2f}")
ok &= round(comma, 2) == 23.46 and round(wolf(pf), 2) == 678.49 and round(400 - just3, 2) == 13.69
ok &= round(qcm, 2) == 696.58 and round(wolf(qcm), 2) == 737.64 and round(clos(53), 2) == 3.62
ok &= [n for n in range(1, 60) if clos(n) < 5] == [53]

def misclosure(fifths, octave=1200.0): return sum(fifths) - 7 * octave
def thirds(fifths, octave=1200.0):  # major third from note i = 4 fifths up - 2 octaves
    return [sum(fifths[(i + k) % 12] for k in range(4)) - 2 * octave for i in range(12)]

# S2 (BREAK closure as a validator): stretched tuning, every fifth 700.7 and octave 1201.2
st = [700.7] * 12
m2 = misclosure(st, 1201.2); oct_err = 1201.2 - 1200; fifth_err = 700.7 - 700
print(f"S2 stretched: misclosure={m2:.3f} cents, yet octave off {oct_err:.1f} and every fifth off {fifth_err:.1f} vs 12-TET")
ok &= abs(m2) < 1e-9 and oct_err > 1

# S3 (BREAK even tempering): eleven fifths at 700, one blundered to 710; distribute misclosure evenly
bl = [700.0] * 12; bl[5] = 710.0
m3 = misclosure(bl); adj = [f - m3 / 12 for f in bl]
err_raw = [abs(f - 700) for f in bl]; err_adj = [abs(f - 700) for f in adj]
good_raw = sum(e == 0 for e in err_raw); good_adj = sum(e < 1e-9 for e in err_adj)
t_raw = [abs(t - 400) for t in thirds(bl)]; t_adj = [abs(t - 400) for t in thirds(adj)]
print(f"S3 blunder: misclosure={m3:.2f}; exact fifths raw {good_raw}/12 -> adjusted {good_adj}/12; "
      f"worst fifth {max(err_raw):.2f}->{max(err_adj):.2f}; thirds off raw {sum(e > 1e-9 for e in t_raw)}/12 "
      f"(max {max(t_raw):.2f}) -> adjusted {sum(e > 1e-9 for e in t_adj)}/12 (max {max(t_adj):.2f})")
ok &= good_raw == 11 and good_adj == 0 and abs(max(err_adj) - 9.1667) < 1e-3
# locate first: residual vs median
med = sorted(bl)[6]; suspect = max(range(12), key=lambda i: abs(bl[i] - med))
fixed = bl[:]; fixed[suspect] = med
print(f"S3b locate-first: suspect fifth index {suspect}, after re-tuning misclosure={misclosure(fixed):.2f}")
ok &= suspect == 5 and abs(misclosure(fixed)) < 1e-9

print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" comma {comma:.2f}, only n=53 closes within 5 cents ({clos(53):.2f}); a stretched circle closes at {m2:.3f} with octaves {oct_err:.1f} off;"
      f" even tempering of one 10-cent blunder leaves 0/12 exact fifths (was 11/12) and 12/12 thirds off (was {sum(e > 1e-9 for e in t_raw)}/12)")
