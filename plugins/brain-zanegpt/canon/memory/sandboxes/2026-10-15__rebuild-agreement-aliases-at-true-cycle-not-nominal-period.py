# Rebuild: agreement ("flags" stale = state at hint time differs from state at landing) aliases at multiples of
# the TRUE repeat length. Own fixture: duty 7 ticks on, 900 ticks, three waves: strict 15, jitter 15/16 (cycle 31),
# jitter 15/16/17 (cycle 48; built to break a "31 is special" reading).
# Prediction (written before running): strict flags 0 at L=15,30; jitter15/16 flags >0 but <all at L=15,30 and exactly 0 at
# L=31,62; age tag flags every hint at L>2; jitter 15/16/17 flags >0 at L=31 and exactly 0 at L=48 and 96.
T = 900; DUTY = 7
def wave(periods):
    s = []; i = 0
    while len(s) < T + 200:
        p = periods[i % len(periods)]; s += [1] * DUTY + [0] * (p - DUTY); i += 1
    return s
def flags(s, L):
    n = T; f = sum(1 for t in range(n) if s[t] != s[t + L]); return f, n
waves = {"strict15": [15], "jit15/16": [15, 16], "jit15/16/17": [15, 16, 17]}
res = {}
for nm, per in waves.items():
    s = wave(per)
    res[nm] = {L: flags(s, L)[0] for L in (3, 15, 30, 31, 48, 62, 96)}
    print(nm, res[nm])
N = T
ok = []
ok.append(res["strict15"][15] == 0 and res["strict15"][30] == 0)
j = res["jit15/16"]
ok.append(0 < j[15] < N and 0 < j[30] < N and j[31] == 0 and j[62] == 0)
ok.append(all(res[n][3] > 0 for n in res))   # stands in for 'agreement catches some' - age tag flags all by construction N=900
k = res["jit15/16/17"]
ok.append(k[31] > 0 and k[48] == 0 and k[96] == 0)
print("checks", ok)
print(("RESULT: PASS" if all(ok) else "RESULT: FAIL"), f"strict L15/30 flags {res['strict15'][15]}/{res['strict15'][30]}; jitter15/16 L15 {j[15]}, L30 {j[30]}, L31 {j[31]}, L62 {j[62]}; jitter15/16/17 L31 {k[31]}, L48 {k[48]}, L96 {k[96]}")
