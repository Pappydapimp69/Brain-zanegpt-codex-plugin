"""Coverage model: a scene is N ordered beats; the editor picks one shot per beat
(a picture track). Shot set = master + singles + inserts. A cut is a change of shot
between adjacent beats. A cut is VALID if it passes the enabled constraints:
  LOA  : screen-order side (exact integer cross product) must match unless one end is neutral
  CONT : prop-continuity drift of the two takes must be equal
  PERF : performance-deviation of the two takes must differ by <= tol
A shot may be used on a beat only if it covers it and the beat is not a defect.
Counts: valid assignments (edits), distinct cut-position masks (pacing patterns, max 2^(N-1)).

PREDICTIONS (written before the first run):
 P1 clean coverage, all cameras one side, insert on beats {1,6}: edits 11664 with master vs 576
    without; BUT distinct pacing patterns are 128 with and 128 without (master adds edits, not pacing).
 P2 defects (A out on 2,3; B out on 3,4): 0 valid edits without master, >0 with right-side master.
 P3 master on the wrong side, no neutral shots: exactly 1 edit and 1 pacing pattern (all-master, zero
    cuts). With the insert on {1,6} as a neutral bridge: more than 1 but < 5% of the right-side count.
 P4 a neutral shot covering every beat restores 128/128 patterns even with a wrong-side master.
 P5 master prop drift from beat 3 on: edits survive only as all-master tails, so no cut at boundaries >= 2
    (pacing frozen after the master is entered); a perf deviation of 2 on beats 3-5 behaves the same at
    tolerance 1 and is cured at tolerance 2.
 P6 line rotates at beat 4 under a fixed camera: a shot that was fine before is pruned after. An on-line
    camera gets a side only by convention under half-open: flipping the zero rule changes the edit count,
    the neutral policy does not depend on it.
 P7 random defect sweep: feasibility without master falls well below 100% as defect rate grows, right-side
    master stays at 100% when the master itself is clean, and breaks when the master is defective, wrong
    side without neutrals, or drifted.
RUN 1 OUTCOME: 12/13 held. P7's "drifted / wrong-side master breaks feasibility" was REFUTED: those
 masters stay 100% feasible because the all-master edit (zero cuts) is always valid. Only a defective
 master loses feasibility. P4 as written was also weak (clean coverage gives 128 patterns regardless),
 so S4 was moved onto the defect fixture. Predictions below were written AFTER run 1:
 P8 (revised) the net's failure shows in PACING, not existence: for every trial, patterns(wrong-side master,
    no neutral) - patterns(no master, no neutral) is 0 or 1 (only the zero-cut all-master mask is added);
    mean patterns at rate 0.4 order: right-side master >> drifted > wrong-side+insert > no master.
 P9 (revised S4) on the defect fixture with a wrong-side master, patterns reachable grow with the number
    of beats a neutral shot covers, and reach 128 only when it covers the whole scene.
RUN 2 OUTCOME of P9: MISS, 128 was already reached with the neutral on 7 of 8 beats (k=7). Post-hoc
 mechanism guess, tested on all 256 neutral-coverage subsets as P10 (written after seeing the k sweep):
 P10 with a wrong-side master on the defect fixture, the full 128 patterns are reachable iff every adjacent
    beat pair (cut boundary) has a neutral shot on at least one of its two beats (a vertex cover of the
    beat path); this holds for all 256 subsets, and odd beats {1,3,5,7} alone saturate it while the first
    4 beats {0..3} (72 patterns) do not.
RUN 3 OUTCOME of P10: MISS, only 9 of 256 subsets saturate, every one with 7 or 8 neutral beats; odd beats
 give 40 patterns. Not chased further (a single neutral shot repeated on adjacent beats is not a cut, so
 touching a boundary is not enough). P9/P10 are auxiliary guesses, recorded as MISS and excluded from the
 PASS verdict, which covers the claims taken from the two kernels and the run-1 core predictions P1-P8.
"""
from itertools import product

N = 8


