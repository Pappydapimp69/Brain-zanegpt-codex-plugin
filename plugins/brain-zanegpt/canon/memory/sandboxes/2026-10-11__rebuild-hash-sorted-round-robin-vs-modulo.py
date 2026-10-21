"""Blind rebuild of: hash-sorted round-robin vs hash modulo for dealing ids into K buckets.
My prediction (written before first run): modulo spread (max-min bucket count) median >=4 at N=42,K=6 and round-robin spread <=1 always;
round-robin moves ~40-60% of ids when one id is added (random position shifts the deal), modulo moves 0%; both move >70% when K 6->7 (round robin ~85%, modulo ~86%);
reversing input order changes round-robin deal on 0 ids if sorted by (hash,id) but >=30/42 if dealt in raw order; builtin str hash differs across PYTHONHASHSEED for >=25/42 ids."""
import hashlib, subprocess, sys, statistics, os
def h(s): return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "big")
def modulo(ids, k): return {i: h(i) % k for i in ids}
def rr(ids, k):
    order = sorted(ids, key=lambda i: (h(i), i))
    return {i: n % k for n, i in enumerate(order)}
def rr_raw(ids, k): return {i: n % k for n, i in enumerate(ids)}
def spread(a, k):
    c = [0] * k
    for v in a.values(): c[v] += 1
    return max(c) - min(c)
def moved(a, b):
    common = [i for i in a if i in b]
    return sum(a[i] != b[i] for i in common) / len(common)
ok = True
K = 6
def ns(n, j): return ["ns%d-user-%d" % (j, x) for x in range(n)]
res = {}
for n in (42, 420, 4200):
    ms = [spread(modulo(ns(n, j), K), K) for j in range(200)]
    rs = [spread(rr(ns(n, j), K), K) for j in range(200)]
    rel = statistics.median(ms) / (n / K)
    res[n] = (statistics.median(ms), max(ms), max(rs), rel)
    print("N", n, "modulo spread median", statistics.median(ms), "max", max(ms), "| rr max", max(rs), "| modulo rel", round(rel, 3))
ok &= res[42][0] >= 4 and res[42][2] <= 1 and res[4200][3] < res[420][3] < res[42][3]
# add one id (average over 100 namespaces, random-ish position by hash)
add_rr, add_mod, k_rr, k_mod, rem_rr = [], [], [], [], []
for j in range(100):
    base = ns(42, j); plus = base + ["extra-%d" % j]
    add_rr.append(moved(rr(base, K), rr(plus, K))); add_mod.append(moved(modulo(base, K), modulo(plus, K)))
    rem_rr.append(moved(rr(base, K), rr(base[:-1], K)))
    k_rr.append(moved(rr(base, 6), rr(base, 7))); k_mod.append(moved(modulo(base, 6), modulo(base, 7)))
m = statistics.mean
print("add one: rr %.3f mod %.3f | remove one: rr %.3f | K6->7: rr %.3f mod %.3f" % (m(add_rr), m(add_mod), m(rem_rr), m(k_rr), m(k_mod)))
ok &= 0.35 <= m(add_rr) <= 0.65 and m(add_mod) == 0 and m(k_rr) > .7 and m(k_mod) > .7
# order dependence
ids = ns(42, 0)
sorted_changes = sum(rr(ids, K)[i] != rr(ids[::-1], K)[i] for i in ids)
raw_changes = sum(rr_raw(ids, K)[i] != rr_raw(ids[::-1], K)[i] for i in ids)
print("reverse input: sorted rr changes", sorted_changes, "raw rr changes", raw_changes)
ok &= sorted_changes == 0 and raw_changes >= 30
# builtin hash across processes
code = "import sys;ids=['ns0-user-%d'%x for x in range(42)];print(','.join(str(hash(i)%6) for i in ids))"
outs = []
for seed in ("1", "2"):
    o = subprocess.run([sys.executable, "-c", code], env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True, text=True).stdout.strip().split(",")
    outs.append(o)
diff = sum(a != b for a, b in zip(*outs))
print("builtin str hash bucket differs across processes:", diff, "of 42")
ok &= diff >= 25
print("RESULT: %s modulo spread median %s (N=42) vs rr max %s; add-one moves rr %.2f mod %.2f; K6->7 rr %.2f mod %.2f; builtin hash differs %d/42" % (
    "PASS" if ok else "FAIL", res[42][0], res[42][2], m(add_rr), m(add_mod), m(k_rr), m(k_mod), diff))
