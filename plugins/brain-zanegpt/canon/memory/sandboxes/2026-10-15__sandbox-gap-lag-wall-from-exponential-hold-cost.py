# Information-gap rationing with an exponential cost of holding open questions.
# Each beat opens one gap; it is resolved LAG beats later (lag 0 = "and then" chain, no gap).
# Holding k simultaneous gaps costs GROWTH**k attention per beat; viewer budget is BUDGET.
# If the cost exceeds the budget the OLDEST gap is forgotten (never pays off).
# Iteration 2: first run expected best lag == affordable count; observed one less (a gap is held while its opener is also open).
# Payoff of a resolved gap = 1 + lag (suspense accrues with waiting). All parameters assumed.
def score(lag, growth, budget, beats=40):
    open_q = []            # opening beat of each held gap, oldest first
    total = 0; resolved = 0; dropped = 0; opened = 0
    for t in range(beats):
        if lag == 0:
            total += 1; resolved += 1; opened += 1      # opens and closes in the same beat
            continue
        open_q.append(t); opened += 1
        while growth ** len(open_q) > budget:           # the wall
            open_q.pop(0); dropped += 1
        if open_q and t - open_q[0] >= lag:             # oldest due now
            total += 1 + lag; resolved += 1; open_q.pop(0)
    return total, resolved, dropped

def best(growth, budget):
    return max(range(0, 9), key=lambda L: score(L, growth, budget)[0])

res = {}
for g in (1.3, 1.6, 2.0, 3.0):
    k_afford = 0
    while g ** (k_afford + 1) <= 10: k_afford += 1
    res[g] = (k_afford, best(g, 10), score(best(g, 10), g, 10)[0], score(k_afford, g, 10)[0], score(0, g, 10)[0])
for g, (k, b, s, over, base) in res.items():
    print(f"growth {g}: affordable gaps {k}, best lag {b} score {s}, lag {k} (first lag past the wall) score {over}, and-then baseline {base}")
# BREAK: kernel says prestige pushes the wall back -> a bigger budget (a reset/rest) moves the optimum out
b_big = best(1.6, 40)
print("growth 1.6 with budget 40 (wall pushed back): best lag", b_big)
ok = all(b == k - 1 for (k, b, s, o, base) in res.values() if k > 0) and all(o < s for (k, b, s, o, base) in res.values() if k > 0) \
     and all(s > base for (k, b, s, o, base) in res.values() if k > 0) and b_big > res[1.6][1]
print("RESULT: %s best gap lag is the affordable hold count minus 1 (%s), one lag past it collapses to %s, and-then baseline %s, bigger budget moves best lag %d to %d"
      % ("PASS" if ok else "FAIL", [res[g][1] for g in res], [res[g][3] for g in res], res[1.6][4], res[1.6][1], b_big))
