"""Toy pin-tumbler lock: n pins, d depths, MACS = maximum adjacent cut difference.
Counts usable keyings by DP, then attacks by (a) exhaustive guess and (b) binding-order pin-by-pin
picking (feedback: one pin binds at a time, so each pin is solved alone). Security pins give a
false set that costs extra probes per pin. Deterministic; parameters are generic, not a vendor's."""
from itertools import product
def keyings_bruteforce(n, d, macs):
    return sum(1 for k in product(range(d), repeat=n) if all(abs(k[i]-k[i+1]) <= macs for i in range(n-1)))
def keyings_dp(n, d, macs):
    cur = [1]*d
    for _ in range(n-1):
        cur = [sum(cur[j] for j in range(d) if abs(i-j) <= macs) for i in range(d)]
    return sum(cur)
def exhaustive_worst(n, d, macs): return keyings_dp(n, d, macs)          # guesses to try all keyings
def binding_order_worst(n, d, false_sets=0):
    # each pin solved alone: try each depth (d), plus `false_sets` extra probes per pin to clear false feedback
    return n*(d + false_sets)
rows = []
cases = [("5 pins x 6 depths, MACS 7 (no limit)", 5, 6, 7, 0),
         ("5 pins x 10 depths, MACS 7", 5, 10, 7, 0),
         ("5 pins x 10 depths, MACS 3", 5, 10, 3, 0),
         ("BREAK: 5 pins x 10 depths, MACS 7, security pins (3 false sets/pin)", 5, 10, 7, 3),
         ("6 pins x 10 depths, MACS 7", 6, 10, 7, 0)]
okdp = True
for name, n, d, macs, fs in cases:
    dp = keyings_dp(n, d, macs)
    if d**n <= 1_000_000: okdp &= (dp == keyings_bruteforce(n, d, macs))
    ex, bo = exhaustive_worst(n, d, macs), binding_order_worst(n, d, fs)
    rows.append((name, d**n, dp, ex, bo))
    print(f"{name}: d^n={d**n}, usable={dp} ({100*dp/d**n:.1f}%), exhaustive worst {ex}, binding-order worst {bo}, ratio {ex/bo:.0f}x")
# 5-digit secret with an early-exit compare (position-by-position feedback), like a plain-verifier leak
code = "40817"
def early_exit_attack(secret):
    probes, known = 0, ""
    for pos in range(len(secret)):
        for dgt in "0123456789":
            probes += 1
            if secret[pos] == dgt: known += dgt; break
    return probes, known
probes, known = early_exit_attack(code)
exh_worst = 10**len(code)
print(f"5-digit secret, early-exit compare: recovered {known} in {probes} probes vs exhaustive worst {exh_worst}")
# time to finish at a guess rate: fast hash vs deliberately slow hash (parameters, not measurements)
for label, rate in (("fast hash 1e9/s", 1e9), ("slow hash 10/s", 10.0)):
    print(f"{label}: exhaustive {exh_worst/rate:.6g} s; early-exit oracle {probes/rate:.6g} s")
okE = known == code and probes < 60 and exh_worst/10.0 > 1000*probes/10.0
ok = okE and okdp and rows[2][2] < rows[1][2] and rows[1][4] == 50 and rows[3][4] == 65 and rows[3][3] / rows[3][4] > 1000 and rows[4][3]/rows[4][4] > rows[1][3]/rows[1][4]
print("RESULT: PASS" if ok else "RESULT: FAIL", f"DP matches brute force={okdp}; 5x10 MACS7 usable {rows[1][2]} vs binding-order {rows[1][4]} probes; security pins raise it to {rows[3][4]} (still {rows[3][3]/rows[3][4]:.0f}x below exhaustive)")
