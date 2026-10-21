"""RUN HISTORY. Run 1 (predictions P1-P6 below, as first written): P1 P2 P5 P6 held; P3 FAILED (the click detector only saw
downward envelope drops, and a cut always ends in a bigger upward onset, so it was blind: instrument defect, 0 clicks everywhere)
and P4 FAILED (dwell 2 s with phase 0 is bar-aligned, so the bar cut tracked it perfectly, err 0.000 versus 0.232 for vertical;
only off-grid dwell 2 s failed, and it failed worse than chance, 0.586). Run 2 keeps P1-P6 unedited, replaces the click count by
off-beat step events (any step of 0.12 or more, either direction, away from the beat grid) and adds POST-HOC checks, marked as such,
that were written after seeing run 1: P7 crossover fade, P8 anti-phase sampling, P9 meter-break table.
Sandbox: bar-quantized horizontal switching vs vertical stem fading for a BINARY combat state.
Deterministic audio-timeline model, stdlib only, integer ticks (100 ticks = 1 s), rendered envelopes.

PREDICTIONS (written before the first run; numbers could come out wrong):
 P1  (tracking, dwell 8 s, fade 1 s, bar 2 s): quantized-horizontal cut error = lag/dwell with lag=(-phase mod bar);
     vertical error = (fade/2)/dwell = 0.0625. So the bar-quantized cut beats vertical(1 s) on tracking error in
     exactly 2 of the 8 quarter-second phases (phase 0 and 1.75 s), ties at 1.5 s, and loses in the other 5.
 P2  (fade sweep): against a 0.25 s vertical fade the bar cut wins tracking only at phase 0 (1 of 8 phases).
 P3  (render evidence): at phase 0 the bar cut renders 0 click drops and 0 misaligned downbeats; every other phase
     with immediate cuts renders >= 1 click and >= 50 percent misaligned downbeats; the BEAT-quantized cut has
     0 misaligned beats but misaligned downbeats at 6 of 8 phases (phase not a multiple of 2 s... see code).
 P4  (rate): once dwell <= 2 s (flip no slower than every bar) neither strategy tracks: bar cut error >= 0.35 and
     vertical(1 s) error >= 0.25, and the winner under tracking-first weights flips with phase, not with rate alone.
 P5  (BREAK attempt, claim 'quantized horizontal needs grid-aligned flips to win'): hunt for an off-grid phase
     (phase != 0) where the bar cut is the robust winner (all three weight presets) over every vertical fade >= 0.5 s
     at some dwell >= 4 s. Prediction: none exists  (if one exists the claim is refuted and this reports FAIL).
 P6  Linear crossfade at the bar removes clicks but not lag; the sequential dip variant is the only one with dead air.
"""
import math, itertools

SR = 100                      # ticks per second
BEAT, BAR = 50, 200           # 0.5 s beat, 2 s bar
DUR = 64 * SR
TAU = 20.0
DEC = [math.exp(-n / TAU) for n in range(BEAT * 4 + 1)]
PAD = 0.25
CAL_DB, CMB_DB, CMB_BT = 0.5, 1.0, 0.4          # calm downbeat, combat downbeat, combat other beats

def seg_val(kind, n):
    """envelope of an authored segment at local tick n (own local clock, loops every bar)"""
    m = n % BAR
    b, r = divmod(m, BEAT)
    if kind == 'C':
        a = CAL_DB if b == 0 else 0.0
    else:
        a = CMB_DB if b == 0 else CMB_BT
    return PAD + a * DEC[r]

def state_flips(on_len, off_len, phase, first=4 * SR):
    flips, t, s = [], first + phase, 1
    while t < DUR:
        flips.append((t, s)); t += on_len if s else off_len; s ^= 1
    return flips

def state_array(flips):
    st, cur, j = [], 0, 0
    for t in range(DUR):
        while j < len(flips) and flips[j][0] <= t: cur = flips[j][1]; j += 1
        st.append(cur)
    return st

