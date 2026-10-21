"""Re-verify seven#E81 (sway out of the sickness band, off the full frame) from a
new angle, composed with the sound-first-then-sight curve. E81 fixed the peak at
0.2-0.4 Hz and a linear field term. Here: peak at each published visual-only
value (0.06, 0.1, 0.2, 0.3 Hz), roll-offs of 6 or 12 dB/octave on each side, and
two field models: area-linear (E81) and eccentricity-weighted (vection driven
mostly by the periphery: weight rises linearly with radius). Deterministic."""
import math
def weight(f, peak, lo_db, hi_db):
    octv = math.log2(f / peak)
    db = -lo_db * (-octv) if octv < 0 else -hi_db * octv
    return 10 ** (db / 20)
def field(kind, edge_area):
    # share of 'vection drive' in an outer ring holding edge_area of a disc's area
    if kind == "area": return edge_area
    r0 = math.sqrt(1 - edge_area)               # ring from r0 to 1; drive density ~ r over area 2*pi*r dr
    num = (1 - r0 ** 3) / 3; den = 1 / 3        # integral of r * r dr
    return num / den
res = {}
for peak in (0.06, 0.1, 0.2, 0.3):
    for lo, hi in ((6, 12), (12, 6), (6, 6), (12, 12)):
        ref = weight(0.3, peak, lo, hi)
        res[(peak, lo, hi)] = (weight(2.0, peak, lo, hi) / ref, weight(0.05, peak, lo, hi) / ref)
jit_ok = all(j <= 0.10 for j, _ in res.values())
drift_breaks = [(k, d) for k, (_, d) in res.items() if d >= 1.0]
for k, (j, d) in res.items():
    print(f"peak {k[0]:>4} Hz lo/hi {k[1]}/{k[2]} dB/oct: 2 Hz jitter {j:.3f}  0.05 Hz drift {d:.3f}  (vs 0.3 Hz sway = 1)")
va, vp = field("area", 0.3), field("periph", 0.3)
print(f"30% edge-only vignette: area model keeps {va:.3f} of drive (cut {1-va:.0%}); periphery-weighted keeps {vp:.3f} (cut {1-vp:.0%})")
for name, c in (("linear", [0, 1/3, 2/3, 1]), ("banded", [0, .1, .5, .9])):
    print(f"{name}: share of the run's visual exposure in the deepest band {c[3]/sum(c):.2f}")
deep = (0.9 / 1.5)
print(f"jitter <=0.10 at every peak/slope: {jit_ok}; drift >= in-band sway in {len(drift_breaks)}/16 cells (peaks {sorted({k[0] for k,_ in drift_breaks})})")
ok = jit_ok and not drift_breaks and (1 - vp) >= 0.6
print(f"RESULT: {'PASS' if ok else 'FAIL'} jitter robust (max {max(j for j,_ in res.values()):.3f}); slow drift as bad or worse than 0.3 Hz sway in {len(drift_breaks)}/16 cells; "
      f"vignette cut {1-va:.0%} area vs {1-vp:.0%} periphery-weighted; banded puts {deep:.0%} of visuals in the deepest band")
