"""Sandbox for ideas GAMEDESIGN/definition/define-a-game-by-the-four-clauses-it-must-satisfy.
Claim: a game needs (a) input mutates authoritative state, (b) state has an order the player prefers along,
(c) input->state mapping legible enough to form AND refute a hypothesis, (d) losing is re-enterable;
drop a->film, b->toy, c->slot machine, d->job; (c) is where builds fail and the definition is a triage order.
Also exercised: sandbox-combined-action-resolver/E1 (fan-out writes make state depend on handler order = clause a)
and the-game-prologue/E21 (stale capacity makes a held meter drain = clause b).
Prediction (before run): (1) each ablation fails exactly its own probe (4x4 diagonal), base passes all four;
(2) fan-out defect trips only probe a-determinism, stale-capacity defect trips only probe b-monotone;
(3) a PARTIAL signal (shows variable a only) passes a 'signal exists' check yet a stop-at-first-consistent learner
    converges on a wrong single-term rule; a full signal converges on the true conjunction. Break case = (3).
Deterministic, stdlib only, no RNG.
Iteration 1 outcome: prediction (1) WRONG - ablations leak: drop a also fails b and c, drop b also fails d, drop c also fails b
(the clauses depend on each other). The meter monotone probe also wrongly counted the clamp's own one-time drop. Iteration 2
checks (1') every ablation fails its own probe, (1'') the first-failing clause in order a,b,c,d misattributes drop-c to b while
the order a,c,b,d attributes all four, and measures monotonicity only AFTER the capacity event."""
from itertools import product

TRUE_K, TRUE_M = 2, 0          # hidden rule: gain +1 iff action==2 and state parity==0, else -1
LOSS = -3

def step(cfg, s, score, a, t):
    if cfg.get("mutates", True): s2 = (s + a + 1) % 6
    else: s2 = s
    if not cfg.get("ordered", True): g = 0
    elif not cfg.get("legible", True): g = 1 if (t * 7 + 3) % 5 < 2 else -1       # depends on time, not (s, a)
    elif not cfg.get("mutates", True): g = 1 if t % 3 == 0 else -1                   # scripted: input ignored
    else: g = 1 if (a == TRUE_K and s % 2 == TRUE_M) else -1
    return s2, score + g

def run(cfg, seq):
    s = score = 0; plays = 1
    for t, a in enumerate(seq):
        s, score = step(cfg, s, score, a, t)
        if score <= LOSS:
            if cfg.get("restart", True): s = score = 0; plays += 1
            else: return s, LOSS, plays                   # absorbing loss
    return s, score, plays

SEQS = list(product(range(3), repeat=6))

def probe_a(cfg):      # input must move authoritative state
    return len({run(cfg, q)[:2] for q in SEQS}) > 1
def probe_b(cfg):      # some sequences must be preferred over others
    sc = [run(cfg, q)[1] for q in SEQS]
    return max(sc) > sum(sc) / len(sc)
def probe_c(cfg):      # same (state, action) must give same result every visit (can form AND refute a hypothesis)
    seen = {}
    for q in SEQS:
        s = score = 0
        for t, a in enumerate(q):
            s2, sc2 = step(cfg, s, score, a, t)
            seen.setdefault((s, a), set()).add(sc2 - score)
            s, score = s2, sc2
    return all(len(v) == 1 for v in seen.values())
def probe_d(cfg):      # after a loss the player gets to play again
    return run(cfg, tuple([0] * 12))[2] > 1

PROBES = {"a": probe_a, "b": probe_b, "c": probe_c, "d": probe_d}
BASE = {}
ABL = {"a": {"mutates": False}, "b": {"ordered": False}, "c": {"legible": False}, "d": {"restart": False}}

print("S1 ablation matrix (rows = clause dropped, True = probe passes):")
diag_ok = True; leaks = {}
base_row = {k: f(BASE) for k, f in PROBES.items()}
print("   base      ", base_row)
for clause, cfg in ABL.items():
    row = {k: f(cfg) for k, f in PROBES.items()}
    print(f"   drop {clause}    ", row)
    diag_ok &= (row[clause] is False)
    leaks[clause] = [k for k in PROBES if k != clause and not row[k]]
diag_ok &= all(base_row.values())
def attribute(cfg, order):
    return next((k for k in order if not PROBES[k](cfg)), None)
naive = {c: attribute(cfg, "abcd") for c, cfg in ABL.items()}
better = {c: attribute(cfg, "acbd") for c, cfg in ABL.items()}
print("   leaks (other probes that also fail):", leaks)
print("   first-failing attribution, order a,b,c,d:", naive)
print("   first-failing attribution, order a,c,b,d:", better)
order_ok = all(better[c] == c for c in ABL) and naive["c"] == "b" and all(naive[c] == c for c in "abd")