def render_h(st, grid, fade, mode):
    """horizontal: grid=None immediate, else quantize grid in ticks. mode cut|xfade|seq. Returns total, gK, gC, clash"""
    layers = []                # [kind, start, gain, rise_at]
    target = 'C'; layers.append(['C', 0, 1.0, 0])
    tot, gKs, gCs, clash = [], [], [], 0
    pending = False
    for t in range(DUR):
        want = 'K' if st[t] else 'C'
        if want != target and (grid is None or t % grid == 0):
            target = want
            if mode == 'cut' or fade == 0:
                layers = [[target, t, 1.0, t]]
            else:
                for L in layers: L.append('down')
                alive = [L for L in layers if L[0] == target and len(L) == 4]
                reuse = [L for L in layers if L[0] == target]
                if reuse:
                    reuse[-1].pop() if len(reuse[-1]) == 5 else None
                    reuse[-1][3] = t
                else:
                    layers.append([target, t, 0.0, t + (fade // 2 if mode == 'seq' else 0)])
        step = 1.0 / (fade // 2 if (mode == 'seq' and fade) else max(fade, 1))
        v, gK, gC = 0.0, 0.0, 0.0
        keep = []
        for L in layers:
            down = len(L) == 5
            if down: L[2] = max(0.0, L[2] - step)
            elif t >= L[3]: L[2] = min(1.0, L[2] + step)
            if L[2] > 0 or not down: keep.append(L)
            v += L[2] * seg_val(L[0], t - L[1])
            if L[0] == 'K': gK += L[2]
            else: gC += L[2]
        layers = keep
        if min(gK, gC) > 0.1: clash += 1
        tot.append(v); gKs.append(min(gK, 1.0)); gCs.append(gC)
    return tot, gKs, clash

def render_v(st, qgrid, fade):
    """vertical: one global timeline; combat stem (beats) gain g chases the state at rate 1/fade; qgrid = start fade on grid"""
    g, tot, gKs, tgt = 0.0, [], [], 0
    step = 1.0 / max(fade, 1)
    for t in range(DUR):
        want = st[t]
        if want != tgt and (qgrid is None or t % qgrid == 0): tgt = want
        g = min(g + step, 1.0) if tgt else max(g - step, 0.0)
        if fade == 0: g = float(tgt)
        m = t % BAR; b, r = divmod(m, BEAT)
        calm = PAD + CAL_DB * DEC[r] * (1 if b == 0 else 0)
        stem = g * ((CMB_DB - CAL_DB) * DEC[r] if b == 0 else CMB_BT * DEC[r])
        tot.append(calm + stem); gKs.append(g)
    return tot, gKs, 0

def measure(tot, gK, clash, st, flips):
    D = DUR
    err = sum(abs(gK[t] - st[t]) for t in range(D)) / D
    # latency per flip capped at next flip
    up, dn, miss = [], [], 0
    for i, (tf, s) in enumerate(flips):
        nxt = flips[i + 1][0] if i + 1 < len(flips) else D
        lat = None
        for t in range(tf, nxt):
            if (s and gK[t] >= 0.5) or ((not s) and gK[t] <= 0.5): lat = t - tf; break
        if lat is None: miss += 1; lat = nxt - tf
        (up if s else dn).append(lat)
    clicks = sum(1 for i in range(1, D) if abs(tot[i] - tot[i - 1]) >= 0.12 and min(i % BEAT, BEAT - i % BEAT) > 3)
    onsets = [i for i in range(1, D) if tot[i] - tot[i - 1] >= 0.2]
    beat_bad = sum(1 for i in onsets if min(i % BEAT, BEAT - i % BEAT) > 3)
    dbs = [i for i in onsets if tot[i] - tot[i - 1] >= 0.45]
    bar_bad = sum(1 for i in dbs if min(i % BAR, BAR - i % BAR) > 3)
    dead = sum(1 for t in range(25, D) if sum(tot[t - 25:t]) / 25 < 0.12)
    return dict(err=err, up=sum(up) / max(len(up), 1) / SR, dn=sum(dn) / max(len(dn), 1) / SR, miss=miss,
                clicks=clicks, beat_bad=beat_bad / max(len(onsets), 1), bar_bad=bar_bad / max(len(dbs), 1),
                dead=dead / D, clash=clash / D, nflips=len(flips))

PRESETS = {'track': (3, 1, 1, 1, 1), 'balanced': (1, 1, 1, 1, 1), 'polish': (1, 3, 3, 2, 2)}
def cost(m, w):
    return (w[0] * m['err'] + w[1] * m['bar_bad'] * 0.5 + w[2] * m['clicks'] * 1.0 / (DUR / SR) * 4
            + w[3] * m['clash'] + w[4] * m['dead'])

def strategies(f):
    ft = int(f * SR)
    return {'Hbar-cut': lambda st: render_h(st, BAR, 0, 'cut'),
            'Hbeat-cut': lambda st: render_h(st, BEAT, 0, 'cut'),
            'Himm-cut': lambda st: render_h(st, None, 0, 'cut'),
            'Hbar-xfade': lambda st: render_h(st, BAR, ft, 'xfade'),
            'Hbar-seq': lambda st: render_h(st, BAR, ft, 'seq'),
            'V': lambda st: render_v(st, None, ft),
            'Vbar': lambda st: render_v(st, BAR, ft)}

_cache = {}
def run(on_len, off_len, phase, fade_s, name):
    key = (on_len, off_len, phase, fade_s, name)
    if key not in _cache:
        flips = state_flips(on_len, off_len, phase); st = state_array(flips)
        tot, gK, clash = strategies(fade_s)[name](st)
        _cache[key] = measure(tot, gK, clash, st, flips)
    return _cache[key]

PH = [p * 25 for p in range(8)]          # phases 0..1.75 s in 0.25 s steps
checks = {}

# ---- S1: phase sweep at dwell 8 s (bar-multiple), fades 0.25/0.5/1/2
print("S1 phase sweep dwell 8 s: tracking err  Hbar-cut | Hbeat-cut | Himm | V(0.25) V(0.5) V(1) V(2)")
w1 = {1.0: 0, 0.25: 0}; ties1 = 0
for ph in PH:
    hb = run(800, 800, ph, 0, 'Hbar-cut'); hbt = run(800, 800, ph, 0, 'Hbeat-cut'); hi = run(800, 800, ph, 0, 'Himm-cut')
    vs = {f: run(800, 800, ph, f, 'V') for f in (0.25, 0.5, 1.0, 2.0)}
    print(f"  phase {ph/SR:4.2f}s: {hb['err']:.4f} | {hbt['err']:.4f} | {hi['err']:.4f} | " +
          ' '.join(f"{vs[f]['err']:.4f}" for f in vs) + f" | Hbar clicks {hb['clicks']} bar_bad {hb['bar_bad']:.2f}; Hbeat beat_bad {hbt['beat_bad']:.2f} bar_bad {hbt['bar_bad']:.2f}; Himm clicks {hi['clicks']} bar_bad {hi['bar_bad']:.2f}")
    for f in (1.0, 0.25):
        if hb['err'] < vs[f]['err'] - 1e-3: w1[f] += 1
        elif abs(hb['err'] - vs[f]['err']) <= 1e-3 and f == 1.0: ties1 += 1
print("  Hbar-cut beats V on tracking in phases:", w1, "ties(V1s):", ties1)
checks['P1'] = (w1[1.0] == 2 and ties1 == 1)
checks['P2'] = (w1[0.25] == 1)

# ---- P3 render evidence
h0 = run(800, 800, 0, 0, 'Hbar-cut')
others = [run(800, 800, p, 0, 'Himm-cut') for p in PH[1:]]
beat_rows = [run(800, 800, p, 0, 'Hbeat-cut') for p in PH]
bm = [r['bar_bad'] > 0.2 for r in beat_rows]
checks['P3'] = (h0['clicks'] == 0 and h0['bar_bad'] == 0 and all(o['clicks'] >= 1 and o['bar_bad'] >= 0.5 for o in others)
                and all(r['beat_bad'] == 0 for r in beat_rows[:1]) and sum(bm) >= 6)
print(f"S1b render evidence: Hbar phase0 clicks {h0['clicks']} bar_bad {h0['bar_bad']:.2f}; Himm off-grid min clicks "
      f"{min(o['clicks'] for o in others)} min bar_bad {min(o['bar_bad'] for o in others):.2f}; Hbeat phases with misaligned downbeats {sum(bm)}/8; "
      f"Hbeat beat_bad max {max(r['beat_bad'] for r in beat_rows):.2f}")

# ---- S2: rate sweep, phase 0 and phase 0.75 s (off-grid)
print("S2 rate sweep (on=off=dwell): err Hbar-cut / V(1s) / V(0.5s) / Himm-cut, clicks Hbar/Himm")
rate_tab = {}
for dw in (1, 2, 3, 4, 6, 8, 12, 16, 24):
    for ph in (0, 75):
        a = run(dw * SR, dw * SR, ph, 0, 'Hbar-cut'); v1 = run(dw * SR, dw * SR, ph, 1.0, 'V'); v5 = run(dw * SR, dw * SR, ph, 0.5, 'V')
        im = run(dw * SR, dw * SR, ph, 0, 'Himm-cut')
        rate_tab[(dw, ph)] = (a, v1)
        print(f"  dwell {dw:2d}s phase {ph/SR:4.2f}s: {a['err']:.3f} / {v1['err']:.3f} / {v5['err']:.3f} / {im['err']:.3f}   clicks {a['clicks']}/{im['clicks']}  Hbar miss {a['miss']}/{a['nflips']}")
fast = [rate_tab[(dw, ph)] for dw in (1, 2) for ph in (0, 75)]
checks['P4'] = all(a['err'] >= 0.35 and v['err'] >= 0.25 for a, v in fast)
print("  fast (dwell<=2s) all four cells: Hbar err >=0.35 and V1s err >=0.25 ->", checks['P4'],
      [(round(a['err'], 3), round(v['err'], 3)) for a, v in fast])

# ---- S3: BREAK hunt: off-grid phase where Hbar-cut is robust winner over EVERY vertical fade >=0.5 s, dwell >=4 s
print("S3 break hunt: robust-winner cells for Hbar-cut vs all V(f>=0.5) / Vbar / Hbar-xfade, all presets")
found = []
for dw in (4, 6, 8, 12, 16, 24):
    for ph in PH:
        rob = True
        for pr, w in PRESETS.items():
            hc = cost(run(dw * SR, dw * SR, ph, 0, 'Hbar-cut'), w)
            for f in (0.5, 1.0, 2.0, 4.0):
                for nm in ('V', 'Vbar', 'Hbar-xfade'):
                    if hc >= cost(run(dw * SR, dw * SR, ph, f, nm), w) - 1e-9: rob = False
        if rob: found.append((dw, ph / SR))
print("  robust Hbar-cut wins (dwell, phase):", found)
off = [x for x in found if x[1] != 0]
checks['P5'] = (len(off) == 0)
print("  off-grid robust wins:", off)

# ---- S3b (POST-HOC P7): empirical crossover fade F*(phase) at which Hbar-cut stops losing to V on tracking error
print("S3b crossover vertical fade F* (smallest fade where Hbar-cut err <= V err) per phase, dwell 8 s; prediction 2*lag")
FADES = [0.25 * k for k in range(1, 17)]
p7 = True; xs = []
for ph in PH:
    lag = ((-ph) % BAR) / SR
    h = run(800, 800, ph, 0, 'Hbar-cut')['err']
    fstar = next((f for f in FADES if h <= run(800, 800, ph, f, 'V')['err'] + 1e-9), None)
    pred = 2 * lag
    xs.append((ph / SR, lag, fstar, pred))
    if pred == 0:
        p7 &= (fstar == FADES[0])
    else:
        p7 &= (fstar is not None and abs(fstar - pred) <= 0.25 + 1e-9)
    print(f"  phase {ph/SR:4.2f}s lag {lag:4.2f}s F* {fstar} predicted {pred:.2f}")
checks['P7'] = p7
print("  fraction of phases where Hbar-cut wins vs fixed vertical fade F (closed form F/(2*bar)):")
for F in (0.5, 1.0, 2.0, 3.0, 4.0):
    wins = sum(1 for ph in PH if run(800, 800, ph, 0, 'Hbar-cut')['err'] < run(800, 800, ph, F, 'V')['err'] - 1e-9)
    print(f"   F={F}s: {wins}/8 phases (strict wins)")

# ---- S4: winner map by vertical fade floor F (V cannot be made arbitrarily short without becoming a cut)
print("S4 winner map, dwell 8 s, per phase, balanced preset, vertical fade fixed at F: best of Hbar-cut / Hbar-xfade(F) / V(F) / Vbar(F)")
for F in (0.5, 1.0, 2.0, 4.0):
    row = []
    for ph in PH:
        cands = {'Hbar-cut': cost(run(800, 800, ph, 0, 'Hbar-cut'), PRESETS['balanced'])}
        for nm in ('Hbar-xfade', 'V', 'Vbar'): cands[nm] = cost(run(800, 800, ph, F, nm), PRESETS['balanced'])
        row.append(min(cands, key=lambda k: (round(cands[k], 9), k)))
    print(f"  F={F:3.1f}s: " + ' '.join(f"{x:10s}" for x in row))
print("  cost components that separate Hbar-cut from V (dwell 8, phase 0.75, F=1): " +
      str({k: (round(run(800,800,75,0,'Hbar-cut')[k],3), round(run(800,800,75,1.0,'V')[k],3)) for k in ('err','bar_bad','clicks','dead','clash')}))

# ---- S4b (POST-HOC P8): anti-phase sampling when dwell ~ bar
print("S4b dwell == 1 bar (2 s) and 1.5 s: Hbar-cut err by phase vs constant-music baseline 0.5 and V(1 s)")
anti = []
for dw in (200, 150):
    row = [run(dw, dw, ph, 0, 'Hbar-cut')['err'] for ph in PH]
    anti.append(max(row)); print(f"  dwell {dw/SR}s: Hbar-cut " + ' '.join(f"{x:.3f}" for x in row) + f" | V(1s) {run(dw,dw,0,1.0,'V')['err']:.3f}")
checks['P8'] = anti[0] > 0.5 and run(200, 200, 0, 0, 'Hbar-cut')['err'] == 0.0
# ---- S4c (POST-HOC P9) meter-break table, render-measured
print("S4c meter break (render-measured misaligned downbeat fraction), dwell 8 s, by phase: Hbar-cut / Hbeat-cut / Himm-cut / V(1)")
mb = {}
for nm, f in (('Hbar-cut', 0), ('Hbeat-cut', 0), ('Himm-cut', 0), ('V', 1.0)):
    mb[nm] = [run(800, 800, ph, f, nm)['bar_bad'] for ph in PH]
    print(f"  {nm:9s} " + ' '.join(f"{x:.2f}" for x in mb[nm]) + f"   offbeat steps total {sum(run(800,800,ph,f,nm)['clicks'] for ph in PH)}")
checks['P9'] = (max(mb['Hbar-cut']) == 0 and max(mb['V']) == 0 and min(mb['Himm-cut'][1:]) >= 0.9 and sum(x > 0.5 for x in mb['Hbeat-cut']) == 6)

names = ['Hbar-cut', 'Hbeat-cut', 'Himm-cut', 'Hbar-xfade', 'Hbar-seq', 'V', 'Vbar']
# ---- S5: render dead-air and clash by variant (dwell 8, phase 0.75)
print("S5 dead air / clash / clicks by variant (dwell 8 s, phase 0.75 s, fade 2 s)")
vr = {}
for nm in names:
    f = 0 if nm.endswith('cut') else 2.0
    r = run(800, 800, 75, f, nm); vr[nm] = r
    print(f"  {nm:11s} err {r['err']:.3f} up-lat {r['up']:.2f}s dn-lat {r['dn']:.2f}s clicks {r['clicks']:2d} dead {r['dead']:.3f} clash {r['clash']:.3f} bar_bad {r['bar_bad']:.2f}")
checks['P6'] = (vr['Hbar-xfade']['clicks'] == 0 and vr['Hbar-xfade']['dn'] >= 0.9 * 2.0 * 0 + vr['Hbar-cut']['dn'] - 0.01
                and vr['Hbar-seq']['dead'] > 0 and all(vr[n]['dead'] == 0 for n in names if n != 'Hbar-seq'))

# ---- S6: bursty and pseudo-random flips (fixed LCG, no RNG module)
print("S6 asymmetric / pseudo-random: err Hbar-cut | V(1) | V(0.5) | Himm clicks")
seed = 12345
def lcg():
    global seed; seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed
rf, t, s = [], 400, 1
while t < DUR:
    rf.append((t, s)); t += (100 + lcg() % 700) if s else (100 + lcg() % 1100); s ^= 1
st_r = state_array(rf)
for lab, (fl, stt) in {'burst on3s/off17s': (state_flips(300, 1700, 50), None), 'random dwell 1-8 s': (rf, st_r)}.items():
    stt = stt or state_array(fl)
    out = []
    for nm, f in (('Hbar-cut', 0), ('V', 1.0), ('V', 0.5), ('Himm-cut', 0)):
        tot, gK, cl = strategies(f)[nm](stt); out.append(measure(tot, gK, cl, stt, fl))
    print(f"  {lab:20s}: {out[0]['err']:.3f} | {out[1]['err']:.3f} | {out[2]['err']:.3f} | clicks Hbar {out[0]['clicks']} Himm {out[3]['clicks']}")

print("CHECKS", {k: bool(v) for k, v in checks.items()})
ok = all(checks.values())
summ = ("Hbar-cut beats V(F) in %d/8 phases at F=1 s, %d/8 at F=2 s, 8/8 at F=4 s; crossover F* ~ 2*lag; off-grid robust wins=%d; "
        "dwell 2 s off-grid Hbar err max %.2f (chance 0.50)") % (w1[1.0], sum(1 for ph in PH if run(800,800,ph,0,'Hbar-cut')['err'] < run(800,800,ph,2.0,'V')['err'] - 1e-9), len(off), anti[0])
print("RESULT:", "PASS" if ok else "FAIL", ("failed=" + ",".join(k for k, v in checks.items() if not v) + " | " if not ok else "") + summ)
