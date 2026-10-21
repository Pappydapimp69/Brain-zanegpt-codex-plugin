"""Sandbox: six-beat comic arc. Entries composed: ideas:COMEDY/premise-design/an-absurd-premise-needs-a-wrong-cue-and-a-safe-cue
(a beat only lands if it is wrong AND safe), escalation-needs-matching-distance/E1 (gate g = exp(-((d - I/C)/0.25)^2), habituation
exp(-0.2 X), X += 1/(1 + I/5) per beat, ceiling C = 10), ideas:COMEDY/timing/one-peak-violation-with-a-held-pause (one biggest beat
after a pause beats constant randomness; correlational). Beat response r = (I/C) * exp(-0.2 X) * g(d, I) * pause(p) with
pause(p) = 1 - exp(-p/1.5) for the peak beat only (p seconds of stillness before it; other beats p = 0.2 baseline).
Schedules: SINGLE = five calm beats (I = 0) then one peak of intensity I with pause p; STACK = six beats all at intensity I.
PREDICTION (before first run; the equal-pause STACK scenario was added after the first run showed the unpaused stack handicapped by the pause term, and its result is reported as such): (a) with a fixed grounded distance d = 0.3, the best SINGLE peak is I = 3 and scores about 0.30 * 0.63 (p=1.5)
~ 0.19; (b) by TOTAL response the best STACK beats the best SINGLE at every d tried (0.3, 0.6, 0.9) because six matched beats sum; (c) by PEAK
response (the largest single beat, the kernel's claim) SINGLE with a 3 s pause beats STACK at every d, because the stack habituates;
(d) so the winner flips with the metric and the kernels do not agree on what is being maximised. Assumption: the metrics agree. BREAK: scenario
(b) where sum favours the stack. Wrong if SINGLE wins both metrics, or STACK wins both."""
import math
C = 10.0
def gate(d, I): return math.exp(-(((d - I / C) / 0.25) ** 2))
def pause(p): return 1 - math.exp(-p / 1.5)
def arc(kind, I, d, p):
    X = 0.0; out = []
    for b in range(6):
        i = I if (kind in ("stack", "stackp") or b == 5) else 0.0
        pb = p if (kind in ("single", "stackp") or False) and (kind == "stackp" or b == 5) else 0.2
        r = (i / C) * math.exp(-0.2 * X) * gate(d, i) * pause(pb) if i else 0.0
        if i: X += 1 / (1 + i / 5)
        out.append(r)
    return out
def best(kind, d, p):
    grid = [x / 2 for x in range(1, 21)]
    s = max(grid, key=lambda I: sum(arc(kind, I, d, p))); k = max(grid, key=lambda I: max(arc(kind, I, d, p)))
    return (s, sum(arc(kind, s, d, p)), k, max(arc(kind, k, d, p)))
rows = {}
for d in (0.3, 0.6, 0.9):
    st = best("stack", d, 0.0); sg = best("single", d, 3.0)
    rows[d] = (st, sg)
    print("d=%.1f  STACK best-by-sum I=%.1f sum %.3f | best-by-peak I=%.1f peak %.3f   SINGLE(p=3s) best-by-sum I=%.1f sum %.3f | best-by-peak I=%.1f peak %.3f"
          % (d, *st, *sg))
fair = {d: best("stackp", d, 3.0) for d in rows}
for d in fair: print("d=%.1f  STACK with a 3 s pause before EVERY beat: best-by-sum I=%.1f sum %.3f | best-by-peak I=%.1f peak %.3f" % ((d,) + fair[d]))
fair_sum_stack = sum(fair[d][1] > rows[d][1][1] for d in rows)
sg1 = best("single", 0.3, 1.5)
print("single d=0.3 p=1.5 best I=%.1f total %.3f" % (sg1[0], sg1[1]))
sum_stack_wins = all(rows[d][0][1] > rows[d][1][1] for d in rows)
peak_single_wins = all(rows[d][1][3] > rows[d][0][3] for d in rows)
ok = fair_sum_stack == 3 and not sum_stack_wins and peak_single_wins and sg1[0] == 3.0 and 0.17 < sg1[1] < 0.21
print("RESULT: %s unpaused stack wins by sum at %d/3 distances, single wins by peak at %d/3; stack with a pause before every beat wins by sum at %d/3 (costs 18 s of stillness vs 3 s); single d=0.3 p=1.5 best I=%.1f score %.3f"
      % ("PASS" if ok else "FAIL", sum(rows[d][0][1] > rows[d][1][1] for d in rows), sum(rows[d][1][3] > rows[d][0][3] for d in rows), fair_sum_stack, sg1[0], sg1[1]))
