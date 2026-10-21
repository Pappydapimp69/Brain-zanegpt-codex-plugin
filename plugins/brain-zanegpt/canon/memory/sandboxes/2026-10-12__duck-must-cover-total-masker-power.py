"""Gap pass on seven E73 and E78 (must-land voice duck: 6 dB lets mono carry 6 at 10%/dB; E78: 8.5 dB at
5%/dB), both built on 1.5 dB per doubling of talkers. Brungart, Simpson, Ericson & Scott 2001 (JASA
110:2527, read first-hand): with two or more same-sex maskers, intelligibility depended 'almost
exclusively on the overall SNR' (linear, r = 0.98), i.e. the TOTAL masker power, not the number of
talkers; equal-level talkers add 10*log10(m) dB, which is 3.01 dB per doubling.
Deterministic: line lands 0.60 against one equal masker at 0 dB (E73's calibration), linear in SNR with
slope s = 5/10/15 %/dB (Brungart: near linear), mono, maskers ducked by d dB below the line.
Required duck for N voices at 80%: d = (0.80-0.60)/s + 10*log10(N-1).
Predictions written before running:
 P1 at 5%/dB, carrying 6 voices needs at least 10 dB of duck (E78 says 8.5).
 P2 at 10%/dB a 6 dB duck carries at most 3 voices (E73 says 6).
 P3 the duck needed grows by about 7 dB from 2 to 6 voices at every slope (slope-independent part).
 P4 under E73/E78's 1.5 dB per doubling the same growth is under 4 dB (so their model understates it ~2x).
"""
import math

def need(N, s, per_doubling=None):
    base = (0.80 - 0.60) / s
    m = N - 1
    pen = 10 * math.log10(m) if per_doubling is None else per_doubling * math.log2(m)
    return base + pen

def carry(d, s, per_doubling=None):
    n = 1
    for N in range(2, 60):
        if need(N, s, per_doubling) <= d + 1e-9: n = N
        else: break
    return n

for s in (0.05, 0.10, 0.15):
    print(f"slope {int(s*100)}%/dB: duck for 2/3/4/6 voices (power sum) " +
          "/".join(f"{need(N, s):.1f}" for N in (2, 3, 4, 6)) + " dB; with 1.5 dB/doubling " +
          "/".join(f"{need(N, s, 1.5):.1f}" for N in (2, 3, 4, 6)) +
          f"; a 6 dB duck carries {carry(6, s)} (power) vs {carry(6, s, 1.5)} (1.5/dbl)")
grow = need(6, 0.10) - need(2, 0.10); grow15 = need(6, 0.10, 1.5) - need(2, 0.10, 1.5)
p1 = need(6, 0.05) >= 10
p2 = carry(6, 0.10) <= 3
p3 = abs(grow - 7.0) < 0.1
p4 = grow15 < 4
checks = [("P1 6 voices at 5%/dB need >= 10 dB", p1), ("P2 6 dB at 10%/dB carries <= 3", p2),
          ("P3 2->6 voices adds ~7 dB", p3), ("P4 1.5/doubling adds < 4 dB", p4)]
held = sum(ok for _, ok in checks)
for n, ok in checks: print(("held   " if ok else "MISSED ") + n)
print(f"RESULT: {'PASS' if held == 4 else 'FAIL'} {held}/4; 6 voices need {need(6,0.05):.1f}/{need(6,0.10):.1f}/{need(6,0.15):.1f} dB "
      f"at 5/10/15%/dB; 6 dB carries {carry(6,0.05)}/{carry(6,0.10)}/{carry(6,0.15)}; growth 2->6 voices {grow:.1f} dB vs {grow15:.1f} at 1.5/doubling")
