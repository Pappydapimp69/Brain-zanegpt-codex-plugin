import random
# Two-sided toy rule from the dark-humor kernel (McGraw et al.): severe harm (h>=7) is benign only when distant (d>=7) and gets funnier with distance;
# mild harm (h<=3) is funnier the closer the victim (c) and is flat when c is low; middle harm (4-6) needs d>=4.
# Beat value: severe -> h*d/10 (0 and UNSAFE if d<7); mild -> h*c; middle -> h*0.5 if d>=4 else 0 and UNSAFE.
def value(h, d, c):
    if h >= 7: return (h*d/10, False) if d >= 7 else (0, True)
    if h <= 3: return (h*c, False)
    return (h*0.5, False) if d >= 4 else (0, True)
def card_cap(policy, d, c):
    if policy == "none": return 99
    if policy == "monotone": return d*(1-0.6*c)          # loop-1 fix: distance times closeness penalty
    if policy == "two_sided": return 99 if d >= 7 else (6 if d >= 4 else 3)   # severe gated by distance only; closeness drives mild value
def run(policy, d, c, steps=6, goal=10):
    sched = [min(goal, 1+round(i*(goal-1)/(steps-1))) for i in range(steps)]
    cap = card_cap(policy, d, c); s = u = 0
    for h in sched:
        h = min(h, cap); v, bad = value(max(1, round(h)), d, c); s += v; u += bad
    return s, u
random.seed(11)
cases = [(random.randint(1, 10), random.choice([0.0, .25, .5, .75, 1.0])) for _ in range(400)]
def agg(p, sel):
    s = u = n = 0
    for d, c in cases:
        if sel(d, c): a, b = run(p, d, c); s += a; u += b; n += 1
    return round(s, 1), u, n
slices = {"all": lambda d, c: True, "near+close(d<=3,c>=.75)": lambda d, c: d <= 3 and c >= .75,
          "far+close(d>=8,c>=.75)": lambda d, c: d >= 8 and c >= .75, "near+far-from-victim(d<=3,c<=.25)": lambda d, c: d <= 3 and c <= .25}
res = {p: {k: agg(p, f) for k, f in slices.items()} for p in ("none", "monotone", "two_sided")}
for p, v in res.items(): print(p, {k: f"score={x[0]} unsafe={x[1]}" for k, x in v.items()})
m, t = res["monotone"]["all"], res["two_sided"]["all"]
farclose_m, farclose_t = res["monotone"]["far+close(d>=8,c>=.75)"], res["two_sided"]["far+close(d>=8,c>=.75)"]
ok = t[1] == 0 and m[1] == 0 and t[0] > m[0] and farclose_t[0] > farclose_m[0]
print("RESULT: %s both cards 0 unsafe; two-sided keeps score %.1f vs monotone %.1f (%.0f%% more); at far+close victims %.1f vs %.1f" % ("PASS" if ok else "FAIL", t[0], m[0], 100*(t[0]/m[0]-1), farclose_t[0], farclose_m[0]))
