# Rebuild of: over a 24-tag palette (6 axes x 4 values; vocal, tempo, energy single-valued) half of blind 5-tag sets
# conflict (49.4%), 85.7% of 8-tag sets, and one blind tag on a persona holding each single axis conflicts 47.4%.
# Own method: brute-force enumeration of every subset (not a closed form), then a DIFFERENT palette as the break case
# (5 axes x 5 values, 2 single-valued) to see whether "half by five" is a palette property.
from itertools import combinations
def rate(axes, vals, single, k):
    tags = [(a, v) for a in range(axes) for v in range(vals)]
    tot = bad = 0
    for s in combinations(tags, k):
        tot += 1
        seen = set()
        for a, v in s:
            if a < single:
                if a in seen: bad += 1; break
                seen.add(a)
    return bad / tot
r5, r8 = rate(6, 4, 3, 5), rate(6, 4, 3, 8)
persona_extra = (3 * 3) / (24 - 5)            # persona holds one value on each of 3 single axes (+2 others)
b5, b8 = rate(5, 5, 2, 5), rate(5, 5, 2, 8)
k_half = next(k for k in range(2, 13) if rate(5, 5, 2, k) >= 0.5)
print(f"palette 6x4 (3 single): 5 tags {r5:.4f}, 8 tags {r8:.4f}, persona +1 {persona_extra:.4f}")
print(f"BREAK palette 5x5 (2 single): 5 tags {b5:.4f}, 8 tags {b8:.4f}, first k with >=50% conflict = {k_half}")
ok = round(r5, 3) == 0.494 and round(r8, 3) == 0.857 and round(persona_extra, 3) == 0.474
print("RESULT: %s 6x4 palette: 5-tag %.1f%%, 8-tag %.1f%%, persona+1 %.1f%% by enumeration; other palette (5x5, 2 single) 5-tag %.1f%%, half reached at %d tags" % (
    "PASS" if ok else "FAIL", 100 * r5, 100 * r8, 100 * persona_extra, 100 * b5, k_half))
