# Own fixture: real 4x4 Bayer matrix; a reveal turns on pixels whose threshold < level. Level climbs by the
# step assigned to each derived beat; "full" means all 16 pixels on after the last beat.
BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def lit(level): return sum(1 for r in BAYER for t in r if t < level)
def floor_split(k): return [16//k]*k
def remainder_split(k):
    base, rem = divmod(16, k); return [base+1 if i < rem else base for i in range(k)]
def final_lit(steps): return lit(min(16, sum(steps)))
fl_fail = [k for k in range(1, 17) if final_lit(floor_split(k)) < 16]
rm_fail = [k for k in range(1, 17) if final_lit(remainder_split(k)) < 16]
spread_ok = all(max(remainder_split(k)) - min(remainder_split(k)) <= 1 for k in range(1, 17))
print("floor stalls at k =", fl_fail, "count", len(fl_fail))
print("remainder stalls at k =", rm_fail, "spread<=1 for all:", spread_ok)
# BREAK: k above 16 -- remainder gives zero-step beats; does it still reach full, and does it show dead beats?
over = {k: (final_lit(remainder_split(k)), remainder_split(k).count(0)) for k in (17, 20, 24)}
print("k>16 (lit, zero-step beats):", over)
# non-divisors: how short does floor fall (pixels lit of 16)?
short = {k: final_lit(floor_split(k)) for k in fl_fail}; print("floor lit counts:", short)
ok = len(fl_fail) == 11 and not rm_fail and spread_ok and all(z > 0 for _, z in over.values())
print("RESULT: %s floor stalls on %d of 16 counts, remainder 0, spread<=1; k>16 yields dead beats %s" % ("PASS" if ok else "FAIL", len(fl_fail), over))
