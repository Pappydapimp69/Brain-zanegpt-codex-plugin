"""New-half pick: tension-as-information-gap + film + sandbox-ad-hook-length-ending-network-crossover/E1.
That entry's funnel: value = hook_survival * exp(-h (L-3)) * (1 + L/60) * ending_mult, with
social fixable-fail ending 1.65 vs clean/none 1.0, and a 15-vs-30 s crossover h* ~ 0.0122/s,
which ASSUMES every cut keeps its ending. fail-ad-cutdowns-keep-the-gap: clock truncation
loses the fail ending in every cut-down; beat-anchored cuts keep it down to 10 s.
Recompute the crossover when the 15 s (and 10 s) cut is made each way. Deterministic.
PREDICTION (written before running): with anchored cuts h* stays 0.0122; with truncated
15 s cuts (ending mult drops to 1.0) h* rises above 0.04/s, so on most social decay rates
(1-4%/s) the 30 s master would beat the 15 s cut - the '15 s beats 30 s' rule then inverts."""
import math
HS = 0.35
def value(L, h, mult): return HS * math.exp(-h * (L - 3)) * (1 + L / 60) * mult
def crossover(L1, m1, L2, m2):
    # value(L1) == value(L2): exp(-h(L1-L2)) ... solve h = ln((i2*m2)/(i1*m1)) / (L2-L1)
    i1, i2 = 1 + L1 / 60, 1 + L2 / 60
    return math.log((i2 * m2) / (i1 * m1)) / (L2 - L1)
h_anchor = crossover(15, 1.65, 30, 1.65)
h_trunc = crossover(15, 1.0, 30, 1.65)
h10_anchor = crossover(10, 1.65, 30, 1.65); h10_trunc = crossover(10, 1.0, 30, 1.65)
print(f"15 vs 30 s crossover: anchored cut h* = {h_anchor:.4f}/s, truncated cut h* = {h_trunc:.4f}/s")
print(f"10 vs 30 s crossover: anchored h* = {h10_anchor:.4f}/s, truncated h* = {h10_trunc:.4f}/s")
for h in (0.01, 0.02, 0.03, 0.04, 0.06):
    a = value(15, h, 1.65) / value(30, h, 1.65); t = value(15, h, 1.0) / value(30, h, 1.65)
    print(f"decay {h:.2f}/s: 15s/30s value  anchored {a:.2f}  truncated {t:.2f}")
wins_trunc = [h for h in (0.01, 0.02, 0.03, 0.04) if value(15, h, 1.0) > value(30, h, 1.65)]
ok = abs(h_anchor - 0.0122) < 0.0005 and h_trunc > 0.04 and not wins_trunc
print(f"RESULT: {'PASS' if ok else 'FAIL'} anchored 15s cut keeps h*={h_anchor:.4f}; truncated 15s cut moves it to {h_trunc:.4f}/s "
      f"({h_trunc / h_anchor:.1f}x); truncated 15s beats the 30s master at decay 1-4%/s: {wins_trunc or 'never'}")
