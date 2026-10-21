import hashlib, math
def h(i):  # deterministic "random" source: sha256 of counter
    return int.from_bytes(hashlib.sha256(str(i).encode()).digest()[:8], 'big')
def first_collision(space, reduce):
    seen = set()
    for i in range(10**6):
        v = reduce(h(i), space)
        if v in seen: return i + 1
        seen.add(v)
    return None
def mean_first(space, reduce, trials=40):
    tot = 0
    for t in range(trials):
        seen = set(); n = 0
        while True:
            v = reduce(h(t * 1000003 + n), space); n += 1
            if v in seen: break
            seen.add(v)
        tot += n
    return tot / trials
mod = lambda x, s: x % s
# Scenario 1: space 2^20, expected ~ sqrt(pi/2 * N) = 1286
N = 2**20; exp = math.sqrt(math.pi / 2 * N)
m1 = mean_first(N, mod); print("s1 2^20 mean first collision", m1, "expected", round(exp))
# Scenario 2: scaling: 4x space -> ~2x draws
N2 = 2**22; m2 = mean_first(N2, mod); print("s2 2^22", m2, "ratio", m2 / m1)
# Scenario 3: modulo bias with small word (8-bit source, space 200) -> some buckets double weight
cnt = [0] * 200
for x in range(256): cnt[x % 200] += 1
p_biased = sum((c / 256) ** 2 for c in cnt); p_uniform = 1 / 200
print("s3 collision prob biased", p_biased, "uniform", p_uniform)
# Scenario 4 (break): reject sampling restores uniform
cnt = [0] * 200
for x in range(256):
    if x < 200: cnt[x] += 1
p_rej = sum((c / 200) ** 2 for c in cnt); print("s4 rejection", p_rej)
ok = abs(m1 / exp - 1) < 0.35 and 1.4 < m2 / m1 < 2.9 and p_biased > p_uniform * 1.05 and abs(p_rej - p_uniform) < 1e-12
print("RESULT: %s birthday scaling sqrt(N) holds; modulo bias raises collision prob %.5f vs %.5f; rejection restores" % ("PASS" if ok else "FAIL", p_biased, p_uniform))