# --- defects from the memory entries -------------------------------------------------------
def fanout_final(order):                   # action-resolver/E1: one 'talk' command, two role handlers write one modal slot
    modal = None
    handlers = {"shop": lambda: "shop", "quest": lambda: "quest"}
    for r in order: modal = handlers[r]()
    return modal
def probe_a_deterministic(final_fn):       # same input, handler order permuted -> same final state?
    return final_fn(("shop", "quest")) == final_fn(("quest", "shop"))
def resolved_final(order):                 # E1 fix: resolve ONE effect before invoking handlers
    return sorted(order)[0]

def meter(clamp, ticks=260):               # the-game-prologue/E21: capacity shrinks 100->50 at tick 200 while held
    raw, cap, hist = 0.0, 100.0, []
    for t in range(ticks):
        if t == 200:
            cap = 50.0
            if clamp: raw = min(raw, cap)
        fill = raw / cap
        rate = 2.0 * (1 - fill)
        raw += rate
        hist.append(raw)
    return hist
def probe_b_monotone(hist):                # after the capacity event, holding input must not reduce the ordered quantity
    h = hist[201:]
    return all(h[i + 1] >= h[i] for i in range(len(h) - 1))

print("S2 defect triage:")
d1 = (probe_a_deterministic(fanout_final), probe_b_monotone(meter(True)))
d1_fixed = probe_a_deterministic(resolved_final)
d2 = (probe_a_deterministic(resolved_final), probe_b_monotone(meter(False)))
d2_fixed = probe_b_monotone(meter(True))
print(f"   fan-out defect:       a-deterministic={d1[0]} b-monotone={d1[1]}   (fixed a-det={d1_fixed})")
print(f"   stale-capacity defect: a-deterministic={d2[0]} b-monotone={d2[1]}   (fixed b-mono={d2_fixed})")
triage_ok = (d1 == (False, True)) and d1_fixed and (d2 == (True, False)) and d2_fixed

# --- clause c: signal presence vs legibility ----------------------------------------------
HYP = [("a==%d" % k, lambda s, a, k=k: a == k) for k in range(3)] + \
      [("par==%d" % m, lambda s, a, m=m: s % 2 == m) for m in range(2)] + \
      [("a==%d&par==%d" % (k, m), lambda s, a, k=k, m=m: a == k and s % 2 == m) for k in range(3) for m in range(2)]
def truth(s, a): return a == TRUE_K and s % 2 == TRUE_M

def learner(signal, budget=12, stop_early=True):
    """Probe (state, action) pairs; keep hypotheses consistent with outcomes. 'signal' tells which variables
    matter: 'full' -> probes both (a, parity); 'partial' -> probes only varies a at the start state (natural play);
    'none' -> hash outcomes, no consistent hypothesis."""
    alive = list(HYP); s = 0; probes = 0; log = []
    if signal == "full":     plan = [(s0, a) for s0 in (0, 1) for a in range(3)]
    elif signal == "partial": plan = [(0, a) for a in range(3)] + [(0, 2)] * 3
    else:                    plan = [(0, a) for a in range(3)] * 4
    for (s0, a) in plan[:budget]:
        probes += 1
        obs = truth(s0, a) if signal != "none" else (probes * 7 + 3) % 5 < 2
        alive = [(n, f) for n, f in alive if f(s0, a) == obs]
        if stop_early and len(alive) == 1: break
        if stop_early and signal == "partial" and probes >= 3 and alive: break   # 'it feels true'
    return [n for n, _ in alive], probes
print("S3 clause-c legibility, stop-at-first-consistent learner:")
res = {sg: learner(sg) for sg in ("full", "partial", "none")}
for sg, (al, p) in res.items(): print(f"   signal={sg:8s} survivors={al} probes={p}")
signal_exists_check = {"full": True, "partial": True, "none": False}
c_ok = res["full"][0] == ["a==2&par==0"] and res["partial"][0] != ["a==2&par==0"] and \
       "a==2" in res["partial"][0] and res["none"][0] == []

ok = diag_ok and order_ok and triage_ok and c_ok
print("RESULT:", "PASS" if ok else "FAIL",
      f"every ablation fails its own probe={diag_ok}, leaks={leaks}, a-b-c-d order misattributes drop-c to {naive['c']} while a-c-b-d attributes all={order_ok}; fan-out trips a only and stale-capacity trips b only={triage_ok}; "
      f"partial signal survivors={res['partial'][0]} after {res['partial'][1]} probes, full={res['full'][0]} after {res['full'][1]}, none={res['none'][0]}")
