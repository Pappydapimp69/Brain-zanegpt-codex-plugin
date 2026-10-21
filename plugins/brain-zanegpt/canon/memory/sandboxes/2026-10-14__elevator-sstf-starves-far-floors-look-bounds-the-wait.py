"""Single elevator, one floor per tick, instant boarding. Requests (arrival tick, floor).
Compare FCFS, SSTF (nearest pending first) and LOOK (sweep in one direction, reverse
when nothing is pending ahead). Deterministic, stdlib only.

PREDICTION (before first run):
 P1 batch of 8 spread requests: total travel FCFS > SSTF >= LOOK-ish, LOOK within 15% of SSTF.
 P2 continuous hot-floor stream (a request near the car every 2 ticks) with one request at
    the far floor 20 at tick 0: SSTF max wait > 150 ticks (starvation), LOOK max wait < 60, FCFS < 60.
 P3 the same stream: SSTF MEAN wait is the lowest of the three (starvation hides in the mean).
 P4 BREAK: when the stream stops at tick 100, SSTF serves the far floor right after (max wait ~ 100 + travel),
    i.e. starvation lasts only as long as the hot stream does.
"""
def simulate(policy, reqs, horizon=2000, start=0):
    pos = start; direction = 1; t = 0; pending = []; done = {}; travel = 0
    reqs = sorted(reqs, key=lambda r: r[0]); i = 0
    while t < horizon and (i < len(reqs) or pending):
        while i < len(reqs) and reqs[i][0] <= t:
            pending.append(reqs[i]); i += 1
        # serve anything at the current floor
        served = [r for r in pending if r[1] == pos]
        for r in served:
            pending.remove(r); done[id(r)] = t - r[0]
        if not pending:
            t += 1; continue
        if policy == 'FCFS':
            target = pending[0][1]
            step = (target > pos) - (target < pos)
        elif policy == 'SSTF':
            target = min(pending, key=lambda r: (abs(r[1] - pos), r[0]))[1]
            step = (target > pos) - (target < pos)
        else:  # LOOK
            ahead = [r for r in pending if (r[1] - pos) * direction > 0]
            if not ahead: direction = -direction
            step = direction
        pos += step; travel += 1; t += 1
    waits = list(done.values())
    return travel, sum(waits) / max(1, len(waits)), max(waits) if waits else 0, len(done), len(reqs)

res = {}
batch = [(0, 3), (0, 17), (0, 8), (0, 1), (0, 14), (0, 6), (0, 19), (0, 11)]
for p in ('FCFS', 'SSTF', 'LOOK'):
    res[("batch", p)] = simulate(p, batch, start=10)
    print("batch", p, "travel %d mean %.1f max %d served %d/%d" % res[('batch', p)])

def stream(stop):
    reqs = [(0, 20)]
    for k in range(0, stop, 2):
        reqs.append((k, 1 + (k // 2) % 3))        # hot floors 1..3 near the car
    return reqs
for stop in (100, 400):
    for p in ('FCFS', 'SSTF', 'LOOK'):
        res[('stream', stop, p)] = simulate(p, stream(stop))
        print("stream stop=%d" % stop, p, "travel %d mean %.1f max %d served %d/%d" % res[('stream', stop, p)])

b = {p: res[('batch', p)] for p in ('FCFS', 'SSTF', 'LOOK')}
s = {p: res[('stream', 400, p)] for p in ('FCFS', 'SSTF', 'LOOK')}
s100 = res[('stream', 100, 'SSTF')]
p1 = b['FCFS'][0] > b['SSTF'][0] and b['LOOK'][0] <= 1.15 * b['SSTF'][0]
p2 = s['SSTF'][2] > 150 and s['LOOK'][2] < 60 and s['FCFS'][2] < 60
p3 = s['SSTF'][1] <= min(s['FCFS'][1], s['LOOK'][1])
p4 = 100 <= s100[2] <= 140
print("P1..P4 held:", p1, p2, p3, p4)
print("RESULT: %s batch-travel FCFS/SSTF/LOOK=%d/%d/%d; stream400 max-wait FCFS/SSTF/LOOK=%d/%d/%d mean=%.1f/%.1f/%.1f; stream100 SSTF max-wait=%d (held %d/4)" % (
    "PASS" if all([p1, p2, p3, p4]) else "FAIL", b['FCFS'][0], b['SSTF'][0], b['LOOK'][0],
    s['FCFS'][2], s['SSTF'][2], s['LOOK'][2], s['FCFS'][1], s['SSTF'][1], s['LOOK'][1], s100[2], sum([p1, p2, p3, p4])))
