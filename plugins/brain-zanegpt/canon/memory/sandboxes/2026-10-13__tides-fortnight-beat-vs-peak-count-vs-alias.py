# Sandbox: spring-neap fortnight = M2/S2 beat; scan vs peak counting vs daily-sampling alias.
import math
M2, S2, K1 = 12.4206012, 12.0, 23.9344696   # periods, hours
def beat(a, b): return 1.0 / abs(1.0 / a - 1.0 / b)
HOURS = 24 * 240

def series(amps, step=1.0):
    n = int(HOURS / step)
    return [sum(A * math.cos(2 * math.pi * (i * step) / P) for P, A in amps) for i in range(n)]

def daily_range(h):
    return [max(h[d*24:(d+1)*24]) - min(h[d*24:(d+1)*24]) for d in range(len(h)//24)]

def scan(x, lo, hi, step=0.05):
    m = sum(x) / len(x); x = [v - m for v in x]
    best = (0, 0); p = lo
    while p <= hi:
        w = 2 * math.pi / p
        re = sum(v * math.cos(w * i) for i, v in enumerate(x)); im = sum(v * math.sin(w * i) for i, v in enumerate(x))
        pw = re * re + im * im
        if pw > best[0]: best = (pw, p)
        p += step
    return best[1]

def peak_count_period(x):
    pk = [i for i in range(1, len(x) - 1) if x[i] > x[i-1] and x[i] >= x[i+1]]
    return (pk[-1] - pk[0]) / (len(pk) - 1) if len(pk) > 1 else float('nan')

theory = beat(M2, S2) / 24
print(f"theory beat = {theory:.3f} d")
ok = True
# 1) M2+S2
r = daily_range(series([(M2, 1.0), (S2, 0.46)]))
s1, p1 = scan(r, 5, 30), peak_count_period(r)
print(f"1 M2+S2: scan {s1:.2f} d, peakcount {p1:.2f} d"); ok &= abs(s1 - theory) < 0.4
# 2) + K1 diurnal
r = daily_range(series([(M2, 1.0), (S2, 0.46), (K1, 0.5)]))
s2, p2 = scan(r, 5, 30), peak_count_period(r)
print(f"2 +K1: scan {s2:.2f} d, peakcount {p2:.2f} d"); ok &= abs(s2 - theory) < 0.4
# 3) BREAK: S2 absent -> no beat; daily range is flat
r = daily_range(series([(M2, 1.0)]))
spread = max(r) - min(r)
print(f"3 M2 only: daily-range spread {spread:.3f} (no beat expected)"); ok &= spread < 0.25
# 4) BREAK: M2 alone sampled once a day aliases to an apparent fortnight
h = series([(M2, 1.0)])
noon = [h[d*24] for d in range(len(h)//24)]
al = scan(noon, 5, 30)
alias_theory = 1 / abs(1 / (M2/24) - round(24/M2))   # |f - 2| cycles/day inverse
print(f"4 M2 sampled daily: apparent period {al:.2f} d (alias theory {1/abs(24/M2-2):.2f} d)")
fake = abs(al - theory) < 0.5
ok &= fake
print(f"RESULT: {'PASS' if ok else 'FAIL'} scan=%.2f/%.2f d vs beat %.3f; K1 peakcount %.2f d; flat without S2 (%.3f); daily-sampled lone M2 fakes %.2f d" % (s1, s2, theory, p2, spread, al))
