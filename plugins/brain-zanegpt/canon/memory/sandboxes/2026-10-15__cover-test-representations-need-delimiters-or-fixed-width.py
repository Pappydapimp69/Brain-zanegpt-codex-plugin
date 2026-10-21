"""Own-fixture sandbox composing two cover-test representations from the age-cutoff family:
delimited-string substring cover and bitstring/bitmask cover, against a set-subset reference.
Landing sets for lag L at base B, modulus P: {(B + t*L) % M for t in range(n)} (my fixture, not the originals').
Deterministic, stdlib only."""
import itertools
def landing(B, P, L, n, M=40): return sorted({(B + t * L * P) % M + (t % 3) for t in range(n)})
def ref(a, b): return set(b) <= set(a)                                  # reference subset test
def delim(a, b):
    sa = "," + ",".join(map(str, a)) + ","
    return all("," + str(x) + "," in sa for x in b)                      # delimited substring
def nodelim(a, b):
    sa = "".join(map(str, a))
    return all(str(x) in sa for x in b)                                  # BREAK: no delimiter
def bitmask(a, b):
    ma = 0
    for x in a: ma |= 1 << x
    mb = 0
    for x in b: mb |= 1 << x
    return mb & ~ma == 0
def bitstr(a, b, width=64):
    sa = "".join("1" if i in set(a) else "0" for i in range(width))
    sb = "".join("1" if i in set(b) else "0" for i in range(width))
    return all(x == "0" or y == "1" for x, y in zip(sb, sa))             # zip over equal-width strings
def bitstr_short(a, b):
    # BREAK: width too small for positions up to 42 -> truncates
    return bitstr(a, b, width=32)
impls = {"delim": delim, "bitmask": bitmask, "bitstr": bitstr, "nodelim": nodelim, "bitstr_w32": bitstr_short}
total = 0; mism = {k: 0 for k in impls}
for B, P in itertools.product((2111, 2113, 1999), (9, 10)):
    for L1, L2, n1, n2 in itertools.product((1, 2, 3, 5), (1, 2, 3, 5), (2, 4, 7), (2, 4, 7)):
        a = landing(B, P, L1, n1); b = landing(B, P, L2, n2); total += 1
        r = ref(a, b)
        for k, f in impls.items(): mism[k] += (f(a, b) != r)
print("pairs", total, "mismatches vs set reference:", mism)
# targeted: 5 vs 15
print("targeted 5 in [15]: ref", ref([15], [5]), "nodelim", nodelim([15], [5]), "delim", delim([15], [5]))
ok = mism["delim"] == 0 and mism["bitmask"] == 0 and mism["bitstr"] == 0 and mism["nodelim"] > 0 and mism["bitstr_w32"] > 0 and nodelim([15], [5]) and not delim([15], [5])
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" delimited-string, bitmask and fixed-width bitstring agree with set on {total} pairs; no-delimiter wrong on {mism['nodelim']}, too-narrow bitstring wrong on {mism['bitstr_w32']}")
