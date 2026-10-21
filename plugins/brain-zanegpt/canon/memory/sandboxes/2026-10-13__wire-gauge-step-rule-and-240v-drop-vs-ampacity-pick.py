# Prediction (before run): (1) 15 A / 100 ft at 120 V: 14 AWG 7.68 %, 12 -> 4.83, 10 -> 3.03, 8 -> 1.95 so the
# first gauge at or under 3 % is 8 AWG; (2) the 'every 2 AWG steps cuts resistance by 0.63' rule predicts the
# 8 AWG drop within 3 % of the table (1.92 vs 1.95); (3) the same 1800 W load at 240 V draws half the current
# so the percentage drop is one quarter on the same wire (1.92 % on 14 AWG at 100 ft) and 14 AWG then passes 3 %.
OHM = {14: 3.07, 12: 1.93, 10: 1.21, 8: 0.778, 6: 0.491}  # ohm per 1000 ft copper, typed from published table
AMP = {14: 15, 12: 20, 10: 30, 8: 40, 6: 55}
def drop(g, amps, ft, v): return 2 * amps * OHM[g] / 1000.0 * ft / v * 100.0
def pick(amps, ft, v, lim=3.0):
    amp_pick = next(g for g in (14, 12, 10, 8, 6) if AMP[g] >= amps)
    final = next(g for g in (14, 12, 10, 8, 6) if AMP[g] >= amps and drop(g, amps, ft, v) <= lim)
    return amp_pick, final
a, f = pick(15, 100, 120)
d = {g: round(drop(g, 15, 100, 120), 2) for g in OHM}
print("S1", d, "ampacity pick", a, "final pick", f)
s1 = a == 14 and f == 8 and abs(d[14] - 7.68) <= 0.011 and d[8] == 1.95 and d[10] > 3.0
rule = drop(14, 15, 100, 120) * 0.63 ** 3
err = abs(rule - drop(8, 15, 100, 120)) / drop(8, 15, 100, 120) * 100
print("S2 rule estimate for 8 AWG %.2f vs table %.2f (%.1f %% off)" % (rule, drop(8, 15, 100, 120), err))
s2 = err < 3.0
# BREAK for the rule: it needs gauges two steps apart, near the table ends the ratio drifts
ratios = [OHM[b] / OHM[a_] for a_, b in ((14, 12), (12, 10), (10, 8), (8, 6))]
print("S2b step ratios", [round(r, 3) for r in ratios])
s2b = max(ratios) - min(ratios) < 0.05 and min(ratios) > 0.6
watts = 15 * 120
d240 = drop(14, watts / 240.0, 100, 240)
print("S3 same %d W at 240 V on 14 AWG 100 ft: %.2f %%" % (watts, d240))
s3 = abs(d240 - 7.68 / 4) < 0.01 and pick(watts / 240.0, 100, 240)[1] == 14
print("RESULT: %s 15A/100ft 120V ampacity pick %d final pick %d (7.68 -> 1.95 pct); 0.63^3 rule off by %.1f pct; 240V quarter drop %.2f pct keeps 14 AWG"
      % ("PASS" if (s1 and s2 and s2b and s3) else "FAIL", a, f, err, d240))
