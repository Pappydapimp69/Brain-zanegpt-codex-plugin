"""Round-robin dealing vs hash-modulo assignment: balance, stability, determinism.

Kernel under test: ideas:algorithm/content/deal-round-robin-not-hash-modulo

PREDICTION (written BEFORE the first run; any item could come out wrong):
  P1 balance, N=42 ids into K=6 buckets, 200 id-namespaces (salts):
     hash-modulo: median (max-min) count spread >= 5 and worst salt >= 9
                  (perfect would be 7 each, spread 0);
     round-robin over hash-sorted ids: spread <= 1 in 200/200 salts (exactly 0
     here, since 42 % 6 == 0).
  P2 scale: median (max-min)/mean for hash-modulo is >= 0.6 at N=42, between
     0.2 and 0.45 at N=420, and < 0.15 at N=4200; round-robin stays <= 1 count.
     ("large enough" is far more than forty.)
  P3 stability, add ONE id to the population (N=42 -> 43): hash-modulo moves
     0 of the 42 existing ids; round-robin moves on average 35%-65% of them
     (everything sorted after the insertion point shifts bucket).
     Remove ONE id: same split.
  P4 stability, bucket count K=6 -> 7: both schemes move more than 70% of ids
     (round-robin buys balance, not stability; modulo has no edge here).
  P5 determinism: same ids, permuted input order -> identical assignment for
     both schemes when the hash key is wide (sha256-derived) and ties are broken
     by id.  Negative controls: (a) round-robin over the raw input order is NOT
     permutation-invariant (>= 30 of 42 ids change bucket under a reversal);
     (b) a narrow 6-bit hash key with NO tie-break makes the sort-then-deal
     input-order dependent (some ids change bucket under a shuffle);
     (c) Python's built-in str hash() modulo differs between two
     PYTHONHASHSEED values (>= 20 of 42 ids differ) while sha256 does not.
  P6 checker validity: a constant bucket function must be flagged unbalanced
     by the same balance metric (spread == 42).
RESULT is PASS only if every prediction above holds.
"""
import hashlib
import subprocess
import sys

K0 = 6
N0 = 42


def h(s):
    """Wide, process-independent content hash (sha256 -> int)."""
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def ids(salt, n):
    return ["%d:id%d" % (salt, i) for i in range(n)]


def deal_modulo(population, k):
    return {x: h(x) % k for x in population}


def deal_rr(population, k, key=h, tiebreak=True):
    order = sorted(population, key=(lambda x: (key(x), x)) if tiebreak else key)
    return {x: i % k for i, x in enumerate(order)}


def counts(assign, k):
    c = [0] * k
    for b in assign.values():
        c[b] += 1
    return c


def spread(assign, k):
    c = counts(assign, k)
    return max(c) - min(c)


