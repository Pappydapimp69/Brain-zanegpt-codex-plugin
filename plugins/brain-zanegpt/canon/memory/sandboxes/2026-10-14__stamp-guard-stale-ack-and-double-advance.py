"""Does ONE stamped-version guard fix both (A) stale/duplicate acks in client
prediction reconciliation and (B) a click racing a timer into a double scene
advance? Deterministic, stdlib only."""
import itertools

# ---------- A: reconciliation with acks ----------
INPUTS = [1, 1, -1, -1, 1, 1, -1, 1]          # seq i+1 has direction INPUTS[i]
def server_pos(upto):                          # server position after seq<=upto
    return sum(INPUTS[:upto])
def reconcile(ack_order, guard):
    """Client predicted all 8 inputs and keeps a buffer, PRUNED on every applied ack
    to inputs with seq > ack.seq. On ack: pos = server_pos(ack.seq) + sum(buffer).
    guard: ignore acks with seq <= last applied seq."""
    last = 0; buf = list(range(1, len(INPUTS) + 1)); pos = sum(INPUTS)
    for seq in ack_order:
        if guard and seq <= last:
            continue
        last = max(last, seq)
        buf = [q for q in buf if q > seq]
        pos = server_pos(seq) + sum(INPUTS[q - 1] for q in buf)
    return pos

truth = sum(INPUTS)
def count_wrong(orders, guard):
    return sum(1 for o in orders if reconcile(o, guard) != truth)

in_order = [tuple(range(1, 9))]
dup = [tuple(sorted(list(range(1, 9)) + [k])) for k in range(1, 9)]
# a late ack: delivered after later ones
late = []
for a_ in range(1, 8):
    for gap in range(1, 8 - a_ + 1):
        o = [i for i in range(1, 9) if i != a_]
        o.insert(o.index(a_ + gap) + 1, a_)
        late.append(tuple(o))
# note: acks only differ from truth if STALE ack lands last
a_wrong_in = count_wrong(in_order, False)
a_wrong_dup_naive = count_wrong(dup, False)
a_wrong_dup_guard = count_wrong(dup, True)
a_wrong_late_naive = count_wrong(late, False)
a_wrong_late_guard = count_wrong(late, True)
print("A in-order naive wrong %d/%d" % (a_wrong_in, len(in_order)))
print("A duplicate acks naive wrong %d/%d guard wrong %d/%d" % (a_wrong_dup_naive, len(dup), a_wrong_dup_guard, len(dup)))
print("A late acks naive wrong %d/%d guard wrong %d/%d" % (a_wrong_late_naive, len(late), a_wrong_late_guard, len(late)))

# ---------- B: click vs timer double advance ----------
N_SCENES = 6
def run_b(click_times, timer_delay, guard):
    """Scene advances via timer firing timer_delay after the scene begins, and via
    clicks. A click advances and starts a new timer. Returns scenes skipped:
    time-in-scene < 1 tick means a scene was never seen."""
    scene = 0; timers = [(timer_delay, 0)]  # (fire_time, scene_it_was_set_for)
    events = [(t, 'click', None) for t in click_times]
    t = 0; seen_len = {}; start = {0: 0}
    queue = sorted(events)
    all_ev = []
    while True:
        # next event: min of timers and clicks
        cands = [(ft, 'timer', sc) for ft, sc in timers] + [e for e in queue]
        if not cands: break
        cands.sort(key=lambda e: (e[0], 0 if e[1] == 'click' else 1))
        ev = cands[0]
        if ev[1] == 'timer': timers.remove((ev[0], ev[2]))
        else: queue.remove(ev)
        if scene >= N_SCENES - 1: break
        if ev[1] == 'timer' and guard and ev[2] != scene: continue   # stale stamp
        scene += 1; start[scene] = ev[0]
        timers.append((ev[0] + timer_delay, scene))
    seen = [s for s in start]
    return N_SCENES - 1 - (len(seen) - 1) if False else sum(1 for s in range(1, scene) if s in start and False) 

def skips(click_times, delay, guard):
    # count scenes whose dwell time is shorter than 1 tick = effectively skipped
    scene = 0; timers = [(delay, 0)]; clicks = sorted(click_times)
    starts = [0]
    while scene < N_SCENES - 1 and (timers or clicks):
        nxt_t = min([t for t, _ in timers] + clicks)
        if nxt_t in clicks:
            clicks.remove(nxt_t); ev = ('click', None)
        else:
            sc = [s for t, s in timers if t == nxt_t][0]; timers.remove((nxt_t, sc)); ev = ('timer', sc)
        if ev[0] == 'timer' and guard and ev[1] != scene: continue
        scene += 1; starts.append(nxt_t); timers.append((nxt_t + delay, scene))
    dwell = [starts[i+1] - starts[i] for i in range(1, len(starts) - 1)]  # scene 0 excluded: a click at t=0 is a real user advance
    return sum(1 for d in dwell if d < 1), len(dwell)
# a click exactly when the timer fires (same tick), and the queue of clicks at every tick 0..11
naive = guarded = 0; cases = 0
for delay in (3, 4, 5):
    for c in range(0, 12):
        cases += 1
        naive += skips([c], delay, False)[0]
        guarded += skips([c], delay, True)[0]
print("B same-tick/any click vs timer: skipped scenes naive %d guarded %d over %d cases" % (naive, guarded, cases))

# ---------- BREAK: restart resets the counter, a monotonic guard now eats real acks ----------
def restart_case(guard):
    last = 99; pos = 0; applied = 0
    for s in (1, 2, 3):                      # fresh server numbering after restart, client last=99
        if guard and s <= last: continue
        applied += 1
    return applied
print("BREAK restart reset: naive applies %d/3 acks, guard applies %d/3 (guard drops all fresh acks)" % (restart_case(False), restart_case(True)))

ok = (a_wrong_in == 0 and a_wrong_dup_naive == 0 and a_wrong_late_naive > 0
      and a_wrong_late_guard == 0 and naive > 0 and guarded == 0 and restart_case(True) == 0)
print("RESULT: %s A-late naive %d/%d guard %d; A-dup naive %d guard %d; B-skips naive %d guarded %d of %d; restart guard applies %d/3" %
      ("PASS" if ok else "FAIL", a_wrong_late_naive, len(late), a_wrong_late_guard, a_wrong_dup_naive, a_wrong_dup_guard, naive, guarded, cases, restart_case(True)))
