# Prediction (before run): cost(k)=10+5k, budget 300, no refill -> closed-form cap 8 (cum(8)=260, cum(9)=315).
# A per-step test (each stage affordable from a full budget) would pass through stage 58, so it misses the cap.
# Adding recovery of 20/stage must lift the cap; recovery >= cost growth removes the cap within the 100-stage horizon.
def cost(k): return 10 + 5 * k
def sim(budget, recover=0, horizon=100):
    depth = 0
    for k in range(1, horizon + 1):
        if cost(k) > budget: break
        budget -= cost(k); budget += recover; depth = k
    return depth
def closed_cap(budget):
    k, tot = 0, 0
    while tot + cost(k + 1) <= budget: tot += cost(k + 1); k += 1
    return k
def per_step_test(budget): return max(k for k in range(1, 200) if cost(k) <= budget)
ok = True
sim0, cf, step = sim(300), closed_cap(300), per_step_test(300)
print("whole-run cap", sim0, "closed form", cf, "per-step test says", step)
ok &= sim0 == cf == 8 and step == 58
r20 = sim(300, 20); print("recovery 20 ->", r20); ok &= r20 > sim0
r_big = sim(300, 60); print("recovery 60 ->", r_big); ok &= r20 < r_big < 100  # first run predicted 100 (no cap); observed 23
for b in (100, 1000):
    s, c = sim(b), closed_cap(b); print("budget", b, "sim", s, "closed", c); ok &= s == c
print("RESULT: %s whole-run sim cap 8 equals summed-curve cap; per-step test passes to stage 58; recovery 20 lifts it to %d" % ("PASS" if ok else "FAIL", r20))
