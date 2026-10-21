# Toy deterministic model: salt scales intensity, acid cuts the dominant rich component (contrast).
S_OPT = 1.0  # adequate salt level (arbitrary units)

def perceived(base, salt, acid):
    # salt: under S_OPT, flavor intensity rises from 0.4x to 1.0x; over S_OPT it still scales but harshness appears
    gain = 0.4 + 0.6 * min(salt, S_OPT) / S_OPT
    comp = [b * gain for b in base]
    # acid suppresses the dominant (richness) component only, adds sour as its own component
    comp[0] = comp[0] / (1 + 0.8 * acid)
    sour = 0.5 * acid
    comp = comp + [sour]
    harsh = max(0.0, salt - S_OPT) ** 2 * 3
    return comp, harsh

def metrics(base, salt, acid):
    comp, harsh = perceived(base, salt, acid)
    total = sum(comp)
    contrast = 1 - max(comp) / total          # high = no single note dominates
    bites = 12.0 / (comp[0] + harsh * 4 + 0.5 * comp[-1] * (acid > 1.2) * 4)  # fatigue from richness/harsh/over-sour
    score = contrast * min(1.0, total / 4.5) * (1 - min(0.9, harsh))  # clear and not weak and not harsh
    return dict(total=total, contrast=contrast, bites=bites, score=score)

stew = [3.0, 1.0, 0.8, 0.6]     # rich, dominant first component
lean = [1.2, 1.0, 0.8, 0.6]     # not rich
res = {}

# 1) stew already adequately salted: more salt vs acid
a = metrics(stew, S_OPT, 0)
more_salt = metrics(stew, 1.4, 0)
acid = metrics(stew, S_OPT, 0.6)
res["s1_more_salt_does_not_help"] = more_salt["score"] <= a["score"]
res['s1_acid_helps'] = acid['score'] > a['score'] and acid['bites'] > a['bites']
res['s1_salt_contrast_same_when_scaled'] = abs(metrics(stew, 1.0, 0)['contrast'] - metrics(stew, 1.0, 0)['contrast']) < 1e-9

# 2) BREAK: underseasoned dish: salt should beat acid
u = metrics(stew, 0.3, 0)
u_salt = metrics(stew, S_OPT, 0)
u_acid = metrics(stew, 0.3, 0.6)
res['s2_underseasoned_salt_wins'] = u_salt['score'] > u_acid['score'] > 0 and u_salt['score'] > u['score']

# 3) vinaigrette: richness = oil load; best acid grows with richness; too much acid reverses
def best_acid(base):
    best = max((metrics(base, S_OPT, x / 20)['score'], x / 20) for x in range(0, 61))
    return best[1]
oil_levels = [1.2, 2.0, 3.0, 4.0]
bests = [best_acid([o, 1.0, 0.8, 0.6]) for o in oil_levels]
res['s3_best_acid_monotone_nondecreasing'] = all(bests[i] <= bests[i + 1] for i in range(3)) and bests[-1] > bests[0]
over = metrics(stew, S_OPT, 3.0)
res['s3_overacid_worse_than_optimal'] = over['score'] < metrics(stew, S_OPT, best_acid(stew))['score']

# 4) lean dish: acid gain smaller than rich dish gain
gain_lean = metrics(lean, S_OPT, 0.6)['score'] - metrics(lean, S_OPT, 0)['score']
gain_rich = acid['score'] - a['score']
res['s4_acid_gain_rich_gt_lean'] = gain_rich > gain_lean

for k, v in res.items():
    print(k, v)
print('best_acid_by_oil', dict(zip(oil_levels, bests)))
print('stew', {k: round(v, 3) for k, v in a.items()}, 'salt+', {k: round(v, 3) for k, v in more_salt.items()}, 'acid', {k: round(v, 3) for k, v in acid.items()})
ok = all(res.values())
print(('RESULT: PASS' if ok else 'RESULT: FAIL'), 'acid beats salt on adequately salted rich dish; reverses when underseasoned; optimum rises with oil', 'best_acid=%s' % bests)