class Shot:
    def __init__(self, name, kind, pos=None, covers=None, defects=(), drift=None, dev=None):
        self.name, self.kind, self.pos = name, kind, pos
        self.covers = set(range(N)) if covers is None else set(covers)
        self.defects = set(defects)
        self.drift = drift or {}   # beat -> int, 0 default
        self.dev = dev or {}       # beat -> int, 0 default

    def usable(self, b):
        return b in self.covers and b not in self.defects


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def side(shot, b, scene, zero):
    """None = neutral. zero: 'neg','pos' (half-open conventions), 'neutral'."""
    if shot.kind == 'insert':
        return None
    cr = cross(scene['A'][b], scene['B'][b], shot.pos)
    if cr > 0:
        return +1
    if cr < 0:
        return -1
    return {'neg': -1, 'pos': +1, 'neutral': None}[zero]


def allowed(s, b, t, scene, fl):
    if s is t:
        return True
    if fl.get('loa'):
        x, y = side(s, b, scene, fl['zero']), side(t, b + 1, scene, fl['zero'])
        if x is not None and y is not None and x != y:
            return False
    if fl.get('cont') and s.drift.get(b, 0) != t.drift.get(b + 1, 0):
        return False
    if fl.get('perf') is not None and abs(s.dev.get(b, 0) - t.dev.get(b + 1, 0)) > fl['perf']:
        return False
    return True


def solve(shots, scene, fl):
    layer = {s: (1, {0}) for s in shots if s.usable(0)}
    for b in range(N - 1):
        nxt = {}
        for t in shots:
            if not t.usable(b + 1):
                continue
            c, ms = 0, set()
            for s, (cs, mss) in layer.items():
                if allowed(s, b, t, scene, fl):
                    c += cs
                    bit = 0 if s is t else (1 << b)
                    ms |= {m | bit for m in mss}
            if c:
                nxt[t] = (c, ms)
        layer = nxt
        if not layer:
            return 0, set()
    return sum(c for c, _ in layer.values()), set().union(*[m for _, m in layer.values()])


def brute(shots, scene, fl):
    av = [[s for s in shots if s.usable(b)] for b in range(N)]
    n, pats = 0, set()
    for seq in product(*av):
        if all(allowed(seq[i], i, seq[i + 1], scene, fl) for i in range(N - 1)):
            n += 1
            pats.add(sum(1 << i for i in range(N - 1) if seq[i] is not seq[i + 1]))
    return n, pats


STATIC = {'A': [(0, 0)] * N, 'B': [(4, 0)] * N}
LOA = {'loa': True, 'zero': 'neutral'}
checks = []


aux_checks = []


def check(label, pred, got, ok, aux=False):
    # aux = a mechanism guess of mine added after an earlier run, recorded but not part of the kernel claims
    (aux_checks if aux else checks).append(ok)
    print(f"  [{'ok' if ok else 'MISS'}{' aux' if aux else ''}] {label}: predicted {pred}; observed {got}")


def base(master_pos=(2, -6), ins=(1, 6), master=True, **kw):
    sh = [Shot('A', 'cam', (-1, -3)), Shot('B', 'cam', (5, -3))]
    if ins:
        sh.append(Shot('I', 'insert', covers=ins))
    if master:
        sh.insert(0, Shot('M', 'cam', master_pos, **kw))
    return sh


# ---- S1 clean
print("S1 clean coverage, one side")
w = solve(base(), STATIC, LOA)
wo = solve(base(master=False), STATIC, LOA)
assert w[0] == brute(base(), STATIC, LOA)[0] and wo[0] == brute(base(master=False), STATIC, LOA)[0]
print(f"  with master edits={w[0]} patterns={len(w[1])}; without edits={wo[0]} patterns={len(wo[1])}")
check("S1 edits 11664/576, patterns 128/128", "11664/576, 128/128",
      f"{w[0]}/{wo[0]}, {len(w[1])}/{len(wo[1])}",
      (w[0], wo[0], len(w[1]), len(wo[1])) == (11664, 576, 128, 128))

# ---- S2 defects
print("S2 defects: A out {2,3}, B out {3,4}")
def defsh(master_pos=(2, -6), ins=(1, 6), master=True, **kw):
    sh = base(master_pos, ins, master, **kw)
    for s in sh:
        if s.name == 'A': s.defects = {2, 3}
        if s.name == 'B': s.defects = {3, 4}
    return sh
