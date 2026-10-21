# Deterministic. Part 1: reaction-pause map derived from captions vs a hand-kept sidecar after a retime.
# Part 2: rank the two recuts on IPM x D1 with seeded LCG samples at several impression budgets.
CAPS = [(0.5, 6.9), (7.3, 15.6), (16.5, 24.0), (24.4, 28.9), (29.3, 39.6), (40.5, 46.5)]
TRIG_CAP = [1, 2, 4, 5]                      # captions holding a reaction trigger

def derived_pauses(caps): return [caps[i][1] for i in TRIG_CAP]          # snap to caption end, derived from the source
SIDECAR = derived_pauses(CAPS)                                          # written by hand once, never regenerated

def split_lines(pauses, caps):
    return sum(1 for p in pauses if any(s < p < e for s, e in caps))

def retime(caps, shift_from, delta):
    return [(s + delta, e + delta) if i >= shift_from else (s, e) for i, (s, e) in enumerate(caps)]

# Part 1: edit 1: caption 2 onward retimed +0.8 s (an intro was lengthened). edit 2: also caption 4 gets 1.2 s longer.
EDIT1 = retime(CAPS, 2, 0.8)
EDIT2 = [(s, e + 1.2) if i == 4 else ((s + 1.2, e + 1.2) if i > 4 else (s, e)) for i, (s, e) in enumerate(retime(CAPS, 2, 0.8))]
rows = {}
for name, caps in (("original", CAPS), ("retime +0.8", EDIT1), ("retime + longer caption", EDIT2)):
    rows[name] = (split_lines(SIDECAR, caps), split_lines(derived_pauses(caps), caps))
    print(f"{name}: sidecar splits {rows[name][0]} of {len(TRIG_CAP)}, derived splits {rows[name][1]}")

# Part 2: true D1 = 0.30 - 0.04 * splits (assumed); conversion rate identical (IPM same). IPM x D1 vs IPM alone.
D1 = {"sidecar": 0.30 - 0.04 * rows["retime + longer caption"][0], "derived": 0.30}
IPM = {"sidecar": 0.0420, "derived": 0.0400}        # sidecar recut slightly higher IPM (the lure) by assumption
def lcg(seed):
    x = seed
    while True:
        x = (1103515245 * x + 12345) % (2 ** 31); yield x / 2 ** 31
def observe(name, n, seed):
    g = lcg(seed); inst = sum(1 for _ in range(n) if next(g) < IPM[name])
    ret = sum(1 for _ in range(inst) if next(g) < D1[name])
    return inst / n * 1000, (ret / inst if inst else 0)
def wins(n, rule):
    w = 0
    for seed in range(1, 41):
        a = observe("sidecar", n, seed * 2 + 1); b = observe("derived", n, seed * 2 + 2)
        sa = a[0] * (a[1] if rule == "ipm_d1" else 1); sb = b[0] * (b[1] if rule == "ipm_d1" else 1)
        w += sb > sa
    return w
table = {n: (wins(n, "ipm"), wins(n, "ipm_d1")) for n in (100, 300, 1000, 5000)}
for n, (a, b) in table.items(): print(f"budget {n}: derived wins of 40 seeds: IPM alone {a}, IPM x D1 {b}")
ok = (rows["original"] == (0, 0) and rows["retime + longer caption"][0] > 0 and all(v[1] == 0 for v in rows.values())
      and table[5000][1] > table[5000][0] and table[100][1] < 30 and table[5000][1] >= 30)
print(f"RESULT: {'PASS' if ok else 'FAIL'} stale sidecar splits {rows['retime + longer caption'][0]}/4 lines after edits vs 0 for derived; derived wins IPM x D1 {table[100][1]}/40 at 100 impressions, {table[1000][1]}/40 at 1000, {table[5000][1]}/40 at 5000 (IPM alone {table[5000][0]}/40)")
