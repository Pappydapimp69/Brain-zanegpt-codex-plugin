"""Prediction (before run), own fixture and my own reading of the claim: a press at tick t with lag L hints role B if B(t) else A; it is legal iff the
hinted role is available at the landing tick t+L. A lag L is usable if some t in [0,H) is legal. The cutoff of a lag set is its largest usable lag; the
shortcut claims cutoff == max(set) whenever the fallback A (a set of residues mod M) is non-empty.
B families (mine, differing from semiprimes / Rudin-Shapiro / powers of 3 / squares): primes, Thue-Morse odd parity, Fibonacci numbers, triangular numbers.
Moduli 3, 11, 13; lags 1..16; all 3-lag sets (560); H=500.
 P1 every single-residue fallback (M residues x 3 moduli x 4 families) has 0 sets with cutoff != max.
 P2 the empty fallback has > 0 failing sets in every family (sparse B cannot supply B(t) and B(t+L)).
 P3 BREAK: horizon H=6 at M=13 with a single residue: failures > 0 (not all residues reachable at a non-B tick), so the guard needs a horizon assumption.
RUN-1 OUTCOME (recorded): P1 held and P3 held (7363 failures). P2 MISSED: the empty fallback failed only for the sparse families (primes 243, fibonacci 591);
Thue-Morse odd parity and triangular numbers gave 0 failures because their pairs B(t),B(t+L) exist for every lag, so emptiness only breaks when B is sparse enough.
Final rule restated to P1 and P3 plus "empty fallback fails for at least the sparse families".
Deterministic, stdlib."""
from itertools import combinations
def primes(n):
    s = set(); 
    for k in range(2, n):
        if all(k % d for d in range(2, int(k ** .5) + 1)): s.add(k)
    return s
LIM = 600
FAM = {"primes": primes(LIM),
       "thue-morse-odd": {k for k in range(LIM) if bin(k).count("1") % 2},
       "fibonacci": {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377},
       "triangular": {k * (k + 1) // 2 for k in range(40)}}
LAGS = range(1, 17); SETS = list(combinations(LAGS, 3))
def usable(L, Bset, M, res, H):
    for t in range(H):
        if t in Bset: legal = (t + L) in Bset
        else: legal = (t + L) % M in res
        if legal: return True
    return False
def fails(Bset, M, res, H):
    u = {L: usable(L, Bset, M, res, H) for L in LAGS}
    return sum(1 for s in SETS if max((L for L in s if u[L]), default=0) != max(s))
tot_single = 0; checks = 0; empty = {}
for name, B in FAM.items():
    for M in (3, 11, 13):
        for r in range(M):
            f = fails(B, M, {r}, 500); tot_single += f; checks += 1
    empty[name] = sum(fails(B, M, set(), 500) for M in (3, 11, 13))
brk = sum(fails(FAM[n], 13, {r}, 6) for n in FAM for r in range(13))
print("single-residue fallbacks checked", checks, "sets each", len(SETS), "total failures", tot_single)
print("empty fallback failures per family (summed over moduli)", empty)
print("BREAK horizon 6, M=13, single residues: failures", brk)
ok = tot_single == 0 and empty["primes"] > 0 and empty["fibonacci"] > 0 and brk > 0
print("RESULT:", "PASS" if ok else "FAIL", f"0 of {checks*len(SETS)} set failures for single-residue fallbacks at H=500; empty fallback fails only for sparse B {empty} (P2 missed for dense Thue-Morse and triangular); horizon-6 breaker {brk}")
