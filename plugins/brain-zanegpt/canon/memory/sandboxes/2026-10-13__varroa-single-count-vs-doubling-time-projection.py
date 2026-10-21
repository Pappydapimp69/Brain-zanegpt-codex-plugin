# Prediction (before run): with mites doubling every 30 days (model value), a count of 1.0/100 bees on day 0
# reaches the 3/100 action threshold on day ~48 (30*log2(3)); a 300 bee wash can only report multiples of
# 0.33/100 so a true 0.9/100 reads 1 mite = 0.33 or 3 mites = 1.0 depending on the sample; and when the bee
# population shrinks in autumn the per-bee rate crosses the threshold earlier than mite count alone says.
import math
DOUBLE = 30.0
def rate(day, r0, bees0=100.0, bee_decay=0.0):
    mites = r0 * 2 ** (day / DOUBLE)
    bees = bees0 * (1 - bee_decay * day)
    return mites / bees * 100.0 / (100.0 / bees0) if False else mites / (bees / bees0)
def day_to(th, r0, bee_decay=0.0):
    d = 0
    while rate(d, r0, bee_decay=bee_decay) < th and d < 400: d += 1
    return d
# S1 exponential truth vs linear extrapolation from two samples 30 days apart
r0 = 1.0
true_day = day_to(3.0, r0)
s30 = rate(30, r0); slope = (s30 - r0) / 30.0
lin_day = int(math.ceil((3.0 - r0) / slope))
print("S1 true day %d linear-projection day %d" % (true_day, lin_day))
# S2 300 bee wash granularity: integer counts only
def reading(true_rate, bees=300):
    return round(true_rate / 100.0 * bees) / bees * 100.0
vals = {t: reading(t) for t in (0.4, 0.9, 1.4, 2.6, 3.0)}
print("S2 readings", {k: round(v, 2) for k, v in vals.items()})
# S3 shrinking bee population (1% of bees lost per day, BREAK)
d_flat = day_to(3.0, r0); d_shrink = day_to(3.0, r0, bee_decay=0.004)
print("S3 threshold day flat bees %d shrinking bees %d" % (d_flat, d_shrink))
ok1 = true_day < lin_day and abs(true_day - 48) <= 1
ok2 = vals[0.9] == vals[1.4] or vals[2.6] != vals[3.0] or True
ok2 = round(vals[0.9], 2) == 1.0 and round(vals[0.4], 2) == 0.33
ok3 = d_shrink < d_flat
print("RESULT: %s doubling 30d gives threshold day %d vs linear projection day %d; 300-bee wash reads 0.9->%.2f, 0.4->%.2f (step 0.33); shrinking bees move the day %d->%d"
      % ("PASS" if (ok1 and ok2 and ok3) else "FAIL", true_day, lin_day, vals[0.9], vals[0.4], d_flat, d_shrink))
