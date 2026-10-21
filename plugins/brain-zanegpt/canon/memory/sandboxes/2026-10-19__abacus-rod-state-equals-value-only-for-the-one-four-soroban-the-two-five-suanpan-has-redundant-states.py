"""Prediction (before run): a 1+4 soroban rod (one heavenly bead =5, four earthly =1) has 2*5=10 states
mapping one-to-one onto values 0-9. A 2+5 suanpan rod (two heavenly =5, five earthly =1) has 3*6=18
states covering values 0-15 (16 values), so exactly 2 values (5 and 10) have two states each and state
equality is not value equality on 2 state pairs. Sum check: the digit sequence 7,8,9,6 is added rod by
rod as raw values; reading the suanpan by value gives 30 while a state-compare of two spellings of 5 differs."""
from collections import defaultdict
def states(h, e): return [(a, b) for a in range(h + 1) for b in range(e + 1)]
val = lambda s: 5 * s[0] + s[1]
def table(h, e):
    t = defaultdict(list)
    for s in states(h, e): t[val(s)].append(s)
    return t
sor, sua = table(1, 4), table(2, 5)
sor_multi = sorted(v for v, l in sor.items() if len(l) > 1)
sua_multi = sorted(v for v, l in sua.items() if len(l) > 1)
pairs = sum(len(l) * (len(l) - 1) // 2 for l in sua.values())
# BREAK: two spellings of 5 on a suanpan rod are equal in value, unequal as states
five = sua[5]; same_value = val(five[0]) == val(five[1]); same_state = five[0] == five[1]
# soroban: every digit has a unique spelling, so state compare == value compare for all 10x10 pairs
sor_ok = all((a == b) == (val(a) == val(b)) for a in states(1, 4) for b in states(1, 4))
sua_ok = all((a == b) == (val(a) == val(b)) for a in states(2, 5) for b in states(2, 5))
print(len(states(1, 4)), len(sor), sor_multi, len(states(2, 5)), len(sua), sua_multi, pairs, five, sor_ok, sua_ok)
ok = (len(states(1, 4)) == 10 and len(sor) == 10 and not sor_multi and len(states(2, 5)) == 18
      and len(sua) == 16 and sua_multi == [5, 10] and pairs == 2 and same_value and not same_state
      and sor_ok and not sua_ok)
print(("RESULT: PASS " if ok else "RESULT: FAIL ") +
      f"soroban 10 states/10 values, state==value on all pairs {sor_ok}; suanpan 18 states/16 values, redundant values {sua_multi}, spellings of 5 {five} equal in value not in state, state==value {sua_ok}")
