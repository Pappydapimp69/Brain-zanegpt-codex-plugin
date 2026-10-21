"""Does the 'late severity cap must land by the schedule midpoint' deadline survive (a) the habituation model of
escalation-needs-matching-distance/E1 and (b) a swept forgiveness threshold and cap level? Deterministic, stdlib only.
Cover/laugh forms are those of rule-card-severity-cap-flattens-the-distance-dial/E1 (assumed toy forms)."""
import math
SPLIT = 0.3
DS = [i / 10 for i in range(11)]
def laugh(s, b): return s if s <= b else max(0.0, s - 3 * (s - b))
def cover(d, s): return 0.8 - 0.5 * d if s <= SPLIT else 0.2 + 0.7 * d

def sched(n, L, level):                 # go-big i/n for first L beats, then capped at level*i/n
    return [(i / n if i <= L else level * i / n) for i in range(1, n + 1)]

def total(d, ss, habit):
    x, t = 0.0, 0.0
    for s in ss:
        h = math.exp(-0.2 * x) if habit else 1.0
        t += h * laugh(s, cover(d, s))
        x += 1 / (1 + 10 * s / 5)       # E1: X += 1/(1+I/5), I = 10*s
    return t

def window(n, L, level, habit):
    ts = [total(d, sched(n, L, level), habit) for d in DS]
    m = max(ts)
    return sum(1 for t in ts if t >= 0.95 * m)

def lstar(n, thr, level, habit):
    last = None
    for L in range(n + 1):
        if window(n, L, level, habit) >= thr: last = L
        else: break
    return last

res = {}
for habit in (False, True):
    for thr in (5, 7, 9):
        res[(habit, thr)] = [lstar(n, thr, SPLIT * 0.8, habit) for n in (6, 9, 12, 18)]
        print(f"habituation={habit} threshold={thr}: L* for n=6,9,12,18 -> {res[(habit, thr)]}")
lv = {lvl: lstar(12, 7, lvl, True) for lvl in (0.1, 0.2, 0.24, 0.3, 0.4, 0.5)}
print("cap level sweep (n=12, thr 7, habituation):", lv)

base = res[(False, 7)]                                  # midpoint pattern: n/2 +-1 at threshold 7
mid_ok = all(l is not None and abs(l - n / 2) <= 1 for l, n in zip(base, (6, 9, 12, 18)))
shift = res[(False, 5)][2] != res[(False, 9)][2]        # threshold moves the deadline at n=12?
habit_same = res[(True, 7)] == base
print("midpoint holds at thr 7, no habituation:", mid_ok, "| threshold moves L* at n=12:", shift,
      "| habituation leaves L* unchanged:", habit_same)
ok = mid_ok and shift
print(f"RESULT: {'PASS' if ok else 'FAIL'} midpoint@thr7={mid_ok} base L*={base} thr5/thr9 at n=12 = {res[(False,5)][2]}/{res[(False,9)][2]} habituation-unchanged={habit_same} level sweep={lv}")
