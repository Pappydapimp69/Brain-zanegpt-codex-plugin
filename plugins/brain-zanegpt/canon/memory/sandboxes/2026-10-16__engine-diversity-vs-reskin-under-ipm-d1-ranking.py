# Deterministic: a 20-variant batch, top-4 retired per week by IPM x D1. Fixed engine table, no RNG.
ENG = {"escalation":1.00,"literalism":0.80,"role-reversal":0.70,"conflict":0.90,"anticlimax":0.60,"callback":0.75,"misdirection":0.95,"genre-switch":0.65}
SKIN = [0.00, 0.04, -0.03, 0.02, -0.05]           # per-variant skin effect, cycles
def ipm(engine, k, fatigue):  return ENG[engine] * (1 + SKIN[k % 5]) * fatigue ** k            # k = how many earlier variants used this engine
def d1(engine, fit):  return 0.30 * (1 + fit * (ENG[engine] - 0.8))                          # retention follows engine fit by 'fit'
def batch(engines, n=20):
    cnt = {}; out = []
    for i in range(n):
        e = engines[i % len(engines)]; k = cnt.get(e, 0); cnt[e] = k + 1; out.append((e, k)); 
    return out
def score(b, fatigue, fit, rule):
    return [ipm(e, k, fatigue) * (d1(e, fit) if rule == "ipm*d1" else 1) for e, k in b]
def top4(b, fatigue, fit, rule):
    s = sorted(score(b, fatigue, fit, rule), reverse=True)[:4]; return sum(s)
same = batch(["escalation"]); diverse = batch(list(ENG))
res = {}
for f in (1.0, 0.95, 0.90, 0.85, 0.75):
    res[f] = (round(top4(same, f, 1, "ipm*d1"), 3), round(top4(diverse, f, 1, "ipm*d1"), 3), round(top4(same, f, 1, "ipm"), 3), round(top4(diverse, f, 1, "ipm"), 3))
    print("fatigue/repeat", f, "(same-engine, diverse, same ipm-only, diverse ipm-only)", res[f])
# crossover fatigue where diverse overtakes the best-engine reskin
lo, hi = 0.5, 1.0
for _ in range(50):
    m = (lo + hi) / 2
    if top4(diverse, m, 1, "ipm*d1") > top4(same, m, 1, "ipm*d1"): lo = m
    else: hi = m
cross = round(hi, 3)
# BREAK: if the approved engine is NOT the best (weak engine reskinned), diversity should win at no fatigue
weak = batch(["anticlimax"]); wk = (round(top4(weak, 1.0, 1, "ipm*d1"), 3), round(top4(diverse, 1.0, 1, "ipm*d1"), 3))
print("crossover fatigue", cross, "weak-engine reskin vs diverse at no fatigue", wk)
ok = res[1.0][0] >= res[1.0][1] and res[0.75][1] > res[0.75][0] and 0.8 < cross < 1.0 and wk[1] > wk[0]
print("RESULT: %s reskinning the best engine beats a diverse batch at fatigue 1.0 (%s vs %s) but loses once per-repeat decay passes %.3f (at 0.75: %s vs %s); reskinning a weak engine loses even with no fatigue (%s vs %s)"
      % ("PASS" if ok else "FAIL", res[1.0][0], res[1.0][1], cross, res[0.75][0], res[0.75][1], wk[0], wk[1]))
