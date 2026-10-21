# Cache policy vs cache size on a cyclic loop, with a hit/miss latency model and a memory ceiling.
# Costs (assumed, ratios from the latency-numbers kernel order of magnitude): hit 1, miss 100,
# and slots beyond HEADROOM live in swapped memory so every access to them costs PAGED (E226 cliff).
from collections import OrderedDict, deque
HEADROOM, HIT, MISS, PAGED = 6, 1, 100, 150

def run(trace, size, policy):
    if size == 0: return 0, len(trace)
    if policy == "lru":
        c = OrderedDict(); hits = 0
        for x in trace:
            if x in c: c.move_to_end(x); hits += 1
            else:
                if len(c) >= size: c.popitem(last=False)
                c[x] = 1
    else:
        c = deque(); s = set(); hits = 0
        for x in trace:
            if x in s: hits += 1
            else:
                if len(c) >= size: s.discard(c.popleft())
                c.append(x); s.add(x)
    return hits, len(trace) - hits

def cost(trace, size, policy):
    h, m = run(trace, size, policy)
    per_hit = HIT if size <= HEADROOM else PAGED
    return h * per_hit + m * MISS

loop = [i % 5 for i in range(100)]
rows = {}
for pol in ("lru", "fifo"):
    rows[pol] = {s: run(loop, s, pol)[0] for s in range(1, 9)}
print("hits by size, loop of 5:", rows)
same = rows["lru"] == rows["fifo"]
cliff = (rows["lru"][4] == 0 and rows["lru"][5] == 95)
by_cost = {s: cost(loop, s, "lru") for s in range(1, 9)}
by_hits_best = max(rows["lru"], key=lambda s: (rows["lru"][s], s))
by_cost_best = min(by_cost, key=lambda s: (by_cost[s], s))
print("cost by size:", by_cost, "| hit-rate-only picks", by_hits_best, "| cost picks", by_cost_best)
# BREAK 1: Belady's anomaly - FIFO gets worse with MORE slots; LRU does not
bel = [1,2,3,4,1,2,5,1,2,3,4,5]
f3, f4 = run(bel, 3, "fifo")[1], run(bel, 4, "fifo")[1]
l3, l4 = run(bel, 3, "lru")[1], run(bel, 4, "lru")[1]
print("belady faults fifo 3->4 slots: %d->%d ; lru: %d->%d" % (f3, f4, l3, l4))
ok = same and cliff and by_hits_best == 8 and by_cost_best == 5 and f4 > f3 and l4 <= l3
print("RESULT: %s policy-equal on a 5-loop (0 hits below 5 slots, 95 at 5), hit-rate-only picks %d slots but cost with a %d-slot ceiling picks %d; FIFO faults %d->%d going 3->4 slots (LRU %d->%d)"
      % ("PASS" if ok else "FAIL", by_hits_best, HEADROOM, by_cost_best, f3, f4, l3, l4))
