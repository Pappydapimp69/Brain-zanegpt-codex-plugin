import itertools
def gray(n): return n ^ (n >> 1)
def ungray(g):
    n = 0
    while g: n ^= g; g >>= 1
    return n
def worst(k, d, enc, dec):
    N = 1 << k; w = 0
    for a in range(N):
        states = [enc((a + j) % N) for j in range(d + 1)]
        win = {(a + j) % N for j in range(d + 1)}
        for pick in itertools.product(range(d + 1), repeat=k):  # each bit sampled from any state in window
            code = sum(((states[p] >> b) & 1) << b for b, p in enumerate(pick))
            v = dec(code)
            dist = min(min((v - m) % N, (m - v) % N) for m in win)
            w = max(w, dist)
    return w
res = {}
for k in (3, 4, 5):
    res[("bin", k, 1)] = worst(k, 1, lambda x: x, lambda x: x)
    res[("gray", k, 1)] = worst(k, 1, gray, ungray)
    res[("gray", k, 2)] = worst(k, 2, gray, ungray)
print(res)
# one-bit cyclic sequences: n distinct codes, consecutive (incl. wrap) differ by one bit
def cyc(n, k):
    def dfs(path, used):
        if len(path) == n: return bin(path[-1] ^ path[0]).count("1") == 1
        for b in range(k):
            nx = path[-1] ^ (1 << b)
            if nx not in used:
                used.add(nx); path.append(nx)
                if dfs(path, used): return True
                path.pop(); used.discard(nx)
        return False
    return dfs([0], {0})
exist = {n: any(cyc(n, k) for k in range(1, 6)) for n in range(2, 17)}
print(exist)
ok = (all(res[("bin", k, 1)] == (1 << (k - 1)) - 1 for k in (3, 4, 5)) and all(res[("gray", k, 1)] == 0 for k in (3, 4, 5))
      and all(res[("gray", k, 2)] == 1 for k in (3, 4, 5)) and all(exist[n] == (n % 2 == 0) for n in exist))
print("RESULT: %s binary worst %s gray1 0 gray2 %s; one-bit cycle exists exactly for even n 2-16 (bits<=5)" % (
    "PASS" if ok else "FAIL", [res[("bin", k, 1)] for k in (3, 4, 5)], [res[("gray", k, 2)] for k in (3, 4, 5)]))
