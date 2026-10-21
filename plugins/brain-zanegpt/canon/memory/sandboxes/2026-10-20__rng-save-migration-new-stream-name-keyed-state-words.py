"""Sandbox: loading an OLD save (state words per stream) into NEW code that adds a stream.
Compares: name-keyed state words, index-keyed state words, counter-based (name,tick) draws.
Deterministic, stdlib only."""
M = 0xFFFFFFFF

def fnv(s):
    h = 2166136261
    for ch in s.encode():
        h = ((h ^ ch) * 16777619) & M
    return h

class Sfc32:
    def __init__(self, seed):
        self.a, self.b, self.c, self.d = 0x9E3779B9, 0x243F6A88, 0xB7E15162, seed & M
        for _ in range(12):
            self.next()
    def next(self):
        t = (self.a + self.b + self.d) & M
        self.d = (self.d + 1) & M
        self.a = self.b ^ (self.b >> 9)
        self.b = (self.c + (self.c << 3)) & M
        self.c = (((self.c << 21) | (self.c >> 11)) & M) + t & M
        return t
    def state(self): return (self.a, self.b, self.c, self.d)
    def load(self, s): self.a, self.b, self.c, self.d = s

def counter_draw(master, name, tick, idx=0):
    x = fnv("%d|%s|%d|%d" % (master, name, tick, idx))
    x ^= x >> 16; x = (x * 0x45D49E3B) & M; x ^= x >> 15
    return x

MASTER, T, N = 1234, 50, 20
OLD = ["A", "B", "C"]
NEW = ["A", "B", "D", "C"]          # D inserted in the middle

def run_named(names, ticks, streams=None):
    st = streams or {n: Sfc32(fnv("%d:%s" % (MASTER, n))) for n in names}
    out = {n: [] for n in names}
    for _ in range(ticks):
        for n in names: out[n].append(st[n].next())
    return st, out

def run_indexed(names, ticks, streams=None):
    st = streams or {i: Sfc32(MASTER + i) for i in range(len(names))}
    out = {n: [] for n in names}
    for _ in range(ticks):
        for i, n in enumerate(names): out[n].append(st[i].next())
    return st, out

results = {}
# Old game: run T ticks, save state words per stream.
st_old_n, _ = run_named(OLD, T)
save_named = {n: st_old_n[n].state() for n in OLD}
st_old_i, _ = run_indexed(OLD, T)
save_indexed = [st_old_i[i].state() for i in range(len(OLD))]

# Reference: what the OLD code would do for the next N ticks (continuation).
ref_old_n = {n: v for n, v in run_named(OLD, T + N)[1].items()}
ref_old_n = {n: v[T:] for n, v in ref_old_n.items()}

# S1: same code, load by name: exact continuation.
st = {n: Sfc32(0) for n in OLD}
for n in OLD: st[n].load(save_named[n])
_, cont = run_named(OLD, N, st)
results["S1 same-code name-keyed load exact"] = all(cont[n] == ref_old_n[n] for n in OLD)

# S2: NEW code (D inserted), old save, name-keyed: A,B,C continue exactly; D fresh.
st = {}
for n in NEW:
    st[n] = Sfc32(fnv("%d:%s" % (MASTER, n)))
    if n in save_named: st[n].load(save_named[n])
_, cont2 = run_named(NEW, N, st)
s2_old_ok = all(cont2[n] == ref_old_n[n] for n in OLD)
results["S2 new-code name-keyed: old streams unchanged"] = s2_old_ok

# S3 (BREAK): is the migrated D equal to what a from-scratch run of NEW code gives for D at tick T..T+N?
fresh_new = run_named(NEW, T + N)[1]
d_match = cont2["D"] == fresh_new["D"][T:]
results["S3 migrated D equals from-scratch D (expected False)"] = d_match

# S4: index-keyed load into NEW code: slot i -> state i of old save (C lands in D's slot, etc.)
st = {i: Sfc32(MASTER + i) for i in range(len(NEW))}
for i in range(len(OLD)): st[i].load(save_indexed[i])
_, cont4 = run_indexed(NEW, N, st)
ref_old_i = run_indexed(OLD, T + N)[1]
ref_old_i = {n: v[T:] for n, v in ref_old_i.items()}
idx_ok = {n: cont4[n] == ref_old_i[n] for n in OLD}
results["S4 index-keyed: old streams unchanged"] = all(idx_ok.values())

# S5: counter-based (name,tick): nothing to save; migrated D at tick T.. equals from-scratch D.
cb_old = {n: [counter_draw(MASTER, n, t) for t in range(T, T + N)] for n in OLD}
cb_new = {n: [counter_draw(MASTER, n, t) for t in range(T, T + N)] for n in NEW}
cb_ok = all(cb_old[n] == cb_new[n] for n in OLD)
cb_fresh = [counter_draw(MASTER, "D", t) for t in range(0, T + N)][T:] == cb_new["D"]
results["S5 counter-based: old unchanged and D equals from-scratch"] = cb_ok and cb_fresh

for k, v in results.items(): print(k, "->", v)
print("index-keyed per-stream ok:", idx_ok)
words_named = 4 * len(NEW)
ok = (results["S1 same-code name-keyed load exact"] and s2_old_ok and not d_match
      and not results["S4 index-keyed: old streams unchanged"] and results["S5 counter-based: old unchanged and D equals from-scratch"])
print("RESULT: %s name-keyed save keeps %d/3 old streams exact but new stream D diverges from a from-scratch run (match=%s); index-keyed keeps %d/3; counter-based keeps all and D matches (%d words saved vs 0)"
      % ("PASS" if ok else "FAIL", sum(1 for n in OLD if cont2[n] == ref_old_n[n]), d_match, sum(idx_ok.values()), words_named))
