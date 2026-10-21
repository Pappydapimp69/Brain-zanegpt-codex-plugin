# Companion claim: gate-only invalid(L) = N*min(x, 1-a) on a golden rotation word (x = ||L*a||, a = density).
# Test it WITH the one-sided periodic formula (N/P)*min(L,W,P-L,P-W): the general form should be N*min(x, a, 1-a).
import math
N = 900; M = N + 200
def rot(a, b, n): return [int(math.floor((t+1)*a + b) - math.floor(t*a + b)) for t in range(n)]
def inv(s, L): return sum(1 for t in range(N) if s[t] == 1 and s[t+L] == 0)
def x(L, a): f = (L*a) % 1.0; return min(f, 1-f)
def worst(a, b, form, Ls=range(1, 145)):
    s = rot(a, b, M)
    return max(abs(inv(s, L) - N*form(L, a)) for L in Ls)
old = lambda L, a: min(x(L, a), 1-a)          # the companion's form
new = lambda L, a: min(x(L, a), a, 1-a)       # periodic-formula form
res = {}
for name, a in [("phi-1", (math.sqrt(5)-1)/2), ("0.718", math.e-2), ("0.414", math.sqrt(2)-1), ("0.142", math.pi-3)]:
    res[name] = (worst(a, 0.0, old), worst(a, 0.31, new), worst(a, 0.0, new))
    print(f"a={name}: max |err| old form={res[name][0]:.1f}  new form={res[name][2]:.1f} (offset .31: {res[name][1]:.1f})")
# periodic control: (N/P)*min(L,W,P-L,P-W) exact for P=12,W=5 over lags 1..11
P, W = 12, 5
ps = [1 if t % P < W else 0 for t in range(M)]
per_ok = all(inv(ps, L) == (N//P)*min(L, W, P-L, P-W) for L in range(1, 12))
# BREAK: density above 0.5 where old==new coincide only if 1-a<=a; low-density must separate them
sep = res["0.142"][0] > 5*max(res["0.142"][2], 1) and res["0.414"][0] > 5*max(res["0.414"][2], 1)
ok = per_ok and sep and all(v[2] <= 3 for v in res.values()) and res["phi-1"][0] <= 3
print("RESULT: %s new form N*min(x,a,1-a) max err %s ticks; old N*min(x,1-a) err %s at a=0.142,0.414 (phi %.1f); periodic %s" % (
    "PASS" if ok else "FAIL", "/".join("%.1f" % v[2] for v in res.values()),
    "%.0f/%.0f" % (res["0.142"][0], res["0.414"][0]), res["phi-1"][0], per_ok))
