# Deterministic: a hook caption must be readable in the hook window. Words readable =
# rate * (hook_seconds * slow + pause). Retention cost: slope*(slow-1) + pause_cost*pause.
RATE = 5 / 3.0          # words/s under the film engine (hook-caption-budget: 5 words in 3 s)
HOOK = 3.0

def words_fit(slow, pause):
    return int(RATE * (HOOK * slow + pause) + 1e-9)

def retention_cost(slow, pause, slope, pcost):
    return slope * (slow - 1) * 100 + pcost * pause * 100

def best(words, cap, pause_max, slope, pcost):
    opts = []
    for s100 in range(100, int(cap * 100) + 1, 5):
        for p10 in range(0, int(pause_max * 10) + 1):
            s, p = s100 / 100, p10 / 10
            if words_fit(s, p) >= words:
                opts.append((retention_cost(s, p, slope, pcost), s, p))
    return min(opts) if opts else None

print("fit, no warp, no pause:", words_fit(1.0, 0))
print("fit, cap 1.5, no pause:", words_fit(1.5, 0))
print("fit, cap 1.5 + 0.6s pause:", words_fit(1.5, 0.6))
r5 = best(5, 1.5, 1.0, 0.2, 0.2)
r8 = best(8, 1.5, 1.0, 0.2, 0.2)
r8_nopause = best(8, 1.5, 0.0, 0.2, 0.2)
r10 = best(10, 1.5, 1.0, 0.2, 0.2)
# BREAK: pause so costly (0.2 per second -> 2.0) that it beats nothing; at pcost high, best is None-or-warp-only
r8_costly = best(8, 1.5, 1.0, 0.2, 2.0)
r8_flat = best(8, 1.5, 1.0, 0.005, 0.2)   # warp nearly free: warp wins over pause
print("5 words best:", r5)
print("8 words best:", r8, "| without pause allowed:", r8_nopause)
print("10 words best:", r10)
print("8 words, pause 10x costly:", r8_costly, "| warp nearly free:", r8_flat)
r7_warp = best(7, 1.5, 1.0, 0.05, 0.5)     # warp cheap, pause dear -> warp only
r7_pause = best(7, 1.5, 1.0, 0.5, 0.05)    # warp dear, pause cheap -> mostly pause
print("7 words, warp cheap:", r7_warp, "| pause cheap:", r7_pause)
ok = (words_fit(1.0, 0) == 5 and words_fit(1.5, 0) == 7 and r8_nopause is None
      and r8 is not None and r8[2] > 0 and r10 is None and r8_flat[2] > 0 and r5[1] == 1.0
      and r7_warp[2] == 0.0 and r7_pause[2] > 0 and r7_pause[1] < 1.5)
print(f"RESULT: {'PASS' if ok else 'FAIL'} fit 5/7/{words_fit(1.5,0.6)} words; 8 words needs pause {r8[2]}s even with free warp {r8_flat}; 10 impossible; 7 words warp-only {r7_warp} vs pause-mix {r7_pause}")
