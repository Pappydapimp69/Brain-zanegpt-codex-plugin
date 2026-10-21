# Own fixture: 6-digit codes at stride 7919 (deterministic sample of 1000 codes); error set per code =
# every single-digit substitution (54) + every adjacent transposition of distinct digits.
# Also double substitutions (any two positions). Check A: digit sum mod 10. Check B: weighted sum (weights 1..6) mod 11. Check C: digit sum mod 5.
def digs(n): return [int(c) for c in f"{n:06d}"]
A = lambda d: sum(d) % 10
B = lambda d: sum((i+1)*x for i, x in enumerate(d)) % 11
C = lambda d: sum(d) % 5
def errors(d):
    for i in range(6):
        for v in range(10):
            if v != d[i]: e = d[:]; e[i] = v; yield "sub", e
    for i in range(6):
        for j in range(i+1, 6):
            for v in range(10):
                for w in range(10):
                    if v != d[i] and w != d[j]: e = d[:]; e[i] = v; e[j] = w; yield "dbl", e
    for i in range(5):
        if d[i] != d[i+1]: e = d[:]; e[i], e[i+1] = e[i+1], e[i]; yield "swap", e
codes = [digs((k*7919) % 1000000) for k in range(60)]
def rates(checks):
    n = 0; miss = [0]*len(checks); joint = 0; by = {"sub": [0, 0], "swap": [0, 0], "dbl": [0, 0]}
    for d in codes:
        for kind, e in errors(d):
            n += 1; hit = [c(d) == c(e) for c in checks]
            for i, h in enumerate(hit): miss[i] += h
            j = all(hit); joint += j; by[kind][0] += j; by[kind][1] += 1
    return n, [m/n for m in miss], joint/n, by
for name, cs in (("A+B unlike", (A, B)), ("A+C dependent", (A, C))):
    n, m, j, by = rates(cs)
    prod = m[0]*m[1]
    print(f"{name}: n={n} missA={m[0]:.4f} missB={m[1]:.4f} joint={j:.5f} product={prod:.5f} ratio={j/prod:.2f} swapjoint={by['swap'][0]}/{by['swap'][1]}")
    if "unlike" in name: ru = j/prod; ju = j; mA = m[0]
    else: rd = j/prod; jd = j
swapA = rates((A,))[3]["swap"]; swapB = rates((B,))[3]["swap"]
print("A misses swaps:", swapA, " B misses swaps:", swapB)
ok = ru < 0.6 and rd >= 1.9 and abs(jd - mA) < 1e-9 and swapA[0] == swapA[1] and swapB[0] == 0
print(f"RESULT: {'PASS' if ok else 'FAIL'} unlike ratio {ru:.2f} (joint {ju:.5f}); dependent ratio {rd:.2f} with joint {jd:.5f} vs missA {mA:.5f}; A misses {swapA[0]}/{swapA[1]} swaps, B {swapB[0]}")
