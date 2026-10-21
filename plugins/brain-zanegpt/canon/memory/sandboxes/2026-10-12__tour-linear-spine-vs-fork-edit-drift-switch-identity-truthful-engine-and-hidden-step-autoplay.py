"""Prediction (written before the first run), a 5-step tour link/query/graph/mine/sync driven by a real mini state machine
with an early binary mode choice (local or full):
 P1 screen count does NOT favour the spine: with k=1 a fork has 5+4=9 screens (the local tour omits the graph step) against
    10 for the spine, so 'a fork multiplies the testing surface' is not about screen counts.
 P2 the cost shows up as edit drift: after editing the copy of 3 shared steps in the primary tour only, a fork leaves
    (2^k - 1)*3 stale screens (3, 9, 21 for k=1, 2, 3); the spine leaves 0.
 P3 a mid-tour mode switch by screen POSITION lands on a different step in the fork for every position at or after the
    omitted step (I predict 3 mismatched positions), and on the same step in the spine (0).
 P4 spine screens built from the engine's own result text match the engine on 10/10 cells; a scripted fake hard error for
    sync in local mode mismatches the engine on 1 cell.
 P5 (built to BREAK 'compare final states'): an auto-play that adds a hidden extra sync after mine has the SAME final state
    as the manual drive in local mode (nothing is pushed either way) but a DIFFERENT final state in full mode; only a trace
    comparison catches the hidden step in both modes."""
STEPS = ["link", "query", "graph", "mine", "sync"]

class Engine:
    def __init__(self): self.s = {"mode": None, "mined": 0, "pushed": 0}; self.trace = []
    def do(self, step, mode=None):
        s = self.s; self.trace.append(step)
        if step == "link": s["mode"] = mode; return f"linked ({mode})"
        if step == "query": return "3 hits"
        if step == "graph": return "graph: 4 edges" if s["mode"] == "full" else "needs full mode"
        if step == "mine": s["mined"] = 2; return "2 proposals drafted"
        if step == "sync":
            if s["mode"] == "full": s["pushed"] = s["mined"]; return f"pushed {s['mined']}"
            return "synced locally, nothing pushed"

def spine_screens(mode, fake=False):
    e = Engine(); out = []
    for st in STEPS:
        r = e.do(st, mode)
        shown = r
        if fake and st == "sync" and mode == "local": shown = "ERROR 500: push failed"
        out.append((st, f"[{mode}] {shown}", r))
    return out

def fork_tours(k):
    """2^k tours; a tour omits the graph step unless its mode bit says full."""
    tours = []
    for bits in range(2 ** k):
        full = bits & 1
        tours.append([s for s in STEPS if full or s != "graph"])
    return tours

ok_all = {}
t1 = fork_tours(1)
fork_screens = sum(len(t) for t in t1); spine_n = len(STEPS) * 2
ok_all["P1"] = (fork_screens, spine_n) == (9, 10)
print("P1 fork screens", fork_screens, "spine screens", spine_n)

EDIT = {"link", "query", "sync"}
stale = {}
for k in (1, 2, 3):
    tours = fork_tours(k)
    stale[k] = sum(1 for i, t in enumerate(tours) if i != 0 for s in t if s in EDIT)
print("P2 stale fork screens", stale, "spine 0")
ok_all["P2"] = stale == {1: 3, 2: 9, 3: 21}

local, full = fork_tours(1)[0], fork_tours(1)[1]
mismatch_fork = sum(1 for pos in range(len(local)) if local[pos] != full[pos])
spine_mismatch = sum(1 for pos in range(len(STEPS)) if STEPS[pos] != STEPS[pos])
print("P3 positional mismatches fork", mismatch_fork, "spine", spine_mismatch)
ok_all["P3"] = (mismatch_fork, spine_mismatch) == (3, 0)

cells = []; fake_bad = 0
for mode in ("local", "full"):
    for (st, shown, truth) in spine_screens(mode):
        cells.append(shown.endswith(truth))
    for (st, shown, truth) in spine_screens(mode, fake=True):
        fake_bad += not shown.endswith(truth)
print("P4 spine matches", sum(cells), "/", len(cells), "fake mismatches", fake_bad)
ok_all["P4"] = sum(cells) == 10 and fake_bad == 1

def manual(mode):
    e = Engine()
    for st in STEPS: e.do(st, mode)
    return e
def auto_hidden(mode):
    e = Engine()
    for st in STEPS:
        e.do(st, mode)
        if st == "mine": e.do("sync")
    return e
res = {}
for mode in ("local", "full"):
    m, a = manual(mode), auto_hidden(mode)
    res[mode] = (m.s == a.s, m.trace == a.trace)
    print("P5", mode, "final state equal", m.s == a.s, "trace equal", m.trace == a.trace, m.s, a.s)
ok_all["P5"] = res["local"] == (True, False) and res["full"] == (False, False)   # as predicted: full state differs
# observed (post-hoc): the hidden sync is idempotent here (the later sync pushes the same 2), so full-mode state ALSO matched
print("predictions:", ", ".join(f"{k}={'held' if v else 'MISSED'}" for k, v in ok_all.items()))
n = sum(ok_all.values())
print("RESULT:", "PASS" if n == len(ok_all) else "FAIL",
      f"{n}/{len(ok_all)} predictions held; fork screens {fork_screens} vs spine {spine_n}; stale {stale}; positional mismatches {mismatch_fork} vs 0; "
      f"spine truthful 10/10, fake mismatches {fake_bad}; hidden-sync state equal local {res['local'][0]} full {res['full'][0]}, trace equal local {res['local'][1]} full {res['full'][1]}")
