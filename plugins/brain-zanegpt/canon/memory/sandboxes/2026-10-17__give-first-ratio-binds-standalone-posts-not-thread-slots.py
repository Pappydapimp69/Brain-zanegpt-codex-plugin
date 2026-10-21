"""Sandbox: with a fixed action budget, how do three DISTRIBUTION kernels' rules combine?
  reddit-containment-not-prohibition: standalone self-promo needs cumulative comments >= R * posts
      (R=9), while a dedicated weekly thread takes a post with no ratio (13 weekly slots in 90 days).
  itch-devlog-cadence-discipline: devlogs at least 15 days apart (<= 6 in 90 days); daily posting unfollows.
  never-duplicate-copy-across-venues: every extra venue's copy must be rewritten (cost +1).
Costs (assumed units of effort): thread post 1+1 rewrite, devlog 3 (+1 rewrite), standalone post 1+1 rewrite
plus R comments each. Reach (assumed): thread 1.0, devlog 2.0, standalone 5.0.
Prediction (written before first run): at budget 60 the optimum has zero standalone posts and uses all 13 thread
slots and 6 devlogs; standalone first enters the optimum only above a budget of about 150; at R=3 it enters
at a lower budget. Assumption: reach values are fixed (standalone reach does not rise when it is rarer);
BREAK scenario: R=1 and a very large budget, where slots, not the ratio, should bind."""
THREADS, DEVLOGS = 13, 6
def best(budget, R):
    top = (-1, None)
    for t in range(THREADS + 1):
        for d in range(DEVLOGS + 1):
            cost_td = 2 * t + 4 * d
            if cost_td > budget:
                continue
            s = (budget - cost_td) // (2 + R)
            reach = 1.0 * t + 2.0 * d + 5.0 * s
            if reach > top[0]:
                top = (reach, (t, d, s))
    return top
def first_standalone(R):
    for b in range(1, 2000):
        if best(b, R)[1][2] > 0:
            return b
for b in (30, 60, 100, 150, 300):
    print(f"R=9 budget={b}: reach={best(b, 9)[0]:.1f} plan(threads,devlogs,standalone)={best(b, 9)[1]}")
f9, f3, f1 = first_standalone(9), first_standalone(3), first_standalone(1)
print(f"standalone enters the optimum at budget {f9} (R=9), {f3} (R=3), {f1} (R=1)")
full = best(2000, 1)[1]
print("R=1 budget 2000 plan:", full)
def best_reach(budget, R, reach_s):
    top = (-1, None)
    for t in range(THREADS + 1):
        for d in range(DEVLOGS + 1):
            c = 2 * t + 4 * d
            if c > budget:
                continue
            s = (budget - c) // (2 + R)
            r = 1.0 * t + 2.0 * d + reach_s * s
            if r > top[0]:
                top = (r, (t, d, s))
    return top
# Break-even: a standalone post costs 2+R actions, a thread post 2, so standalone beats a thread slot
# only when its reach exceeds (2+R)/2 x thread reach; at R=9 that is 5.5 versus the assumed 5.
for reach_s in (4.0, 5.0, 5.4, 5.6, 8.0):
    print(f"budget 2000 R=9 standalone reach {reach_s}: plan {best_reach(2000, 9, reach_s)[1]}")
flip = [rs for rs in (4.0, 5.0, 5.4, 5.6, 8.0) if best_reach(2000, 9, rs)[1][0] == 0]
print("reach values where standalone replaces every thread post:", flip, "(break-even 5.5)")
b60 = best(60, 9)[1]
ok = b60[2] == 0 and b60[0] == THREADS and b60[1] == DEVLOGS and f9 > f3 > f1 and full[0] == THREADS and full[1] == DEVLOGS
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" predicted zero standalone at budget 60 but plan was {b60}; standalone enters at budget {f9} (R=9), {f3} (R=3), {f1} (R=1); break-even reach (2+R)/2 means reach decides, not the ratio")
