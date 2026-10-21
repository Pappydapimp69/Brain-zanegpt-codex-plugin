# Prediction (before run): with mites doubling every 30d from 1.0/100 and threshold 3/100 (model values),
# true crossing is day 48. Washing every 14d and reading a 300-bee wash (steps of 0.33/100) detects the
# crossing late by up to one interval plus quantisation; weekly washes cut exposure days above threshold
# vs 28-day washes but cost 4x the washes; a doubling-time projection (fit on last 2 readings in log space)
# triggers an earlier action than the raw threshold reading when readings are noise-free, but with
# 300-bee quantisation at low counts the log fit can be wrong (BREAK: starting at 0.33 reads zero -> no fit).
import math
DOUBLE, TH, BEES = 30.0, 3.0, 300
def true_rate(d, r0=1.0, decay=0.0): return r0 * 2 ** (d / DOUBLE) / (1 - decay * d)
def read(d, r0=1.0, decay=0.0):
    return round(true_rate(d, r0, decay) / 100 * BEES) / BEES * 100
def first_cross(r0=1.0, decay=0.0):
    d = 0
    while true_rate(d, r0, decay) < TH: d += 1
    return d
def run(interval, mode, r0=1.0, decay=0.0, horizon=120):
    """return (action_day, washes, exposure_days_above_threshold_before_action)"""
    prev = None; washes = 0
    for d in range(0, horizon, interval):
        washes += 1
        v = read(d, r0, decay)
        act = v >= TH
        if mode == "proj" and prev and prev[1] > 0 and v > prev[1]:
            dt = d - prev[0]
            dbl = dt * math.log(2) / math.log(v / prev[1])
            tcross = d + dbl * math.log(TH / v) / math.log(2)
            act = act or tcross <= d + interval   # would cross before next wash
        prev = (d, v)
        if act:
            return d, washes, max(0, d - first_cross(r0, decay))
    return None, washes, None
tc = first_cross()
print("true crossing day", tc)
res = {}
for iv in (7, 14, 28):
    for m in ("raw", "proj"):
        res[(iv, m)] = run(iv, m)
        print("S1 interval %2d mode %-4s -> action day %s washes %d exposure %s" % ((iv, m) + res[(iv, m)]))
s2 = {m: run(14, m, decay=0.004) for m in ("raw", "proj")}
print("S2 shrinking bees (crossing day %d): %s" % (first_cross(decay=0.004), s2))
s3 = {m: run(14, m, r0=0.33) for m in ("raw", "proj")}
print("S3 BREAK start at 0.33/100 (crossing %d): %s" % (first_cross(r0=0.33), s3))
ok1 = res[(7,"raw")][2] < res[(28,"raw")][2] and res[(28,"raw")][1] > res[(7,"raw")][1] is False or True
ok1 = res[(7,"raw")][2] <= res[(14,"raw")][2] <= res[(28,"raw")][2] and res[(7,"raw")][1] > res[(28,"raw")][1]
ok2 = res[(14,"proj")][2] <= res[(14,"raw")][2]
ok3 = all(v[2] is not None for v in s3.values()) and s3["proj"][2] >= 0
print("RESULT: %s exposure days raw 7/14/28d = %s/%s/%s (washes %s/%s/%s); proj at 14d exposure %s vs raw %s; shrinking bees raw exposure %s; 0.33 start proj exposure %s vs raw %s"
      % ("PASS" if (ok1 and ok2 and ok3) else "FAIL",
         res[(7,"raw")][2], res[(14,"raw")][2], res[(28,"raw")][2],
         res[(7,"raw")][1], res[(14,"raw")][1], res[(28,"raw")][1],
         res[(14,"proj")][2], res[(14,"raw")][2], s2["raw"][2], s3["proj"][2], s3["raw"][2]))
