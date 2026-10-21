# Library call-number ordering: Dewey fractions and Cutter numbers are DECIMAL fractions, compared digit by digit.
# Compare three comparators against the reference (right-padded digit string). Deterministic, stdlib only.
import itertools
from functools import cmp_to_key

def split(cn):
    whole, _, frac = cn.partition('.')
    return int(whole), frac

def ref_key(cn):                       # reference: whole number, then fraction digits right-padded with 0 to equal length
    w, f = split(cn); return (w, f.rstrip('0'))   # '2' vs '20' equal; compare as strings below
def ref_cmp(a, b):
    (wa, fa), (wb, fb) = split(a), split(b)
    if wa != wb: return -1 if wa < wb else 1
    n = max(len(fa), len(fb)); fa, fb = fa.ljust(n, '0'), fb.ljust(n, '0')
    return (fa > fb) - (fa < fb)
def float_cmp(a, b):
    x, y = float(a), float(b); return (x > y) - (x < y)
def intfrac_cmp(a, b):                 # reads the fraction as an integer: .12 > .2
    (wa, fa), (wb, fb) = split(a), split(b)
    ka, kb = (wa, int(fa or 0)), (wb, int(fb or 0)); return (ka > kb) - (ka < kb)
def str_cmp(a, b):                     # plain string compare of the whole call number
    return (a > b) - (a < b)

def order(items, cmp): return sorted(items, key=cmp_to_key(cmp))
def is_weak_order(items, cmp):         # SORTING/comparator kernel: antisymmetry + transitivity on all triples
    for a, b in itertools.product(items, repeat=2):
        if cmp(a, b) != -cmp(b, a): return False
    for a, b, c in itertools.product(items, repeat=3):
        if cmp(a, b) <= 0 and cmp(b, c) <= 0 and cmp(a, c) > 0: return False
    return True

S1 = ['513.2', '513.12', '513.3', '513.1', '513.25', '513', '99.5', '513.02']      # Dewey-style, short
S2 = ['363.32517', '363.3252', '363.325', '363.3251']                              # five-place Dewey
S3 = ['.C9', '.C88', '.C8', '.C89', '.C90']                                        # Cutter-style (digits after the letter)
S3 = [x.replace('.C', '0.') for x in S3]                                           # model the digits as a fraction
S4 = ['513.12345678901234567', '513.12345678901234568', '513.1234567890123457']     # 17+ digit fractions: BREAK float
S5 = ['513.2', '513.20', '513.200']                                                 # trailing zeros must tie
cmps = {'float': float_cmp, 'intfrac': intfrac_cmp, 'string': str_cmp}
fails = {}
for name, S in [('dewey-short', S1), ('dewey-5place', S2), ('cutter', S3), ('long-fraction', S4), ('trailing-zero', S5)]:
    want = order(S, ref_cmp)
    for cn, cmp in cmps.items():
        got = order(S, cmp)
        same = [ref_cmp(a, b) for a, b in zip(got, want)]
        ok = all(v == 0 for v in same) and all(ref_cmp(got[i], got[i+1]) <= 0 for i in range(len(got)-1))
        fails[(name, cn)] = not ok
        print('%-14s %-8s %s' % (name, cn, 'OK  ' if ok else 'WRONG'), got if not ok else '')
tr = {cn: is_weak_order(S1 + S2, cmp) for cn, cmp in cmps.items()}
print('weak-order (transitive, antisymmetric) on S1+S2:', tr)
float_ties = [(a, b) for a, b in itertools.combinations(S4, 2) if float_cmp(a, b) == 0 and ref_cmp(a, b) != 0]
print('float ties on distinct long call numbers:', len(float_ties))
ok = (not any(fails[(n, 'float')] for n in ('dewey-short', 'dewey-5place', 'cutter', 'trailing-zero'))
      and len(float_ties) == 3
      and fails[('dewey-short', 'intfrac')] and fails[('cutter', 'intfrac')] and fails[('dewey-short', 'string')]
      and all(tr.values()))
print('RESULT: %s float matches the digit-string order on short fractions (0 wrong of 4 sets) but ties %d distinct 17+ digit numbers; int-fraction wrong on dewey-short and cutter; whole-string compare wrong on dewey-short only through 99.5 vs 513; all 3 comparators are valid weak orders so the bug is wrong order, not an invalid comparator'
      % ('PASS' if ok else 'FAIL', len(float_ties)))
