# Schroeder/Freeverb comb RT60: formula vs measurement, shared-g spread, per-comb g equalisation.
import math
FS = 44100
DS = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617]   # Freeverb comb lengths @44.1k

def comb_ir(D, g, n):
    # feedback comb y[n] = x[n-D] + g*y[n-D]
    y = [0.0] * n
    for i in range(D, n):
        y[i] = (1.0 if i == D else 0.0) + g * y[i - D]
    return y

def rt60(ir):
    # Schroeder backward integration, fit -5..-35 dB, extrapolate to -60
    e = [v * v for v in ir]; tot = 0.0; edc = [0.0] * len(e)
    for i in range(len(e) - 1, -1, -1): tot += e[i]; edc[i] = tot
    db = [10 * math.log10(v / edc[0]) if v > 0 else -999 for v in edc]
    t5 = next(i for i, v in enumerate(db) if v <= -5); t35 = next(i for i, v in enumerate(db) if v <= -35)
    return 60 / ((35 - 5) / ((t35 - t5) / FS))

def formula(D, g): return -3 * D / (FS * math.log10(g))

N = FS * 8
res = []
# 1) single comb: measurement matches formula
m1, f1 = rt60(comb_ir(1557, .84, N)), formula(1557, .84)
res.append(abs(m1 - f1) / f1 < .05); print(f"1) D=1557 g=.84 formula {f1:.3f}s measured {m1:.3f}s")
# 2) shared g across Freeverb combs: per-comb RT60 spread, and what the SUM measures (BREAK case: 'shared g = one decay')
per = [formula(D, .84) for D in DS]
summ = [sum(v) for v in zip(*[comb_ir(D, .84, N) for D in DS])]
ms = rt60(summ); mean = sum(per) / len(per)
print(f"2) shared g=.84: per-comb {min(per):.2f}..{max(per):.2f}s (x{max(per)/min(per):.2f}), mean {mean:.2f}s, sum measures {ms:.2f}s")
res.append(max(per) / min(per) > 1.4 and min(per) < ms < max(per))   # first-run guess 'sum tracks longest' was refuted: it lands between
# 3) per-comb g_i = 10^(-3 D_i/(FS*T)) equalises to target T=3.0s
T = 3.0; gs = [10 ** (-3 * D / (FS * T)) for D in DS]
summ = [sum(v) for v in zip(*[comb_ir(D, g, FS * 12) for D, g in zip(DS, gs)])]
m3 = rt60(summ); print(f"3) target {T}s, g {min(gs):.4f}..{max(gs):.4f}, sum measures {m3:.3f}s")
res.append(abs(m3 - T) / T < .05)
print(("RESULT: PASS" if all(res) else "RESULT: FAIL") + f" formula {f1:.2f}~{m1:.2f}s; shared-g spread x{max(per)/min(per):.2f}, sum {ms:.2f}s sits between mean {mean:.2f}s and longest {max(per):.2f}s; per-comb g hits {m3:.2f}s of {T}s")