def median(v):
    v = sorted(v)
    return v[len(v) // 2]


def moved(a, b):
    common = [x for x in a if x in b]
    return sum(1 for x in common if a[x] != b[x]), len(common)


def fixed_permutation(pop):
    return sorted(pop, key=lambda s: hashlib.md5(s.encode()).hexdigest())


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print("%-4s %s | %s" % ("ok" if ok else "FAIL", name, detail))


# ---- P1 balance at N=42, K=6 over 200 namespaces
mod_sp, rr_sp = [], []
for salt in range(200):
    pop = ids(salt, N0)
    mod_sp.append(spread(deal_modulo(pop, K0), K0))
    rr_sp.append(spread(deal_rr(pop, K0), K0))
check("P1 balance N=42 K=6",
      median(mod_sp) >= 5 and max(mod_sp) >= 9 and max(rr_sp) <= 1,
      "modulo spread median=%d worst=%d | round-robin worst=%d (200 salts)"
      % (median(mod_sp), max(mod_sp), max(rr_sp)))

# ---- P2 scale sweep
rel = {}
rr_worst = 0
for n in (42, 420, 4200):
    r = []
    for salt in range(100):
        pop = ids(salt, n)
        r.append(spread(deal_modulo(pop, K0), K0) / (n / K0))
        rr_worst = max(rr_worst, spread(deal_rr(pop, K0), K0))
    rel[n] = median(r)
check("P2 scale sweep",
      rel[42] >= 0.6 and 0.2 <= rel[420] <= 0.45 and rel[4200] < 0.15 and rr_worst <= 1,
      "modulo median (max-min)/mean N=42:%.2f N=420:%.2f N=4200:%.2f | rr worst spread=%d"
      % (rel[42], rel[420], rel[4200], rr_worst))

# ---- P3 stability on add / remove one id
acc = {"mod_add": 0.0, "rr_add": 0.0, "mod_rem": 0.0, "rr_rem": 0.0}
TRIALS = 100
for salt in range(TRIALS):
    pop = ids(salt, N0)
    plus = pop + ["%d:extra" % salt]
    minus = pop[1:]
    for tag, fn in (("mod", deal_modulo), ("rr", deal_rr)):
        base = fn(pop, K0)
        m, c = moved(base, fn(plus, K0))
        acc[tag + "_add"] += m / c
        m, c = moved(base, fn(minus, K0))
        acc[tag + "_rem"] += m / c
for k in acc:
    acc[k] /= TRIALS
check("P3 add/remove one id",
      acc["mod_add"] == 0 and acc["mod_rem"] == 0
      and 0.35 <= acc["rr_add"] <= 0.65 and 0.35 <= acc["rr_rem"] <= 0.65,
      "moved fraction add: modulo=%.3f rr=%.3f | remove: modulo=%.3f rr=%.3f"
      % (acc["mod_add"], acc["rr_add"], acc["mod_rem"], acc["rr_rem"]))

# ---- P4 bucket count 6 -> 7
mm = rm = 0.0
for salt in range(100):
    pop = ids(salt, N0)
    a, c = moved(deal_modulo(pop, 6), deal_modulo(pop, 7))
    mm += a / c
    a, c = moved(deal_rr(pop, 6), deal_rr(pop, 7))
    rm += a / c
mm /= 100
rm /= 100
check("P4 K 6->7 stability", mm > 0.70 and rm > 0.70,
      "moved fraction modulo=%.3f rr=%.3f" % (mm, rm))

# ---- P5 determinism and negative controls
pop = ids(7, N0)
rev = list(reversed(pop))
shuf = fixed_permutation(pop)
same_mod = deal_modulo(pop, K0) == deal_modulo(rev, K0)
same_rr = deal_rr(pop, K0) == deal_rr(shuf, K0) and deal_rr(pop, K0) == deal_rr(rev, K0)


def rr_input_order(population, k):
    return {x: i % k for i, x in enumerate(population)}


raw_changed = sum(1 for x in pop if rr_input_order(pop, K0)[x] != rr_input_order(rev, K0)[x])


def narrow(s):
    return h(s) % 64


narrow_diff = 0
for salt in range(20):
    p = ids(salt, N0)
    q = fixed_permutation(p)
    a = deal_rr(p, K0, key=narrow, tiebreak=False)
    b = deal_rr(q, K0, key=narrow, tiebreak=False)
    narrow_diff += sum(1 for x in p if a[x] != b[x])

CHILD = ("ids=['7:id%d' % i for i in range(42)]\n"
         "print([hash(x) % 6 for x in ids])\n")
outs = []
for seed in ("1", "2"):
    # fixed seeds; no -I flag, because isolated mode would drop PYTHONHASHSEED
    r = subprocess.run([sys.executable, "-c", CHILD], capture_output=True,
                       text=True, env={"PYTHONHASHSEED": seed})
    outs.append(r.stdout.strip())
a_list, b_list = eval(outs[0]), eval(outs[1])
builtin_diff = sum(1 for x, y in zip(a_list, b_list) if x != y)
check("P5a content-addressed deal ignores input order", same_mod and same_rr,
      "modulo reversed-equal=%s rr shuffled+reversed-equal=%s" % (same_mod, same_rr))
check("P5b NEG raw-order round-robin is order dependent", raw_changed >= 30,
      "%d of 42 ids changed bucket under reversal" % raw_changed)
check("P5c NEG narrow key without tie-break is order dependent", narrow_diff > 0,
      "%d id-bucket changes over 20 shuffled populations" % narrow_diff)
check("P5d NEG built-in str hash differs by process seed", builtin_diff >= 20,
      "%d of 42 ids differ between two PYTHONHASHSEED values" % builtin_diff)

# ---- P6 checker validity: constant bucket must be flagged
const = {x: 0 for x in ids(0, N0)}
check("P6 checker flags a constant deal", spread(const, K0) == N0,
      "constant-bucket spread=%d" % spread(const, K0))

ok = all(checks)
print("RESULT: %s round-robin spread<=1 in 200/200 vs modulo median %d worst %d at N=42; "
      "add-one moves modulo %.0f%% vs rr %.0f%%; K 6->7 moves %.0f%%/%.0f%%; %d/%d checks"
      % ("PASS" if ok else "FAIL", median(mod_sp), max(mod_sp), acc["mod_add"] * 100,
         acc["rr_add"] * 100, mm * 100, rm * 100, sum(checks), len(checks)))
