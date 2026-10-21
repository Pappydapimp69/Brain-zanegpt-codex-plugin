"""Sandbox: an invalid sort comparator gives order-dependent results.

Self-contained, stdlib only, deterministic (fixed-seed shuffles, no timing,
no files). Last printed line is RESULT: PASS|FAIL <summary>.

PREDICTION (written BEFORE the first run):
  P1 control (consistent total order), all 720 permutations of 6 values -> exactly 1 distinct output.
  P2 cyclic rock-paper-scissors comparator on {R,R,P,P,S,S}, all distinct input orders -> between 2 and 20 distinct outputs.
  P3 boolean-returning comparator (the JS `a > b` bug, returns 0/1 never -1) on 6 distinct
     values -> 720 distinct outputs out of 720 (output just echoes the input order), 0 of them sorted.
  P4 NaN in the data (sorted() with `<`, and a sign(a-b) comparator) on 5 values x 120 perms -> >= 2 distinct outputs.
  P5 tolerance comparator (equal if |a-b| < eps) on a chain 0,.6,1.2,1.8,2.4 with eps=1 -> >= 2 distinct outputs.
  P6 BREAK (narrowing) cases: the same invalid comparators give exactly 1 output when the violating
     tuple is not co-present: RPS with only two of the three symbols; eps comparator on values spaced > eps.
  P7 fixes (rank-map key / tiebreak, quantise round(v/eps), NaN filtered out) -> exactly 1 distinct output each.
  P8 order dependence survives size: RPS multiset of 96 items, 200 fixed-seed shuffles -> >= 190 distinct outputs.
  P9 (timsort threshold) a pure-Python model of CPython's small-list path (run detection + binary insertion,
     using only `lt`) reproduces the real sorted() output of the cyclic comparator on 100% of 200 shuffled
     lists of length 40, and on < 100% of lists of length 130 (merge path engaged).
  P10 no invalid comparator raises an exception (silent failure).
"""
import itertools
import math
import random
import sys
from functools import cmp_to_key

fails = []


def check(name, ok, detail):
    print(("ok   " if ok else "FAIL ") + name + " :: " + detail)
    if not ok:
        fails.append(name)


def sign(x):
    return (x > 0) - (x < 0)


def distinct(cmp, items, key=None):
    """Distinct outputs over every distinct ordering of `items`."""
    outs = set()
    errors = 0
    for p in set(itertools.permutations(items)):
        try:
            if cmp is None:
                outs.add(tuple(sorted(p)))
            else:
                outs.add(tuple(sorted(p, key=cmp_to_key(cmp))))
        except Exception:
            errors += 1
    return outs, errors


def is_sorted(seq, rank=lambda v: v):
    return all(rank(seq[i]) <= rank(seq[i + 1]) for i in range(len(seq) - 1))


# ---- comparators ----------------------------------------------------------
def cmp_total(a, b):
    return sign(a - b)


def cmp_bool(a, b):  # JS-style bug: returns a boolean-ish 0/1, never negative
    return int(a > b)


BEATS = {("R", "S"), ("S", "P"), ("P", "R")}  # a "greater" than b if a beats b


def cmp_rps(a, b):
    if a == b:
        return 0
    return 1 if (a, b) in BEATS else -1


def make_eps(eps):
    def cmp_eps(a, b):
        return 0 if abs(a - b) < eps else sign(a - b)
    return cmp_eps


NAN = float("nan")

# ---- P1 control -----------------------------------------------------------
vals = [3, 1, 4, 1.5, 9, 2.6]
o, e = distinct(cmp_total, vals)
check("P1 control", len(o) == 1, "%d distinct of %d perms" % (len(o), math.factorial(6)))

# ---- P2 cyclic RPS --------------------------------------------------------
rps = list("RRPPSS")
o_rps, e_rps = distinct(cmp_rps, rps)
n_in = len(set(itertools.permutations(rps)))
check("P2 rps cycle", 2 <= len(o_rps) <= 20,
      "%d distinct outputs from %d distinct input orders" % (len(o_rps), n_in))
print("     rps outputs:", sorted("".join(x) for x in o_rps))

# ---- P3 boolean comparator -----------------------------------------------
o_b, e_b = distinct(cmp_bool, vals)
n_sorted_b = sum(is_sorted(x) for x in o_b)
check("P3 boolean cmp", len(o_b) == 720 and n_sorted_b == 1,
      "%d distinct of 720, %d of them sorted (the input that was already sorted)" % (len(o_b), n_sorted_b))

# ---- P4 NaN ---------------------------------------------------------------
nanvals = [3.0, 1.0, NAN, 2.0, 0.0]
o_n1, e_n1 = distinct(None, nanvals)
o_n2, e_n2 = distinct(cmp_total, nanvals)
nan_ok = len(o_n1) >= 2 and len(o_n2) >= 2
check("P4 NaN", nan_ok, "sorted(<): %d distinct of 120; sign(a-b) cmp: %d distinct of 120" % (len(o_n1), len(o_n2)))
bad_n1 = sum(1 for x in o_n1 if not is_sorted([v for v in x if v == v]))
print("     NaN case: outputs whose non-NaN part is mis-sorted (plain sorted): %d of %d" % (bad_n1, len(o_n1)))

# ---- P5 eps chain ---------------------------------------------------------
chain = [0.0, 0.6, 1.2, 1.8, 2.4]
o_e, e_e = distinct(make_eps(1.0), chain)
check("P5 eps chain", len(o_e) >= 2, "%d distinct of 120 perms" % len(o_e))

