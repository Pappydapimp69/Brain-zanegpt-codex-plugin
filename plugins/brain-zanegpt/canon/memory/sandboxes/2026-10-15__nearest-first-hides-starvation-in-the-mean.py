"""One lift, 9 floors. Busy low floors (0-3) plus a rare top-floor caller going down (10% of people).
Nearest-first vs sweep (SCAN), over several loads. Measures the longest and average wait.
Lift: 2.4 floors/s, doors 0.9 s, capacity 8. Poisson arrivals, seeded. Mirrors the Going Up game."""
import random, math
def sim(rule, rate, seed, F=9, T=600, top_share=.1):
    r = random.Random(seed); t, dt = 0.0, 1 / 30; y, target, door, dirn = 0.0, None, 0.0, 1
    riders, waiting, waits = [], [], []; nxt = r.expovariate(rate)
    while t < T:
        while nxt <= t:
            if r.random() < top_share: a, b = F - 1, 0
            else: a = r.randrange(4); b = r.randrange(3); b += b >= a
            waiting.append((a, b, nxt)); nxt += r.expovariate(rate)
        if door > 0: door -= dt
        else:
            here = round(y)
            if target is None:
                if len(riders) < 8 and abs(y - here) < 1e-6 and any(p[0] == here for p in waiting): target = here
                else:
                    fs = set(p[1] for p in riders) | (set(p[0] for p in waiting) if len(riders) < 8 else set())
                    fs.discard(here) if abs(y - here) < 1e-6 else None
                    if fs:
                        if rule == 'nearest': target = min(fs, key=lambda f: (abs(f - y), f))
                        else:
                            ahead = [f for f in fs if (f - y) * dirn >= 0]
                            if not ahead: dirn = -dirn; ahead = list(fs)
                            target = min(ahead, key=lambda f: abs(f - y))
            if target is not None:
                d = target - y
                if abs(d) <= 2.4 * dt:
                    y = target; door = .9; f = target; target = None
                    riders = [p for p in riders if p[1] != f]
                    for p in [p for p in waiting if p[0] == f]:
                        if len(riders) < 8: riders.append(p); waiting.remove(p); waits.append(t - p[2])
                else: y += math.copysign(2.4 * dt, d); dirn = 1 if d > 0 else -1
        t += dt
    still = [t - p[2] for p in waiting]
    allw = waits + still
    return max(allw), sum(waits) / max(1, len(waits))
rows = {}
for rate in (.4, .7, .9, 1.1):
    for rule in ('nearest', 'sweep'):
        mx = [sim(rule, rate, s)[0] for s in range(6)]; av = [sim(rule, rate, s)[1] for s in range(6)]
        rows[(rate, rule)] = (sorted(mx)[3], sum(av) / len(av))
        print(f"rate {rate}/s {rule:8s} median longest wait {rows[(rate, rule)][0]:6.1f} s, mean wait {rows[(rate, rule)][1]:5.1f} s")
# the claim, after the first run refuted "they tie at light load": the longest wait separates at EVERY load,
# while the mean barely moves at light load, so a dashboard of averages would miss it
ratio_light = rows[(.4, 'nearest')][0] / rows[(.4, 'sweep')][0]
mean_light = abs(rows[(.4, 'nearest')][1] - rows[(.4, 'sweep')][1])
sweep_bounded = max(rows[(r, 'sweep')][0] for r in (.4, .7, .9, 1.1)) < 60
near_grows = rows[(1.1, 'nearest')][0] > 10 * rows[(.4, 'nearest')][0]
ok = ratio_light > 2 and mean_light < 1 and sweep_bounded and near_grows
print(f"RESULT: {'PASS' if ok else 'FAIL'} even at light load nearest-first's longest wait is {ratio_light:.1f}x the sweep's while mean waits differ by {mean_light:.1f} s; sweep's longest stays under 60 s at every load, nearest-first's grows to {rows[(1.1,'nearest')][0]:.0f} s")
