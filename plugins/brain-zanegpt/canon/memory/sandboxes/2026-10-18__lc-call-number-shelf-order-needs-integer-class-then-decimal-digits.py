# Domain seed LIBRARY-SHELVING. Rule modelled (Library of Congress classification as I know it, not re-fetched):
# a call number is LETTERS + INTEGER class number + optional decimal fraction (QA76.73 shelves before QA76.9
# because .73 < .9 as a decimal), compared as (letters, integer, decimal fraction).
# Prediction (before running): over all pairs from 100 deterministic call numbers, (a) plain string sort mis-orders pairs
# ONLY when the integer parts differ in digit count (QA9 vs QA76) and never otherwise; (b) a "split on the dot and compare
# both sides as integers" sort mis-orders pairs ONLY when the two decimal parts differ in digit count (.9 vs .73);
# (c) the tuple (letters, int, decimal string padded right with zeros) has 0 mis-orders against an exact Fraction reference.
# Built to break (c): decimals that differ only by trailing digits (.7 vs .70 vs .700) must compare equal, not be ordered.
from fractions import Fraction
from itertools import combinations
import random
r = random.Random(7)
nums = set()
while len(nums) < 100:
    L = r.choice(["QA", "QB", "Z", "HF"]); i = r.choice([1, 9, 76, 100, 5000, 5415])
    d = r.choice([None, "9", "73", "7", "35", "135", "5"])
    nums.add((L, i, d))
nums = sorted(nums, key=lambda c: (c[0], c[1], c[2] or ""))
def ref(c): return (c[0], c[1], Fraction(0) if c[2] is None else Fraction(int(c[2]), 10 ** len(c[2])))
def s(c): return c[0] + str(c[1]) + ("." + c[2] if c[2] else "")
def str_key(c): return s(c)
def int_key(c): return (c[0], c[1], int(c[2]) if c[2] else -1)
def tup_key(c): return (c[0], c[1], (c[2] or "").ljust(6, "0"))
def mis(key, pred):
    n = 0; bad_other = 0
    for a, b in combinations(nums, 2):
        ra, rb = ref(a), ref(b)
        if ra == rb: continue
        wrong = (key(a) < key(b)) != (ra < rb)
        if wrong:
            n += 1
            if not pred(a, b): bad_other += 1
    return n, bad_other
width_int = lambda a, b: len(str(a[1])) != len(str(b[1])) or a[0] != b[0] and True
width_dec = lambda a, b: a[0] == b[0] and a[1] == b[1] and len(a[2] or "") != len(b[2] or "")
n_s, o_s = mis(str_key, lambda a, b: len(str(a[1])) != len(str(b[1])) or (a[0] != b[0] and len(a[0]) != len(b[0])))
n_i, o_i = mis(int_key, width_dec)
n_t, o_t = mis(tup_key, lambda a, b: True)
print("string sort mis-ordered pairs", n_s, "outside integer-width cases", o_s)
print("int-split sort mis-ordered pairs", n_i, "outside decimal-width cases", o_i)
print("tuple sort mis-ordered pairs", n_t)
t = [("QA", 76, "7"), ("QA", 76, "70"), ("QA", 76, "700")]
eq = len({ref(c) for c in t}) == 1 and len({tup_key(c) for c in t}) == 1
print("trailing zeros compare equal under tuple key", eq)
ok = n_s > 0 and o_s == 0 and n_i > 0 and o_i == 0 and n_t == 0 and eq
print("RESULT: %s string sort wrong on %d pairs (all integer-width), int-split wrong on %d pairs (all decimal-width), padded tuple key wrong on %d of %d pairs, trailing zeros equal %s" % ("PASS" if ok else "FAIL", n_s, n_i, n_t, len(nums) * (len(nums) - 1) // 2, eq))
