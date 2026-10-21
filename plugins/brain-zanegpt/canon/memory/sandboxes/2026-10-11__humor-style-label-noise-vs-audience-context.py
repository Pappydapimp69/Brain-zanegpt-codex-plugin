"""Sandbox: humor-styles/E1 (max-subscale class unstable, margin matters) x humor/E1 (affiliative safe only on mixed audience).
Prediction (before run): retest class agreement 0.5-0.7; predicting 'safe sender' from the noisy class label errs >=20% on a mixed audience;
gating on a margin >=0.5 SD cuts that error but leaves >=10% unlabeled-or-wrong; in a shared-target in-group the label rule's error
is higher than on a mixed audience even with a PERFECT label (context, not measurement, dominates)."""
import sys
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
s = SEED
def u():
    global s
    s = (1103515245 * s + 12345) & 0x7FFFFFFF
    return s / 0x7FFFFFFF
def g():  # approx normal, sum of 12 uniforms
    return sum(u() for _ in range(12)) - 6
N, NOISE, GEN = 4000, 0.5, 0.6
STY = ["affil", "selfenh", "aggr", "selfdef"]
people = []
for _ in range(N):
    gen = g()
    t = [GEN * gen + (1 - GEN) ** 0.5 * g() for _ in STY]
    people.append(t)
def measure(t): return [x + NOISE * g() for x in t]
def cls(m):
    o = sorted(range(4), key=lambda i: -m[i]); return o[0], m[o[0]] - m[o[1]]
def true_cls(t): return max(range(4), key=lambda i: t[i])
obs1 = [measure(t) for t in people]; obs2 = [measure(t) for t in people]
agree = sum(cls(a)[0] == cls(b)[0] for a, b in zip(obs1, obs2)) / N
print("retest class agreement", round(agree, 3))
# ground truth: sender is 'safe' if their actual jokes land: mixed audience -> aggressive tendency hurts (true aggr > 0.3 SD above affil);
# shared-target in-group -> aggressive lands, so everyone safe except very low affil+aggr (flat).
def safe_mixed(t): return t[2] - t[0] < 0.3
def safe_ingroup(t): return t[0] + t[2] > -1.0
def err(pred_fn, truth_fn, labelfn):
    wrong = lab = 0
    for t, m in zip(people, obs1):
        l = labelfn(t, m)
        if l is None: continue
        lab += 1
        wrong += pred_fn(l) != truth_fn(t)
    return wrong / max(lab, 1), lab / N
rule = lambda c: c != 2   # 'affiliative-ish safe, aggressive risky'
noisy = lambda t, m: cls(m)[0]
perfect = lambda t, m: true_cls(t)
gated = lambda t, m: cls(m)[0] if cls(m)[1] >= 0.5 else None
res = {}
for name, tr in (("mixed", safe_mixed), ("ingroup", safe_ingroup)):
    for ln, lf in (("noisy", noisy), ("perfect", perfect), ("gated", gated)):
        res[(name, ln)] = err(rule, tr, lf)
        print(name, ln, "error %.3f labeled %.3f" % res[(name, ln)])
ok = (0.5 <= agree <= 0.7
      and res[("mixed", "noisy")][0] >= 0.20
      and res[("mixed", "gated")][0] < res[("mixed", "noisy")][0]
      and res[("mixed", "gated")][1] < 0.9
      and res[("ingroup", "perfect")][0] > res[("mixed", "perfect")][0])
print("RESULT: %s retest agreement %.2f; mixed noisy-label error %.3f gated %.3f (labeled %.2f); perfect-label error mixed %.3f vs in-group %.3f" % (
    "PASS" if ok else "FAIL", agree, res[("mixed","noisy")][0], res[("mixed","gated")][0], res[("mixed","gated")][1],
    res[("mixed","perfect")][0], res[("ingroup","perfect")][0]))
