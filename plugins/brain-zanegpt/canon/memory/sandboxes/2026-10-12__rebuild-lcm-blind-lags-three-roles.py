# Rebuild: mismatch-based staleness aliases at the lcm of contributing periods; age tag does not.
# Own fixture: three roles (periods 6, 10, 14 -> lcm 210), priority resolver with windows,
# N=840 samples, age threshold 3. Plus a masked-role control.
from math import gcd
from functools import reduce

def lcm(*xs): return reduce(lambda a, b: a * b // gcd(a, b), xs)

N, THR = 840, 3
ROLES = [("dash", 6, 2), ("block", 10, 3), ("wait", 14, 5)]  # name, period, active window

def resolve(t, roles):
    for name, p, w in roles:
        if (t % p) < w:
            return f"{name}{t % p}"
    return "idle"

def counts(L, roles):
    out = [resolve(t, roles) for t in range(N + L)]
    mism = sum(1 for t in range(N) if out[t] != out[t + L])  # hint emitted at t, read at t+L
    age = sum(1 for t in range(N) if L > THR)                 # emit-time stamp, age = L
    return mism, age

def minimal_period(roles, cap=2000):
    out = [resolve(t, roles) for t in range(2 * cap)]
    for P in range(1, cap):
        if all(out[t] == out[t + P] for t in range(cap)):
            return P

ok = True
L_full = lcm(6, 10, 14)
print("lcm(6,10,14) =", L_full, "observed output period =", minimal_period(ROLES))
for L in [2, 6, 10, 14, 30, 42, 70, 105, 210, 420]:
    m, a = counts(L, ROLES)
    print(f"L={L:4d} mismatch={m:4d} age={a:4d}")
    want_zero = (L % L_full == 0)
    if want_zero != (m == 0): ok = False
    if a != (N if L > THR else 0): ok = False

# exhaustive: mismatch==0 iff L multiple of 210, for L in 1..450
for L in range(1, 451):
    m, _ = counts(L, ROLES)
    if (m == 0) != (L % L_full == 0):
        ok = False; print("unexpected at", L, m)

# masked-role control: a higher-priority role that is always active hides the other role entirely
masked = [("a", 4, 4), ("b", 9, 2)]  # a always active -> b never contributes
mp = minimal_period(masked)
m36, _ = counts(36, masked); m4, _ = counts(4, masked)
print(f"masked: lcm(4,9)=36, observed period={mp}, mismatch L=4 -> {m4}, L=36 -> {m36}")
masked_ok = (mp == 4 and m4 == 0)  # blind lag is lcm of CONTRIBUTING periods only
if not masked_ok: ok = False

print("RESULT: %s mismatch zero iff L%%210==0 over L=1..450 (>0 at 6,10,14,30,42,70,105); age tag flags 840/840 for L>3; masked role shrinks blind lag to contributing lcm (4)" % ("PASS" if ok else "FAIL"))