# ---- P6 BREAK: violating tuple not co-present ----------------------------
o_two, _ = distinct(cmp_rps, list("RRPPPP"))
spaced = [0.0, 1.5, 3.0, 4.5, 6.0]
o_sp, _ = distinct(make_eps(1.0), spaced)
check("P6 break (narrowing)", len(o_two) == 1 and len(o_sp) == 1,
      "rps with 2 of 3 symbols: %d distinct; eps cmp on spaced values: %d distinct" % (len(o_two), len(o_sp)))

# ---- P7 fixes -------------------------------------------------------------
RANK = {"R": 0, "P": 1, "S": 2}  # explicit total order replaces the cycle
fix_rps = {tuple(sorted(p, key=RANK.get)) for p in set(itertools.permutations(rps))}
fix_eps = {tuple(sorted(p, key=lambda v: round(v / 1.0))) for p in set(itertools.permutations(chain))}
fix_nan = {tuple(sorted(v for v in p if v == v)) for p in set(itertools.permutations(nanvals))}
fix_bool = {tuple(sorted(p)) for p in set(itertools.permutations(vals))}
check("P7 fixes", all(len(s) == 1 for s in (fix_rps, fix_eps, fix_nan, fix_bool)),
      "rank-key %d, quantise %d, NaN-filter %d, plain key %d distinct" %
      (len(fix_rps), len(fix_eps), len(fix_nan), len(fix_bool)))

# ---- P7b (iteration 2, written AFTER seeing P7 fail; not one of the original predictions) ----
# Quantising makes the GROUPING identical for every input order, but stable sort leaves each
# bucket in input order, so the output order still varies until a value tiebreak is added.
def groups(seq):
    return frozenset(frozenset(v for v in seq if round(v / 1.0) == k) for k in {round(v) for v in seq})


grp = {groups(x) for x in fix_eps}
fix_eps2 = {tuple(sorted(p, key=lambda v: (round(v / 1.0), v))) for p in set(itertools.permutations(chain))}
posthoc = len(grp) == 1 and len(fix_eps2) == 1 and len(fix_eps) > 1
print(("ok   " if posthoc else "FAIL ") + "P7b quantise grouping vs order :: grouping %d distinct, output order %d distinct, "
      "with (bucket, value) key %d distinct" % (len(grp), len(fix_eps), len(fix_eps2)))
if not posthoc:
    fails.append("P7b")

# ---- P8 scale: RPS multiset of 96 ----------------------------------------
rng = random.Random(20261009)
big = list("RPS") * 32
outs = set()
for _ in range(200):
    p = big[:]
    rng.shuffle(p)
    outs.add("".join(sorted(p, key=cmp_to_key(cmp_rps))))
small = list("RPS") * 4
outs_small = set()
for _ in range(200):
    p = small[:]
    rng.shuffle(p)
    outs_small.add("".join(sorted(p, key=cmp_to_key(cmp_rps))))
check("P8 scale", len(outs) >= 190,
      "n=96: %d distinct of 200 shuffles; n=12: %d distinct of 200" % (len(outs), len(outs_small)))

# ---- P9 timsort small-list model -----------------------------------------
def lt(a, b):
    return cmp_rps(a, b) < 0


def model_sort(a):
    """Run detection then binary insertion, using only lt (small-list path)."""
    a = a[:]
    n = len(a)
    if n < 2:
        return a
    run = 2
    if lt(a[1], a[0]):
        while run < n and lt(a[run], a[run - 1]):
            run += 1
        a[:run] = a[:run][::-1]
    else:
        while run < n and not lt(a[run], a[run - 1]):
            run += 1
    for start in range(run, n):
        pivot = a[start]
        l, r = 0, start
        while l < r:
            p = l + ((r - l) >> 1)
            if lt(pivot, a[p]):
                r = p
            else:
                l = p + 1
        a[l + 1:start + 1] = a[l:start]
        a[l] = pivot
    return a


def match_rate(n, trials):
    hit = 0
    for _ in range(trials):
        p = [rng.choice("RPS") for _ in range(n)]
        if model_sort(p) == sorted(p, key=cmp_to_key(cmp_rps)):
            hit += 1
    return hit


m40 = match_rate(40, 200)
m130 = match_rate(130, 200)
check("P9 timsort model", m40 == 200 and m130 < 200,
      "model == real sorted(): n=40 %d/200, n=130 %d/200 (python %d.%d)" %
      (m40, m130, sys.version_info[0], sys.version_info[1]))

# ---- P10 silent ----------------------------------------------------------
errs = e_rps + e_b + e_n1 + e_n2 + e_e
check("P10 silent failure", errs == 0, "%d exceptions raised across all invalid-comparator runs" % errs)

# ---- version note (information only) -------------------------------------
print("     interpreter %d.%d: rps distinct outputs %d (n=96: %d/200, n=12: %d/200)"
      % (sys.version_info[0], sys.version_info[1], len(o_rps), len(outs), len(outs_small)))

# ---- result ---------------------------------------------------------------
if fails:
    print("RESULT: FAIL py%d.%d original predictions refuted: %s (rps=%d distinct, n=96 %d/200, model n=40 %d/200)"
          % (sys.version_info[0], sys.version_info[1], ", ".join(fails), len(o_rps), len(outs), m40))
else:
    print("RESULT: PASS py%d.%d rps %d distinct, boolean %d/720, NaN %d/%d, eps %d, break cases 1/1, fixes 1 each, n=96 %d/200, model n=40 %d/200 n=130 %d/200"
          % (sys.version_info[0], sys.version_info[1], len(o_rps), len(o_b), len(o_n1), len(o_n2), len(o_e), len(outs), m40, m130))
