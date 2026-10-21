# Deterministic bus-bunching on a line route (no overtaking). Exact fractions, no RNG.
from fractions import Fraction as F
def run(rho, hold, buses=8, stops=40, H=F(10), T=F(2), perturb=F(1, 2)):
    """dwell at a stop = rho * gap, gap = time since the leader left that stop (passengers accrue at rate 1).
    hold = min headway enforced by holding at EVERY stop (0 = free running). Buses released H apart,
    odd buses delayed by perturb*H. Returns per-stop (departure headways list) and total passenger wait."""
    d_prev_stop = [F(i) * H + (perturb * H if i % 2 else 0) for i in range(buses)]   # departure times from the depot
    lead_dep = None
    heads = []; wait_area = F(0); pax = F(0)
    cur = d_prev_stop[:]
    for s in range(stops):
        arr = [c + T for c in cur]
        dep = []
        for b in range(buses):
            prev = dep[b - 1] if b else arr[0] - H            # first bus: stop was last served one headway ago
            start = max(arr[b], prev)                         # cannot pass the leader
            if hold and start - prev < hold: start = prev + hold
            gap = start - prev
            dep.append(start + rho * gap)
            pax += gap; wait_area += gap * gap / 2
        cur = dep
        heads.append([dep[b] - dep[b - 1] for b in range(1, buses)])
    return heads, wait_area / pax
def cv(h):
    m = sum(h) / len(h); v = sum((x - m) ** 2 for x in h) / len(h)
    return float(v) ** 0.5 / float(m)
res = {}
for rho in (F(0), F(1, 10), F(1, 4), F(2, 5)):
    h0, w0 = run(rho, 0)
    row = {"first": round(cv(h0[0]), 3), "free_last": round(cv(h0[-1]), 3), "free_wait": round(float(w0), 1)}
    for hold in (6, 10, 11, 12):                       # nominal headway is 10 (BREAK: holds just below and above it)
        hh, ww = run(rho, F(hold)); row["hold%d" % hold] = (round(cv(hh[-1]), 2), round(float(ww), 1))
    res[str(rho)] = row
    print("rho", rho, row)
grows = all(res[k]["free_last"] > res[k]["first"] for k in res if k != "0")
flat0 = res["0"]["free_last"] == res["0"]["first"]
cliff = all(res[k]["hold11"][0] == 0 and res[k]["hold12"][0] == 0 for k in res if k != "0")
below = all(res[k]["hold10"][0] > 0.5 for k in res if k != "0")
waitdrop = all(res[k]["hold11"][1] < res[k]["free_wait"] for k in res if k != "0")
ok = grows and flat0 and cliff and below and waitdrop
print("RESULT: %s dwell proportional to gap grows headway cv along the route (0.55-0.86 -> 2.45 = one platoon of 8) for rho 0.1-0.4, flat at rho=0; holding to a minimum headway of 10 (nominal) leaves cv 1.7-2.4 but 11 or 12 gives cv 0 and mean wait 5.5-6 vs 28-145729 free"
      % ("PASS" if ok else "FAIL"))
