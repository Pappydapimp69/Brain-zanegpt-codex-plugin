# Pin-tumbler keyspace: depths 0-9, 5 pins, MACS (max adjacent cut spec) 7; master keying adds a second shear option per chamber.
from itertools import product
D, P, MACS = 10, 5, 7
def ok(key, macs): return all(abs(a - b) <= macs for a, b in zip(key, key[1:]))
def dp(p, macs):
    cnt = [1] * D
    for _ in range(p - 1):
        cnt = [sum(cnt[j] for j in range(D) if abs(i - j) <= macs) for i in range(D)]
    return sum(cnt)
brute = sum(1 for k in product(range(D), repeat=P) if ok(k, MACS))
print("total", D**P, "MACS7 brute", brute, "dp", dp(P, MACS), "removed %.1f%%" % (100 * (1 - brute / D**P)))
# master keying: each chamber gets one extra cut depth (master); a lock opens for 2^P keys at most; count MACS-valid ones
import random
locks = [(0, 5, 2, 7, 4), (1, 9, 0, 8, 2), (3, 3, 3, 3, 3)]
def openers(change, master):
    opts = [(c, m) if c != m else (c,) for c, m in zip(change, master)]
    return [k for k in product(*opts) if ok(k, MACS)]
master = (6, 1, 8, 3, 9)
counts = [len(openers(l, master)) for l in locks]
print("openers per master-keyed lock (max 32):", counts)
# distinct lock count at fixed master: change keys that are valid and whose master combination is distinct fully
valid_changes = [k for k in product(range(D), repeat=P) if ok(k, MACS)]
# a change key is usable only if it differs from the master in every chamber (else the chamber has one shear line)
full = sum(1 for k in valid_changes if all(a != b for a, b in zip(k, master)))
print("change keys differing from master in all 5 chambers", full, "of", len(valid_changes))
ok_ = brute == dp(P, MACS) and 70000 < brute < 85000 and counts[2] >= 1 and max(counts) <= 32
print("RESULT: %s MACS7 keeps %d of %d (%.1f%% removed); master-keyed locks open %s keys of max 32; all-different change keys %d" % ("PASS" if ok_ else "FAIL", brute, D**P, 100 * (1 - brute / D**P), counts, full))
