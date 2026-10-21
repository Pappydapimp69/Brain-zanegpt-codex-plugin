"""Sandbox: LRU/FIFO eviction + write invalidation + late-arriving fills (stale race).
Deterministic, stdlib only, no RNG, no real time (a fill lands DELAY events after its miss).
Prediction (written before first run):
 1) no writes: loop of 5 through 5 slots = 95/100 hits for LRU and FIFO; hot set + cold stream through 4 slots LRU 57 vs FIFO 30.
 2) with a write to item 0 every 10 reads on the 5-loop in 5 slots, hits drop for BOTH policies by the same amount (policy still irrelevant on a loop).
 4) BREAK: with delay=0 (fill lands on the next event) I predicted 0 stale reads. [Iteration 1 refuted this: 10 stale, because the next event is the write.]
    Iteration 2 prediction: only an ATOMIC fill (installed inside the read) gives 0 stale, unguarded.
 3) on a trace where a write follows each read of item 0, with fills delayed 3 events, an UNGUARDED cache serves >=1 stale read; a version-GUARDED cache (reject a fill older than the latest invalidation) serves 0 stale reads;
    the guard costs hits (fewer cached fills) but never changes the stale count by policy.
"""
from collections import OrderedDict, deque

class Cache:
    def __init__(self, slots, policy, guarded, delay):
        self.slots, self.policy, self.guarded, self.delay = slots, policy, guarded, delay
        self.d = OrderedDict(); self.order = deque()
        self.store = {}            # backing store: key -> version
        self.inval = {}            # key -> version at last invalidation
        self.pending = []          # (land_at, key, version)
        self.t = 0; self.hits = 0; self.reads = 0; self.stale = 0
    def _land(self):
        keep = []
        for land, k, v in self.pending:
            if land > self.t: keep.append((land, k, v)); continue
            if self.guarded and v < self.inval.get(k, 0): continue   # fill older than an invalidation: drop
            self._put(k, v)
        self.pending = keep
    def _put(self, k, v):
        if k in self.d: self.d[k] = v; return
        if len(self.d) >= self.slots:
            victim = next(iter(self.d)) if self.policy == "LRU" else self.order.popleft()
            if self.policy == "LRU": pass
            self.d.pop(victim)
            if self.policy == "LRU" and victim in self.order: self.order.remove(victim)
        self.d[k] = v; self.order.append(k)
    def write(self, k):
        self.store[k] = self.store.get(k, 0) + 1
        self.inval[k] = self.store[k]
        if k in self.d:
            self.d.pop(k)
            if k in self.order: self.order.remove(k)
        self.t += 1; self._land()
    def read(self, k):
        self.t += 1; self._land(); self.reads += 1
        if k in self.d:
            self.hits += 1
            if self.d[k] < self.store.get(k, 0): self.stale += 1
            if self.policy == "LRU": self.d.move_to_end(k)
        else:
            if self.delay < 0: self._put(k, self.store.get(k, 0))   # atomic fill: no window between fetch and install
            else: self.pending.append((self.t + self.delay, k, self.store.get(k, 0)))

def run(trace, slots, policy, guarded=False, delay=0):
    c = Cache(slots, policy, guarded, delay)
    for op, k in trace:
        (c.read if op == "r" else c.write)(k)
    return c.hits, c.reads, c.stale

loop = [("r", i % 5) for i in range(100)]
hot = []
for r in range(20):
    hot += [("r", 0), ("r", 1), ("r", 2), ("r", 100 + r)]
loopw = []
for i in range(100):
    loopw.append(("r", i % 5))
    if i % 10 == 9: loopw.append(("w", 0))
race = []   # a write to item 0 lands right after each read of item 0, so a miss's fill is in flight when the write happens
for i in range(100):
    race.append(("r", i % 5))
    if i % 5 == 0: race.append(("w", 0))
res = {}
for pol in ("LRU", "FIFO"):
    res[pol] = dict(loop=run(loop, 5, pol)[0], loop4=run(loop, 4, pol)[0], hot=run(hot, 4, pol)[0], loopw=run(loopw, 5, pol)[0])
    ung = run(race, 5, pol, False, 3); gua = run(race, 5, pol, True, 3)
    res[pol]["ung_stale"], res[pol]["gua_stale"] = ung[2], gua[2]
    res[pol]["ung_hits"], res[pol]["gua_hits"] = ung[0], gua[0]
    print(pol, res[pol])
L, F = res["LRU"], res["FIFO"]
c1 = L["loop"] == F["loop"] == 95 and L["loop4"] == F["loop4"] == 0 and L["hot"] == 57 and F["hot"] == 30
c2 = L["loopw"] == F["loopw"] and L["loopw"] < 95
c3 = L["ung_stale"] >= 1 and F["ung_stale"] >= 1 and L["gua_stale"] == F["gua_stale"] == 0 and L["gua_hits"] <= L["ung_hits"]
# BREAK: delay 0 (fills land immediately) -- no race window, so the guard should buy nothing
brk = [run(race, 5, p, False, 0)[2] for p in ("LRU", "FIFO")]
print("BREAK delay=0 unguarded stale:", brk)
atomic = [run(race, 5, p, False, -1)[2] for p in ("LRU", "FIFO")]
print("BREAK atomic fill unguarded stale:", atomic)
c4 = brk == [10, 10] and atomic == [0, 0]
print(("RESULT: PASS" if (c1 and c2 and c3 and c4) else "RESULT: FAIL"),
      f"c1 {c1} c2 {c2} c3 {c3} c4 {c4}; loop hits {L['loop']}, hot LRU/FIFO {L['hot']}/{F['hot']}, writes loop hits {L['loopw']}, stale unguarded {L['ung_stale']}/{F['ung_stale']} guarded {L['gua_stale']}/{F['gua_stale']}")
