# Cross-check the exact margin-vector DP against brute force, then show how far a seeded sfc32 sampler can discriminate.
import itertools
from fractions import Fraction

PERMS = list(itertools.permutations(range(3)))
def signs(p):
    pos = {c: i for i, c in enumerate(p)}
    return (1 if pos[0] < pos[1] else -1, 1 if pos[1] < pos[2] else -1, 1 if pos[0] < pos[2] else -1)
SV = [signs(p) for p in PERMS]

def has_cw(m):
    ab, bc, ac = m
    a_beats_b, b_beats_c, a_beats_c = ab > 0, bc > 0, ac > 0
    # candidate strict winners
    if ab > 0 and ac > 0: return True            # A beats B and C
    if ab < 0 and bc > 0: return True            # B beats A and C
    if ac < 0 and bc < 0: return True            # C beats A and B
    return False

def dp(n):
    st = {(0, 0, 0): 1}
    for _ in range(n):
        nx = {}
        for m, c in st.items():
            for s in SV:
                k = (m[0]+s[0], m[1]+s[1], m[2]+s[2])
                nx[k] = nx.get(k, 0) + c
        st = nx
    tot = 6 ** n
    nocw = sum(c for m, c in st.items() if not has_cw(m))
    cyc = sum(c for m, c in st.items() if (m[0] > 0 and m[1] > 0 and m[2] < 0) or (m[0] < 0 and m[1] < 0 and m[2] > 0))
    return Fraction(nocw, tot), Fraction(cyc, tot)

def brute(n):
    nocw = cyc = 0
    for prof in itertools.product(range(6), repeat=n):
        m = [0, 0, 0]
        for i in prof:
            s = SV[i]; m[0] += s[0]; m[1] += s[1]; m[2] += s[2]
        if not has_cw(m):
            nocw += 1
            if (m[0] > 0 and m[1] > 0 and m[2] < 0) or (m[0] < 0 and m[1] < 0 and m[2] > 0): cyc += 1
    return Fraction(nocw, 6 ** n), Fraction(cyc, 6 ** n)

ok = True
# 1) exact vs brute force
for n in range(1, 8):
    d, b = dp(n), brute(n)
    same = d == b
    ok &= same
    print(f"n={n} dp_nocw={float(d[0])*100:.3f}% cyc={float(d[1])*100:.3f}% brute_match={same}")
# 2) published odd-n values and even-n tie mass
pub = {3: 5.556, 7: 7.502, 31: 8.499, 61: 8.635}
for n, v in pub.items():
    nocw, cyc = dp(n)
    r = round(float(cyc) * 100, 3)
    good = abs(r - v) < 0.0015 and nocw == cyc
    ok &= good
    print(f"odd n={n} cycle={r}% expected~{v}% nocw==cycle:{nocw==cyc} below_limit:{float(cyc)<0.08774}")
    ok &= float(cyc) < 0.08774
even = {}
for n in (2, 4, 30):
    nocw, cyc = dp(n); even[n] = (float(nocw)*100, float(cyc)*100)
    print(f"even n={n} nocw={even[n][0]:.1f}% cycles={even[n][1]:.2f}%")
ok &= abs(even[2][0]-66.7) < 0.1 and abs(even[30][0]-29.1) < 0.1 and even[30][1] < 3.3

# 3) seeded sfc32 sampler, state words saved; power to tell exact 8.499% from the 8.774% limit at n=31
M = 0xFFFFFFFF
class Sfc32:
    def __init__(s, a, b, c, d): s.w = [a & M, b & M, c & M, d & M]
    def next(s):
        a, b, c, d = s.w
        t = (a + b + d) & M
        d = (d + 1) & M
        a = b ^ (b >> 9)
        b = (c + (c << 3)) & M
        c = ((c << 21) | (c >> 11)) & M
        c = (c + t) & M
        s.w = [a, b, c, d]
        return t
def warm(seed):
    r = Sfc32(0, seed, seed ^ 0x9E3779B9, 1)
    for _ in range(12): r.next()
    return r
r = warm(12345)
for _ in range(1000): r.next()
snap = list(r.w)
a = [r.next() for _ in range(100)]
r2 = Sfc32(*snap); b = [r2.next() for _ in range(100)]
print("state-word restore identical:", a == b)
ok &= a == b

def sample(n, trials, rng):
    hit = 0
    for _ in range(trials):
        m = [0, 0, 0]
        for _ in range(n):
            s = SV[rng.next() % 6]; m[0] += s[0]; m[1] += s[1]; m[2] += s[2]
        if not has_cw(m): hit += 1
    return hit
TR = 20000
res = {}
for n in (3, 31):
    h = sample(n, TR, warm(2024))
    p = h / TR; se = (p * (1 - p) / TR) ** 0.5
    ex = float(dp(n)[0]); lim = 0.08774
    z_ex = (p - ex) / se; z_lim = (p - lim) / se
    res[n] = (p, se, z_ex, z_lim)
    print(f"sample n={n} trials={TR} est={p*100:.2f}% se={se*100:.2f}% z_vs_exact={z_ex:.2f} z_vs_limit8.774={z_lim:.2f}")
ok &= abs(res[3][2]) < 3 and abs(res[31][2]) < 3
# the break: at n=31 the 20000-trial sampler's z against the limit is small (cannot reject it)
cannot_reject = abs(res[31][3]) < 2
print("n=31 sampler cannot reject 8.774% at 20000 trials:", cannot_reject)
ok &= cannot_reject
# and at n=3 it can
reject3 = abs((res[3][0] - 0.08774) / res[3][1]) > 3
print("n=3 sampler rejects 8.774%:", reject3)
ok &= reject3
print(("RESULT: PASS" if ok else "RESULT: FAIL"), f"dp==brute n1-7; odd cycles<8.774; even n30 nocw {even[30][0]:.1f}%; sfc32 20000-sample n=31 z_limit={res[31][3]:.2f} not rejectable")
