# Sandbox: Beaufort number from the published formula v = 1.625 B^(3/2) knots vs the published knot-band table.
LO = [0, 1, 4, 7, 11, 17, 22, 28, 34, 41, 48, 56, 64]   # lower knot bound of bands 0..12 (Wikipedia table)
def table(kn):
    return max(b for b, lo in enumerate(LO) if kn >= lo)
def formula_round(kn):  # invert v=1.625*B^1.5, round to nearest B, cap 12
    return min(12, round((kn / 1.625) ** (2 / 3)))
def formula_mid(kn):    # band boundaries at midpoints of consecutive formula speeds
    best = 0
    for b in range(13):
        if kn >= 1.625 * max(b - .5, 0) ** 1.5: best = b
    return best
speeds = range(0, 71)
for name, f in (("round", formula_round), ("midpoint", formula_mid)):
    miss = [k for k in speeds if f(k) != table(k)]
    off2 = [k for k in miss if abs(f(k) - table(k)) > 1]
    print(name, "agree %d/%d" % (len(speeds) - len(miss), len(speeds)), "misses at kn:", miss, "off by >1:", len(off2))
m = [k for k in speeds if formula_round(k) != table(k)]
# BREAK: the table is NOT the formula's own bands - formula forward values vs table band centres
fwd = [(b, round(1.625 * b ** 1.5, 1)) for b in range(13)]
inside = sum(1 for b, v in fwd if table(round(v)) == b)
print("forward formula speed lands in its own table band:", inside, "/13", fwd)
big = max(abs(formula_round(k) - table(k)) for k in speeds)
ok = len(m) > 0 and big == 1 and inside == 13 and len(m) / len(speeds) < 0.25
print("RESULT: %s formula-inverse agrees with the band table on %d of 71 integer knots, every miss is one band (max %d), forward formula lands in its own band for %d of 13"
      % ("PASS" if ok else "FAIL", 71 - len(m), big, inside))
