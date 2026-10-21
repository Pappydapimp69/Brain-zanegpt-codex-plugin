# Prediction (before running): 3 cards (limit/statement balance 2000/1800, 5000/2000, 10000/1200), budget 1500
# paid before close, 50-unit grid. (a) Aggregate utilization is identical for every allocation that spends
# the whole budget (5000-1500=3500 over 17000 = 20.59%). (b) Water-filling (always pay the card with the
# highest utilization) reaches the brute-force minimum of the MAXIMUM per-card utilization. (c) Built to
# break: for the objective "fewest cards at or above 10 percent", water-filling is NOT optimal; brute
# force finds a strictly lower count. (d) The same budget paid after close changes reported utilization by 0.
import itertools
L = (2000, 5000, 10000); B0 = (1800, 2000, 1200); BUD = 1500; STEP = 50
def util(b): return [x / l for x, l in zip(b, L)]
def reported(b_close): return util(b_close)
splits = [(a, b, BUD - a - b) for a in range(0, BUD + 1, STEP) for b in range(0, BUD - a + 1, STEP)
          if 0 <= BUD - a - b and a <= B0[0] and b <= B0[1] and BUD - a - b <= B0[2]]
def apply(s): return tuple(x - p for x, p in zip(B0, s))
aggs = {round(sum(apply(s)) / sum(L), 6) for s in splits}
def waterfill():
    b = list(B0); left = BUD
    while left > 0:
        i = max(range(3), key=lambda k: b[k] / L[k] if b[k] > 0 else -1)
        p = min(STEP, left, b[i]); b[i] -= p; left -= p
    return tuple(b)
wf = waterfill()
best_max = min(max(util(apply(s))) for s in splits)
wf_max = max(util(wf))
cnt = lambda b, th: sum(u >= th for u in util(b))
best_cnt10 = min(cnt(apply(s), 0.10) for s in splits)
best_cnt30 = min(cnt(apply(s), 0.30) for s in splits)
print("splits", len(splits), "aggregate values", aggs)
print("waterfill balances", wf, "max util %.4f vs brute %.4f" % (wf_max, best_max))
print("count>=10%%: waterfill %d brute %d | count>=30%%: waterfill %d brute %d" % (cnt(wf, .10), best_cnt10, cnt(wf, .30), best_cnt30))
post = reported(B0)  # payment after close leaves the closing balances unchanged
print("post-close payment reported", [round(u, 3) for u in post], "== no-payment", post == reported(B0))
ok = len(aggs) == 1 and abs(wf_max - best_max) < 1e-9 and best_cnt10 < cnt(wf, .10)
print("RESULT: %s aggregate %s identical across %d allocations; waterfill max util %.3f = brute-force min %.3f; count>=10%% waterfill %d vs best %d" % ("PASS" if ok else "FAIL", sorted(aggs), len(splits), wf_max, best_max, cnt(wf, .10), best_cnt10))
