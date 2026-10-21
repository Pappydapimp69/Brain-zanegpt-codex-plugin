"""RUN 1 FAILED: I had the digit-unit backwards. One unit of the third significant digit is 0.01 whatever the leading digit, which is ~1% of a 1.x result but ~0.1% of a 9.x result, so a flat relative error passes the three-digit test near 1 and fails near 9. Revised prediction (written before run 2): results 1-2 are third-digit-correct in >=99%, results 5-10 in <=60%, and the pass rate falls monotonically with leading digit.
Original prediction (before run 1): model a slide rule as log10 positions on a scale of 1000 divisions per decade, each reading rounded
to the nearest division (half-step 0.0005 in log10). Multiplying mantissas a*b (1<=a,b<10) by adding positions and rounding
the sum gives relative error bounded by 3 half-steps*ln10 = 0.35%, nearly the same for small and large products (flat in
RELATIVE terms). So the sample "three significant digits" claim (error < 0.5 unit in the third digit) fails for results with
leading digits 1.x (unit = 0.001 of ~1.0 = 0.1%) in at least 30% of the sampled pairs, holds for results 5.x-9.x in at least 95%.
The decade: mantissa product lands in [1,100); without the user-tracked exponent, 40% or more of 9x9 grid products read as the wrong
power of ten (anything with mantissa product >=10 wraps to the next decade)."""
import math
STEPS = 1000
rd = lambda x: round(math.log10(x) * STEPS) / STEPS
def mult(a, b):
    pos = rd(a) + rd(b)                      # lengths add; read the sum on the scale
    pos = round(pos * STEPS) / STEPS
    wrap = pos >= 1                          # slid past the index: the result is in the next decade
    return 10 ** (pos - (1 if wrap else 0)), wrap
grid = [round(1 + i * 0.1, 1) for i in range(0, 90)]       # 1.0 .. 9.9
rows = []
for a in grid:
    for b in grid:
        if a * b > 9.9995 and a * b < 10.0005: continue
        m, wrap = mult(a, b)
        true = a * b; true_m = true / 10 if true >= 10 else true
        rel = abs(m - true_m) / true_m
        unit = 10 ** (math.floor(math.log10(true_m)) - 2)        # one unit in the third significant digit
        rows.append((true_m, rel, abs(m - true_m) <= 0.5 * unit, wrap, true >= 10))
maxrel = max(r[1] for r in rows)
low = [r for r in rows if r[0] < 2]; high = [r for r in rows if r[0] >= 5]
fail_low = sum(not r[2] for r in low) / len(low); ok_high = sum(r[2] for r in high) / len(high)
wrap_mismatch = sum(r[3] != r[4] for r in rows)
raw_wrong = sum(1 for r in rows if r[4]) / len(rows)         # share of products whose power of ten is off by one if the exponent is not tracked
bylead = {}
for r in rows: bylead.setdefault(int(r[0]), []).append(r[2])
rate = [sum(v) / len(v) for k, v in sorted(bylead.items())]
mono = all(rate[i] >= rate[i + 1] - 0.02 for i in range(len(rate) - 1))
print(len(rows), maxrel, fail_low, ok_high, wrap_mismatch, raw_wrong, [round(x, 2) for x in rate])
ok = maxrel < .0036 and (1 - fail_low) >= .99 and ok_high <= .60 and mono and wrap_mismatch == 0 and raw_wrong >= .40
print(("RESULT: PASS (revised claim) " if ok else "RESULT: FAIL ") +
      f"{len(rows)} products: max relative error {maxrel:.3%}; third-digit correct by leading digit 1..9 {[round(x,2) for x in rate]} (1-2: {1-fail_low:.1%}, 5-10: {ok_high:.1%}); decade wrap matches the true carry ({wrap_mismatch} mismatches), {raw_wrong:.1%} of products need an exponent bump")
