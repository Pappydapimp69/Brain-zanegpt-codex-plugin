"""Sandbox: Wason 2-4-6 rule discovery as a deterministic hypothesis-elimination model.
Kernels exercised: DECISION-MAKING/confirmation-bias/wason-2-4-6-rule-discovery-task,
DEBUGGING/cognitive-bias/confirmation-bias/confirmation-bias-makes-a-hypothesis-hard-to-abandon,
TESTING/property-based/generation-and-shrinking (counterexample search by ordered enumeration, shrunk to smallest).
Learner holds the narrowest rule consistent with the data so far; no RNG, fixed enumeration order."""
from itertools import product
N = 14
GRID = [t for t in product(range(1, N+1), repeat=3)]
RULES = {
 "step2":      lambda a,b,c: b-a==2 and c-b==2,
 "even_asc":   lambda a,b,c: a<b<c and a%2==0 and b%2==0 and c%2==0,
 "any_AP_asc": lambda a,b,c: a<b<c and b-a==c-b,
 "asc":        lambda a,b,c: a<b<c,
 "nondesc":    lambda a,b,c: a<=b<=c,
}
EXT = {k: frozenset(t for t in GRID if f(*t)) for k, f in RULES.items()}
START = (2,4,6)

def narrowest(data):
    ok = [k for k in RULES if all(RULES[k](*t) == y for t, y in data)]
    return min(ok, key=lambda k: (len(EXT[k]), k))

def run(hidden, strategy, n_tests=10):
    data = [(START, True)]; hyp = narrowest(data); yes = 0; seen = {START}
    for i in range(n_tests):
        pos = strategy == "pos" or (strategy == "mixed" and i % 2 == 0)
        near = strategy == "near" or (strategy == "mixed" and i % 2 == 1)
        cand = [t for t in GRID if t not in seen and (RULES[hyp](*t) == pos)]
        if not cand: break
        if near:                          # near-miss: violator closest (L1) to the hypothesis's own extension
            ext = EXT[hyp]
            cand.sort(key=lambda t: (min(sum(abs(x-y) for x, y in zip(t, e)) for e in ext), t))
        elif not pos:                     # naive negative test: smallest-sum violator of hyp
            cand.sort(key=lambda t: (sum(t), t))
        t = cand[0]; seen.add(t)
        y = RULES[hidden](*t); yes += y
        data.append((t, y)); hyp = narrowest(data)
    return hyp, yes

hiddens = ["asc", "nondesc", "any_AP_asc", "even_asc", "step2"]
table = {}
for h in hiddens:
    for s in ("pos", "neg", "near", "mixed"):
        hyp, yes = run(h, s)
        table[(h, s)] = (hyp == h, hyp, yes)
        print(f"hidden={h:10s} strategy={s:5s} announced={hyp:10s} correct={hyp==h} yes_answers={yes}")

# S1 headline: hidden=asc (the real Wason rule): pos-only never revises and gets all-yes; neg-only finds it
s1 = (not table[("asc","pos")][0]) and table[("asc","pos")][1] == "step2" and table[("asc","pos")][2] >= 9 and table[("asc","near")][0]
# S2 mixed (alternating positive and near-miss) finds asc; NAIVE negative tests do NOT (the break: disconfirmation must be a near miss)
s2 = table[("asc","mixed")][0] and not table[("asc","neg")][0]
naive_fail = [h for h in hiddens if h != "step2" and not table[(h,"neg")][0]]
print("naive smallest-violator negative tests fail for:", naive_fail)
# S3 BREAK: when hidden is NARROWER than the hypothesis or equal, positive testing is enough (even_asc, step2, any_AP? )
narrow = [h for h in hiddens if table[(h,"pos")][0]]
wide_fail = [h for h in hiddens if not table[(h,"pos")][0]]
print("positive-only correct for:", narrow, "| fails for:", wide_fail)
s3 = "step2" in narrow and "asc" in wide_fail and "nondesc" in wide_fail
# S4 property-based counterexample search: smallest triple on which the held hypothesis (step2) and the hidden asc rule disagree
ce = min((t for t in GRID if RULES["step2"](*t) != RULES["asc"](*t)), key=lambda t: (sum(t), t))
ce_neg = min((t for t in GRID if not RULES["step2"](*t) and RULES["asc"](*t)), key=lambda t: (sum(t), t))
print("S4 smallest disagreement triple (hypothesis says no, truth says yes):", ce_neg, "- found by a NEGATIVE test only; any positive test of step2 passes both")
s4 = ce_neg == (1,2,3) and all(RULES["asc"](*t) for t in GRID if RULES["step2"](*t))
checks = [s1, s2, s3, s4]
print("checks:", checks)
print("RESULT:", "PASS" if all(checks) else "FAIL",
 f"hidden=asc (prediction: neg finds it; refuted for naive neg, held for near-miss): pos-only announced {table[('asc','pos')][1]} after {table[('asc','pos')][2]}/10 yes, naive-neg correct={table[('asc','neg')][0]}, near-miss correct={table[('asc','near')][0]}, mixed correct={s2}; positive-only correct only when hidden is not wider than the hypothesis: {narrow}; wrong for {wide_fail}; smallest negative-test counterexample {ce_neg}")