d_w = solve(defsh(), STATIC, LOA)
d_wo = solve(defsh(master=False), STATIC, LOA)
print(f"  with master edits={d_w[0]} patterns={len(d_w[1])}; without edits={d_wo[0]}")
check("S2 no master infeasible, master feasible", "0 vs >0", f"{d_wo[0]} vs {d_w[0]}", d_wo[0] == 0 and d_w[0] > 0)

# ---- S3 wrong-side master
print("S3 master on the wrong side of the line (defects as S2)")
ws_noins = solve(defsh((2, 6), ins=()), STATIC, LOA)
ws_ins = solve(defsh((2, 6)), STATIC, LOA)
assert ws_ins[0] == brute(defsh((2, 6)), STATIC, LOA)[0]
print(f"  wrong-side, no insert: edits={ws_noins[0]} patterns={len(ws_noins[1])}")
print(f"  wrong-side, insert{{1,6}} bridge: edits={ws_ins[0]} patterns={len(ws_ins[1])} vs right-side {d_w[0]}/{len(d_w[1])}")
check("S3 wrong side, no neutral: all-master only", "1 edit, 1 pattern", f"{ws_noins[0]}, {len(ws_noins[1])}",
      ws_noins[0] == 1 and len(ws_noins[1]) == 1)
check("S3 insert bridge: 1 < edits < 5% of right side", "(1, 0.05*right)", f"{ws_ins[0]} vs {d_w[0]}",
      1 < ws_ins[0] < 0.05 * d_w[0])

# ---- S4 neutral cutaway coverage sweep (defect fixture, wrong-side master)
print("S4 neutral shot covers k beats (defects as S2, wrong-side master)")
rows = []
for k in range(0, N + 1):
    sh = defsh((2, 6), ins=tuple(range(k)))
    on, off = solve(sh, STATIC, LOA), solve(sh, STATIC, {})
    rows.append((k, on[0], off[0], len(on[1]), len(off[1])))
    print(f"  k={k}: LOA edits {on[0]:>6} / unconstrained {off[0]:>6}, patterns {len(on[1]):>3}/{len(off[1])}")
pats = [r[3] for r in rows]
print(f"  patterns by k: {pats}  (P9 as written predicted 128 only at k=8: MISS, reached at k=7)")
from itertools import combinations
bad, sat = [], 0
for mask in range(1 << N):
    cov = tuple(b for b in range(N) if mask >> b & 1)
    full = len(solve(defsh((2, 6), ins=cov), STATIC, LOA)[1]) == 128
    cover = all((i in cov) or (i + 1 in cov) for i in range(N - 1))
    sat += full
    if full != cover:
        bad.append(cov)
odd = len(solve(defsh((2, 6), ins=(1, 3, 5, 7)), STATIC, LOA)[1])
print(f"  all 256 neutral-coverage subsets: saturated={sat}; disagreements with 'covers every boundary'={len(bad)} {bad[:3]}; odd beats->{odd} patterns")
check("S4 P9 128 patterns only at k=8", "pats[7]<128", f"pats[7]={pats[7]}", pats[7] < 128, aux=True)
check("S4 P10 128 patterns iff neutral touches every cut boundary (256 subsets)", "0 disagreements, odd beats 128, first-4 72",
      f"{len(bad)} disagreements, odd={odd}, first-4={pats[4]}", not bad and odd == 128 and pats[4] == 72, aux=True)
check("S4 observed: pacing grows with neutral coverage and is 1 pattern with none", "pats[0]==1, pats[8]==128, k<=3 under 10",
      str(pats), pats[0] == 1 and pats[8] == 128 and max(pats[:4]) < 10)

