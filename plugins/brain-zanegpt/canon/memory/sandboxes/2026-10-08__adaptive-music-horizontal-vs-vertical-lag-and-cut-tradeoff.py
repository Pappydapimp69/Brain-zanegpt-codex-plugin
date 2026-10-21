"""Prediction (before run): on a binary combat trace, quantized horizontal switching tracks the state with lag <= 1 bar and zero mid-bar cuts,
while vertical layering with a 4-bar fade lags more than 3 bars; on a continuous sparse trace, horizontal switching produces >= 3 audible cuts
and vertical produces 0; vertical never changes harmony (1 distinct segment) while horizontal uses >= 2; combined (horizontal piece by area,
vertical intensity inside) has 0 cuts on both traces and uses 2 pieces. Built to break: an UNQUANTIZED horizontal switch must produce mid-bar cuts on the
binary trace, and a vertical layer with a 1-bar fade must erase the binary-trace lag gap (refuting 'vertical is too slow for sharp states')."""
BAR = 8  # ticks per bar
T = 16 * BAR
def threat(trace_kind):
    if trace_kind == 'binary':   # enemies appear at tick 37 (mid-bar), leave at 85 (mid-bar)
        return [10 if 37 <= t < 85 else 0 for t in range(T)]
    return [min(10, t // 12) if t < 120 else 10 - (t - 120) // 6 for t in range(T)]  # slow ramp up then down
def decouple(raw):   # separate intensity director: threat score -> tier 0..3 (kernel: discrete tier state machine)
    return [0 if r == 0 else 1 if r < 4 else 2 if r < 8 else 3 for r in raw]
def horizontal(tier, quant):
    seg, cuts, out, pend = 0, 0, [], None
    for t, tr in enumerate(tier):
        want = tr
        if want != seg:
            if quant:
                if t % BAR == 0: seg = want
            else:
                seg = want; cuts += (t % BAR != 0)
        out.append(seg)  # one authored segment per tier
    return out, cuts
def switches_audible(level):  # level jumps of >=2 in one tick = audible 'system' cut
    return sum(abs(level[i] - level[i - 1]) >= 1 for i in range(1, len(level)))
def vertical(tier, fade):
    lv, out = 0.0, []
    for tr in tier:
        lv += max(-3.0 / (fade * BAR), min(3.0 / (fade * BAR), tr - lv)) if fade else (tr - lv)
        out.append(lv)
    return out
def lag(level, tier):  # ticks for level to reach within 0.5 of target after each tier change (sum of worst)
    worst = 0
    for i in range(1, len(tier)):
        if tier[i] != tier[i - 1]:
            for j in range(i, T):
                if abs(level[j] - tier[j]) <= 0.5 or tier[j] != tier[i]: worst = max(worst, j - i); break
    return worst
res = {}
for kind in ('binary', 'continuous'):
    tier = decouple(threat(kind))
    hq, cq = horizontal(tier, True); hu, cu = horizontal(tier, False)
    v4 = vertical(tier, 4); v1 = vertical(tier, 1)
    # combined: piece chosen by area (constant 'area' here => 1 horizontal switch at start), intensity vertical
    comb = vertical(tier, 2)
    res[kind] = dict(hq_lag=lag(hq, tier) , hq_cuts=switches_audible(hq), hu_midbar=cu,
                     v4_lag=lag(v4, tier), v1_lag=lag(v1, tier), v4_cuts=switches_audible(v4), comb_cuts=switches_audible(comb),
                     hq_distinct=len(set(x for x in hq)), v_distinct_harmony=1)
    print(kind, res[kind])
b, c = res['binary'], res['continuous']
ok = (b['hq_lag'] <= BAR and b['hu_midbar'] >= 1 and b['v4_lag'] > 3 * BAR and b['v1_lag'] <= b['hq_lag'] + BAR
      and c['hq_cuts'] >= 3 and c['v4_cuts'] == 0 and c['comb_cuts'] == 0 and b['comb_cuts'] == 0)
print("RESULT:", "PASS" if ok else "FAIL", f"binary hq_lag={b['hq_lag']} v4_lag={b['v4_lag']} v1_lag={b['v1_lag']} unquantized_midbar_cuts={b['hu_midbar']}; continuous hq_cuts={c['hq_cuts']} v4_cuts={c['v4_cuts']} comb_cuts={c['comb_cuts']}")
