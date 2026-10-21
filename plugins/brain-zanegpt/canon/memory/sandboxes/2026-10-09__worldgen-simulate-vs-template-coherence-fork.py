"""Deterministic sandbox: simulate-forward vs template-and-constrain world history,
plus terrain-driven vs independent settlement placement, audited by a timeline checker.
Stdlib only. Seeded LCG, no real timing."""
class R:
    def __init__(s, seed): s.x = seed * 2654435761 % 2**32 or 1
    def n(s, k):
        s.x = (s.x * 1103515245 + 12345) % 2**31
        return (s.x >> 8) % k

N_CIV, TURNS = 6, 40

def simulate(seed):
    r = R(seed); strength = [5 + r.n(6) for _ in range(N_CIV)]; alive = [True]*N_CIV
    ev = []  # (turn, kind, actor, target, cause_idx or None, true_cause)
    for t in range(TURNS):
        for a in range(N_CIV):
            if not alive[a]: continue
            b = r.n(N_CIV)
            if b == a or not alive[b]: continue
            if strength[a] > strength[b] + 2:
                ev.append((t, 'conquer', a, b, None, 'strength'))
                strength[a] += 1; strength[b] -= 3
                if strength[b] <= 0: alive[b] = False; ev.append((t, 'fall', b, b, len(ev)-1, 'defeat'))
    return ev

def template(seed, constrain, kinds=('conquer', 'fall', 'plague', 'prophet')):
    r = R(seed); alive = [True]*N_CIV; ev = []
    for t in range(TURNS):
        for _ in range(3):
            k = kinds[r.n(len(kinds))]; a = r.n(N_CIV); b = r.n(N_CIV)
            if constrain and (not alive[a] or not alive[b] or a == b): continue
            if k == 'fall': b = a; alive[a] = False
            ev.append((t, k, a, b, None, None))
    return ev

def rationalize(ev, thick):
    # attach a connective cause: pick a prior event involving the same actor if thick, else any prior event
    out = []; r = R(99)
    for i, e in enumerate(ev):
        cause = None
        if i:
            prior = [j for j in range(i) if (ev[j][2] in (e[2], e[3]))] if thick else list(range(i))
            if prior: cause = prior[r.n(len(prior))]
        out.append(e[:4] + (cause, e[5]))
    return out

def audit(ev):
    """fact-index + timeline + checker. Returns (state violations, claimed-cause-not-genuine, events)."""
    alive = [True]*N_CIV; viol = fake = 0
    for i, (t, k, a, b, c, true) in enumerate(ev):
        if not alive[a] or not alive[b]: viol += 1      # dead actor/target acts
        if k == 'fall': alive[a] = False
        if c is not None:
            ck = ev[c][1]
            genuine = (true is not None)  # simulator's cause is a real state fact; rationalizer's is only a link
            if not genuine and not (ck == 'conquer' and k == 'fall' and ev[c][3] == a): fake += 1
    return viol, fake, len(ev)

def placement(seed, terrain_driven):
    r = R(seed); W = 24
    river = {(x, 12) for x in range(W)}
    cells = [(x, y) for x in range(W) for y in range(W)]
    near = lambda c: min(abs(c[1]-12), 99) <= 1
    picks = []
    for _ in range(8):
        if terrain_driven:
            cand = sorted([cells[r.n(len(cells))] for _ in range(6)], key=lambda c: abs(c[1]-12))
            picks.append(cand[0])
        else: picks.append(cells[r.n(len(cells))])
    return sum(near(c) for c in picks) / len(picks)

def mean(f, seeds=range(1, 41)):
    v = [f(s) for s in seeds]; return v

# Prediction (before run): simulate -> 0 state violations and 0 non-genuine claimed causes;
# unconstrained thin template -> >0 violations and majority of claimed causes non-genuine;
# constraint removes state violations but NOT fake causes (coherence stays an illusion).
S = {}
sim = [audit(simulate(s)) for s in range(1, 41)]
S['simulate'] = (sum(v for v,_,_ in sim), sum(f for _,f,_ in sim), sum(n for *_,n in sim))
for name, cons, thick in [('tmpl_thin_free', False, False), ('tmpl_thin_constrained', True, False), ('tmpl_thick_constrained', True, True)]:
    res = [audit(rationalize(template(s, cons), thick)) for s in range(1, 41)]
    S[name] = (sum(v for v,_,_ in res), sum(f for _,f,_ in res), sum(n for *_,n in res))
for k, (v, f, n) in S.items(): print(f"{k:24s} state_violations={v:5d} fake_causes={f:5d} events={n}")
td = sum(placement(s, True) for s in range(1, 41)) / 40; rnd = sum(placement(s, False) for s in range(1, 41)) / 40
print(f"settlements within 1 of river: terrain_driven={td:.2f} independent={rnd:.2f}")
ok = (S['simulate'][0] == 0 and S['simulate'][1] == 0 and S['tmpl_thin_free'][0] > 0
      and S['tmpl_thin_constrained'][0] == 0 and S['tmpl_thin_constrained'][1] > 0 and td > rnd * 2)
print("RESULT: " + ("PASS" if ok else "FAIL") + f" sim=({S['simulate'][0]},{S['simulate'][1]}) free_viol={S['tmpl_thin_free'][0]} constrained=({S['tmpl_thin_constrained'][0]},{S['tmpl_thin_constrained'][1]}) river_share {td:.2f} vs {rnd:.2f}")