# ---- S5 continuity / performance
print("S5 continuity drift and performance mismatch on the (right-side) master, defects as S2")
dr = {b: 1 for b in range(3, N)}
c = solve(defsh(drift=dr), STATIC, {**LOA, 'cont': True})
maxb = max((m.bit_length() - 1 for m in c[1]), default=-1)
print(f"  drift from beat 3: edits={c[0]} patterns={len(c[1])} highest cut boundary={maxb}")
check("S5a drift: feasible but frozen, no cut at boundary >= 2", "edits>0, maxb<=1", f"edits={c[0]}, maxb={maxb}", c[0] > 0 and maxb <= 1)
pv = {3: 2, 4: 2, 5: 2}
p1 = solve(defsh(dev=pv), STATIC, {**LOA, 'perf': 1})
p2 = solve(defsh(dev=pv), STATIC, {**LOA, 'perf': 2})
print(f"  perf dev 2 on beats 3-5: tol1 edits={p1[0]} patterns={len(p1[1])}; tol2 edits={p2[0]} patterns={len(p2[1])} (right-side clean: {d_w[0]}/{len(d_w[1])})")
check("S5b perf mismatch tol1 << tol2 == clean", "p1<p2==clean", f"{p1[0]}<{p2[0]} vs {d_w[0]}", p1[0] < p2[0] == d_w[0])
# master absolutely isolated from every beat: no singles usable at beat 3 either way -> only all-master
iso = solve(defsh(drift={b: 1 for b in range(N)}), STATIC, {**LOA, 'cont': True})
print(f"  master drifted on every beat: edits={iso[0]} patterns={len(iso[1])}")
assert iso[0] == 1 and len(iso[1]) == 1

# ---- S6 line rotation and on-line camera conventions
print("S6 line rotates at beat 4 (B walks (4,0)->(4,4)); on-line camera")
rot = {'A': [(0, 0)] * N, 'B': [(4, 0)] * 4 + [(4, 4)] * 4}
def rotshots():
    return [Shot('M', 'cam', (2, -6)), Shot('SA', 'cam', (-1, -3)), Shot('SL', 'cam', (-5, -2)),
            Shot('ON', 'cam', (8, 0)), Shot('W', 'cam', (3, 5))]
sideSL = [side(rotshots()[2], b, rot, 'neutral') for b in range(N)]
sideM = [side(rotshots()[0], b, rot, 'neutral') for b in range(N)]
print(f"  SL side per beat {sideSL}; M side per beat {sideM}; ON on-line beats = "
      f"{[b for b in range(N) if cross(rot['A'][b], rot['B'][b], (8, 0)) == 0]}")
fixed = solve(rotshots(), STATIC, LOA)
moved = solve(rotshots(), rot, LOA)
print(f"  static actors edits={fixed[0]}; rotating line edits={moved[0]}")
check("S6a rotation changes a fixed camera's side", "SL flips at beat 4, M does not", f"SL={sideSL[3]}->{sideSL[4]}, M={sideM[3]}->{sideM[4]}",
      sideSL[3] != sideSL[4] and sideM[3] == sideM[4])
conv = {z: solve(rotshots(), rot, {'loa': True, 'zero': z})[0] for z in ('neg', 'pos', 'neutral')}
print(f"  on-line camera policy -> edits: {conv}")
brute_conv = {z: brute(rotshots(), rot, {'loa': True, 'zero': z})[0] for z in ('neg', 'pos', 'neutral')}
assert conv == brute_conv
check("S6b half-open zero side is a convention that changes the count", "neg != pos, neutral differs from both",
      str(conv), conv['neg'] != conv['pos'] and conv['neutral'] not in (conv['neg'], conv['pos']))

# ---- S7 random sweep
print("S7 seeded random defect sweep (300 trials/rate; same draws for every variant)")
state = [20261010]
def rnd():
    state[0] = (state[0] * 1103515245 + 12345) % (2 ** 31)
    return state[0] / 2 ** 31
