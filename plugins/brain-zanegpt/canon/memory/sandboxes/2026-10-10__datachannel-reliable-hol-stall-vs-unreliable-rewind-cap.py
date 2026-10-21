"""Model (not a real browser): 60 Hz position updates (16 ms tick) over a 40 ms one-way link.
Every LOSS_EVERY-th packet is lost. reliable+ordered: lost packet retransmitted after RTO, all later packets
wait behind it (head-of-line). unordered+maxRetransmits=0: lost packet is simply gone, others arrive on time.
Prediction (before run): reliable max staleness >= 3x unreliable max staleness at RTO 120 ms; unreliable max
staleness == 2 ticks-ish (<= 2*16+40+? ) i.e. under 100 ms; sender backlog (packets queued unacked behind a stall)
peaks >= 7 on reliable and 0 on unreliable; an uncapped rewind (claimed latency = measured staleness) lets a hit on a
target already in cover register on reliable and a 50 ms cap blocks it; with NO loss both channels are identical (control)."""
TICK, LAT, N = 16, 40, 600
def sim(reliable, loss_every, rto):
    arrive = {}
    stall_until = 0
    for i in range(N):
        send = i * TICK
        lost = loss_every and (i % loss_every == loss_every - 1)
        if reliable:
            t = send + LAT
            if lost:
                t = send + LAT + rto; stall_until = max(stall_until, t)
            else:
                t = max(t, stall_until)
            arrive[i] = t
        else:
            if not lost: arrive[i] = send + LAT
    stal = []; backlog = 0
    for now in range(0, N * TICK, TICK):
        got = [i for i, a in arrive.items() if a <= now]
        newest = max(got) if got else -1
        stal.append(now - newest * TICK if newest >= 0 else 0)
    # backlog = packets sent but not yet delivered, beyond the normal in-flight (LAT/TICK)
    peak = 0
    for now in range(0, N * TICK, TICK):
        sent = now // TICK + 1
        delivered = sum(1 for a in arrive.values() if a <= now)
        lostc = sum(1 for i in range(sent) if i not in arrive)
        peak = max(peak, sent - delivered - lostc - (LAT // TICK + 1))
    return max(stal), sum(stal) / len(stal), max(0, peak)
# target stands 20 units inside cover now (pos=60, cover edge at 40 means pos>=40 is covered); moves 0.2 u/ms toward cover.
def hit(claimed, cap):
    rew = min(claimed, cap); pos_then = 60 - 0.2 * rew   # earlier position, further from cover
    return pos_then < 40          # exposed then => hit registers
rows = {}
for name, rel, le in (("reliable loss", True, 7), ("unreliable loss", False, 7), ("reliable noloss", True, 0), ("unreliable noloss", False, 0)):
    rows[name] = sim(rel, le, 120)
    print(f"{name:18s} maxstale={rows[name][0]:4d} ms mean={rows[name][1]:6.1f} backlog_peak={rows[name][2]}")
r, u = rows["reliable loss"], rows["unreliable loss"]
c1, c2 = rows["reliable noloss"], rows["unreliable noloss"]
claimed_rel, claimed_unrel = r[0], u[0]
h = {(k, cap): hit(c, cap) for k, c in (("reliable", claimed_rel), ("unreliable", claimed_unrel)) for cap in (1000, 50)}
print("claimed latency reliable", claimed_rel, "unreliable", claimed_unrel, "hits", h)
# mutually exclusive limits (spec rule modeled as a validator)
def create(ordered=True, mr=None, mpl=None):
    if mr is not None and mpl is not None: raise ValueError("SyntaxError")
    return "reliable" if mr is None and mpl is None else "unreliable"
try: create(False, 0, 100); excl = False
except ValueError: excl = True
sweep = {rto: round(sim(True, 7, rto)[0] / u[0], 2) for rto in (60, 120, 240, 480)}
print("ratio reliable/unreliable max staleness by RTO", sweep)
ok = (r[0] >= 3 * u[0] and u[0] < 100 and r[2] >= 7 and u[2] == 0 and c1[:2] == c2[:2]
      and h[("reliable", 1000)] and not h[("reliable", 50)] and excl)
print("RESULT:", "PASS" if ok else "FAIL", f"reliable maxstale {r[0]} vs unreliable {u[0]} ms; backlog {r[2]} vs {u[2]}; uncapped reliable hit {h[('reliable',1000)]}, cap50 {h[('reliable',50)]}; no-loss identical {c1[:2]==c2[:2]}; ratio by RTO {sweep}")
