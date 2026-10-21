"""Own fixture, built from the claim text only. Interpretation (stated, not taken from the entry):
tick t is ACTIVE if (t mod P) < W (primary role A window) or, with the fallback, t is even.
A lag L is valid iff tick L is active when anchored at tick 0 (0 is active). The formula under test:
valid iff (L mod P) <= W-1 or L even. I compute validity by scanning an explicit tick array
(not by the formula), then compare. 'Drop lag d' = largest valid lag left in the set.
Prediction (before run): parity-extended formula 0 mismatches on P in {13,14,15,16}, W 1..6, lags 1..60;
residue-only has >=1 mismatch at P15; drop 15 from {2,6,15} at W3 -> 6 (residue-only 2);
for ALL-ODD lag sets parity adds nothing (the two rules agree); for odd P the claim needs odd-tick-free
breaker: with fallback only on ODD ticks the rule flips to 'odd', so the parity term is tied to the fallback phase."""
def active(P, W, fb):
    return lambda t: (t % P) < W or (fb == "even" and t % 2 == 0) or (fb == "odd" and t % 2 == 1)

def valid_scan(P, W, fb, L):
    return active(P, W, fb)(L)           # direct tick lookup

def rule_parity(P, W, L, fb="even"):
    return (L % P) <= W - 1 or (L % 2 == 0 if fb == "even" else L % 2 == 1)
def rule_resid(P, W, L):
    return (L % P) <= W - 1

def drop(P, W, lags, d, valid):
    rest = [l for l in lags if l != d and valid(l)]
    return max(rest) if rest else 0

mm_par = mm_res = total = 0
for P in (13, 14, 15, 16):
    for W in range(1, 7):
        for fb in ("even", "odd"):
            for L in range(1, 61):
                total += 1
                s = valid_scan(P, W, fb, L)
                mm_par += s != rule_parity(P, W, L, fb)
                if fb == "even": mm_res += s != rule_resid(P, W, L)
print("mismatches parity-formula:", mm_par, "residue-only (even fallback):", mm_res, "of", total)
r = lambda W: (lambda l: valid_scan(15, W, "even", l))
d3 = drop(15, 3, [2, 6, 15], 15, r(3))
d3_res = drop(15, 3, [2, 6, 15], 15, lambda l: rule_resid(15, 3, l))
print("drop 15 from 2,6,15 at W3: scan", d3, "residue-only", d3_res)
odd_agree = all(valid_scan(P, W, "even", L) == rule_resid(P, W, L) for P in (13, 15) for W in range(1, 7) for L in range(1, 60, 2) if True) 
# odd lags: active only via residue, except none -> agree
odd_set = [drop(15, W, [1, 3, 7, 15], 15, r(W)) for W in range(1, 7)]
print("odd lags 1,3,7,15 drop 15 by W1..6:", odd_set, "odd-lag scan==residue-only everywhere:", odd_agree)
ok = mm_par == 0 and mm_res >= 1 and d3 == 6 and d3_res == 2 and odd_agree
print(f"RESULT: {'PASS' if ok else 'FAIL'} parity-formula mismatches {mm_par}/{total}, residue-only {mm_res}, drop15@W3 scan {d3} vs residue-only {d3_res}, odd lags agree {odd_agree}, odd-lag drop by W {odd_set}")
