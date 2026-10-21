"""NUMERAL-SYSTEMS/additive-subtractive kernel: the plain sum-and-subtract parse gives one
value many spellings; 'decode then re-encode and compare' is the canonical rule. Boundary:
real inscriptions use non-canonical but MEANINGFUL forms. Test a fixed list of attested
variant spellings with their intended values: clock-face IIII (4), XIIII (14), additive
VIIII (9), MDCCCC (1900), medieval IIX (8) and XIIX (18), IC (99), IIC (98), XM (990).
For each: the plain parse's value, and whether the canonical rule accepts it.
PREDICTION (written before running): the canonical rule rejects all 9 variants; the plain
parse returns the intended value for every purely additive form (IIII, XIIII, VIIII,
MDCCCC, 4 of 9) and for IC and XM, but misreads the double-subtractive forms IIX, XIIX and
IIC (3 of 9 wrong values, silently)."""
V = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
def parse(s):                 # plain: subtract a symbol smaller than its right neighbour
    t = 0
    for i, ch in enumerate(s):
        v = V[ch]
        t += -v if i + 1 < len(s) and V[s[i + 1]] > v else v
    return t
def encode(n):
    out = []
    for v, sym in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                   (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v: out.append(sym); n -= v
    return "".join(out)
VARIANTS = [("IIII", 4), ("XIIII", 14), ("VIIII", 9), ("MDCCCC", 1900), ("IIX", 8), ("XIIX", 18), ("IC", 99), ("IIC", 98), ("XM", 990)]
wrong, rejected = [], 0
for s, intended in VARIANTS:
    p = parse(s); canon = encode(p) == s
    rejected += not canon
    if p != intended: wrong.append((s, intended, p))
    print(f"{s:7s} intended {intended:5d}  plain parse {p:5d} {'OK ' if p == intended else 'WRONG'}  canonical rule: {'accept' if canon else 'reject'} (canonical {encode(intended)})")
ok = rejected == 9 and sorted(w[0] for w in wrong) == sorted(["IIX", "XIIX", "IIC"])
print(f"RESULT: {'PASS' if ok else 'FAIL'} canonical rule rejects {rejected}/9 attested variants; plain parse silently misreads "
      f"{len(wrong)}/9: " + ", ".join(f"{s} as {p} (meant {i})" for s, i, p in wrong))