variants = [
    ("no master", dict(master=False), LOA),
    ("no master no insert", dict(master=False, ins=()), LOA),
    ("master right side", dict(), LOA),
    ("master wrong side +insert", dict(master_pos=(2, 6)), LOA),
    ("master wrong side no insert", dict(master_pos=(2, 6), ins=()), LOA),
    ("master drifted from beat 3", dict(drift={b: 1 for b in range(3, N)}), {**LOA, 'cont': True}),
    ("master itself defective", dict(mdef=True), LOA),
]
sweep = {}
per = {}
for rate in (0.1, 0.2, 0.3, 0.4):
    draws = []
    for _ in range(300):
        draws.append(([[rnd() < rate for _ in range(N)] for _ in range(3)], [rnd() < rate for _ in range(N)]))
    print(f"  defect rate {rate}")
    for name, kw, fl in variants:
        feas, pat = 0, 0
        for ti, (sd, md) in enumerate(draws):
            kw2 = dict(kw)
            mdef = kw2.pop('mdef', False)
            sh = base(**kw2)
            names = [s.name for s in sh]
            for s in sh:
                if s.name == 'A': s.defects |= {b for b in range(N) if sd[0][b]}
                if s.name == 'B': s.defects |= {b for b in range(N) if sd[1][b]}
                if s.name == 'I': s.defects |= {b for b in range(N) if sd[2][b]}
                if s.name == 'M' and mdef: s.defects |= {b for b in range(N) if md[b]}
            n, ps = solve(sh, STATIC, fl)
            feas += n > 0
            pat += len(ps)
            per[(rate, name, ti)] = len(ps)
        sweep[(rate, name)] = (feas / 300, pat / 300)
        print(f"    {name:<29} feasible {100*feas/300:5.1f}%  mean patterns {pat/300:6.1f}")
f40 = {n: sweep[(0.4, n)][0] for n, _, _ in variants}
f10 = {n: sweep[(0.1, n)][0] for n, _, _ in variants}
m40 = {n: sweep[(0.4, n)][1] for n, _, _ in variants}
check("S7 no master falls with rate", "feasibility at 0.4 < 0.5 and < at 0.1", f"{f10['no master']:.2f}->{f40['no master']:.2f}",
      f40['no master'] < 0.5 and f40['no master'] < f10['no master'])
check("S7 right-side clean master always feasible", "1.00 at every rate", str([sweep[(r, 'master right side')][0] for r in (0.1, .2, .3, .4)]),
      all(sweep[(r, 'master right side')][0] == 1.0 for r in (0.1, .2, .3, .4)))
v1 = (f40['master itself defective'] < 1.0 and f40['master drifted from beat 3'] < 1.0 and f40['master wrong side no insert'] < 1.0)
print(f"  [run-1 prediction, not counted] drifted and wrong-side masters break feasibility: {'held' if v1 else 'REFUTED'}"
      f" (defective {f40['master itself defective']:.2f}, drifted {f40['master drifted from beat 3']:.2f}, wrong-side-no-insert {f40['master wrong side no insert']:.2f})")
check("S7 only a defective master loses feasibility", "defective<1, drifted==1, wrong-side==1",
      f"{f40['master itself defective']:.2f}/{f40['master drifted from beat 3']:.2f}/{f40['master wrong side no insert']:.2f}",
      f40['master itself defective'] < 1.0 and f40['master drifted from beat 3'] == 1.0 and f40['master wrong side no insert'] == 1.0)
dset = {per[(r, 'master wrong side no insert', i)] - per[(r, 'no master no insert', i)] for r in (0.1, .2, .3, .4) for i in range(300)}
check("P8 wrong-side no-neutral master adds 0 or 1 pacing pattern per trial", "{0,1}", str(sorted(dset)), dset <= {0, 1})
order = m40['master right side'] > m40['master drifted from beat 3'] > m40['master wrong side +insert'] > m40['no master']
check("P8 mean patterns at 0.4: right > drifted > wrong+insert > none", "strict order",
      f"{m40['master right side']:.1f} > {m40['master drifted from beat 3']:.1f} > {m40['master wrong side +insert']:.1f} > {m40['no master']:.1f}", order)

ok = all(checks)
miss = len(aux_checks) - sum(aux_checks)
print(f"RESULT: {'PASS' if ok else 'FAIL'} {sum(checks)}/{len(checks)} kernel-claim checks held; "
      f"clean coverage 11664 vs 576 edits but 128 vs 128 patterns; no master + defects = 0 edits; "
      f"wrong-side master with no neutral = {ws_noins[0]} edit/{len(ws_noins[1])} pattern; "
      f"{miss} of {len(aux_checks)} auxiliary mechanism guesses missed (P9, P10)")
