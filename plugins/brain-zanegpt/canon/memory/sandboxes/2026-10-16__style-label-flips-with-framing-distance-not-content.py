# Sandbox: a humor-style profile (2x2 of benign vs injurious, self vs other; label only when
# the top-two margin clears a band) read from the SAME fixed set of gags under different
# framing distances. A gag is 'injurious' when its severity exceeds the framing distance
# (benign-violation: no ok-reason => not benign). Does the label follow the content or the framing?
import random
BAND = 0.15
def gags(seed, n=120):
    r = random.Random(seed)
    return [{"sev": r.choice([1, 1, 2, 2, 3, 4, 5]), "self": r.random() < 0.4} for _ in range(n)]
def profile(g, dist):
    c = {"affiliative": 0, "self-enhancing": 0, "aggressive": 0, "self-defeating": 0}
    for x in g:
        inj = x["sev"] > dist(x)
        key = ("self-defeating" if x["self"] else "aggressive") if inj else ("self-enhancing" if x["self"] else "affiliative")
        c[key] += 1
    return c
def label(c):
    t = sorted(c.items(), key=lambda kv: -kv[1]); n = sum(c.values())
    top, second = t[0], t[1]
    return top[0] if (top[1] - second[1]) / n >= BAND else "abstain"
framings = {"grounded(2)": lambda x: 2, "surreal(5)": lambda x: 5, "matched": lambda x: x["sev"]}
labels = {k: {} for k in framings}
for seed in range(30):
    g = gags(seed)
    for k, d in framings.items():
        l = label(profile(g, d)); labels[k][l] = labels[k].get(l, 0) + 1
for k, v in labels.items():
    print("%-12s %s" % (k, dict(sorted(v.items()))))
# Prediction (before run): over 30 seeds of the same gag mix the grounded framing labels
# mostly injurious (aggressive/self-defeating) in >=15 seeds; surreal(5) labels 0 injurious;
# the label set differs between framings (content identical), so the label follows framing.
inj = lambda v: v.get("aggressive", 0) + v.get("self-defeating", 0)
ok = inj(labels["grounded(2)"]) >= 15 and inj(labels["surreal(5)"]) == 0 and labels["grounded(2)"] != labels["surreal(5)"]
print("RESULT: %s injurious labels grounded=%d surreal=%d matched=%d of 30 seeds; abstain grounded=%d surreal=%d"
      % ("PASS" if ok else "FAIL", inj(labels["grounded(2)"]), inj(labels["surreal(5)"]), inj(labels["matched"]),
         labels["grounded(2)"].get("abstain", 0), labels["surreal(5)"].get("abstain", 0)))
