"""Sandbox: pin-tumbler key space vs a maximum-adjacent-cut (MACS) rule. Deterministic, stdlib only.
Parameters are ILLUSTRATIVE (pins, depths, MACS), not a specific product. A key is a tuple of cut depths 0..D-1;
valid if every adjacent pair differs by at most MACS (a cut too steep between neighbours would not physically fit)."""
import itertools
def count_brute(pins, depths, macs):
    return sum(1 for k in itertools.product(range(depths), repeat=pins)
               if all(abs(k[i] - k[i + 1]) <= macs for i in range(pins - 1)))
def count_dp(pins, depths, macs):          # independent method: transfer counting
    ways = [1] * depths
    for _ in range(pins - 1):
        ways = [sum(ways[j] for j in range(depths) if abs(i - j) <= macs) for i in range(depths)]
    return sum(ways)
rows = []
for pins, depths in ((5, 6), (5, 10), (6, 10)):
    nominal = depths ** pins
    for macs in (depths - 1, 7, 4, 2):
        b = count_brute(pins, depths, macs) if nominal <= 1_000_000 else None
        d = count_dp(pins, depths, macs)
        assert b is None or b == d, (pins, depths, macs, b, d)
        rows.append((pins, depths, macs, nominal, d))
        print(f"pins={pins} depths={depths} macs={macs} nominal={nominal} valid={d} ({d/nominal:.1%})")
# break: with macs >= depths-1 nothing is excluded; keys are not equally likely to be used (duplicate bitting) - not modeled
full = [r for r in rows if r[2] == r[1] - 1]
cut = [r for r in rows if r[2] == 2]
ok = all(r[4] == r[3] for r in full) and all(r[4] < r[3] for r in cut)
ok = ok and next(r for r in rows if r[:3] == (5, 10, 4))[4] < next(r for r in rows if r[:3] == (5, 10, 7))[4]
r510 = next(r for r in rows if r[:3] == (5, 10, 4))
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" nominal 5-pin 10-depth space 100000 shrinks to {r510[4]} at macs 4 and to {next(r for r in rows if r[:3]==(5,10,2))[4]} at macs 2; brute force equals transfer count")
