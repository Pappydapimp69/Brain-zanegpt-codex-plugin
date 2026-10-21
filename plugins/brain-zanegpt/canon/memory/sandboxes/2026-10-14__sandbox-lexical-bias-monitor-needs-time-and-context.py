# Deterministic expected-count model: slips generated 50/50 lexical/nonlexical,
# a prearticulatory monitor deletes nonword outcomes with prob = attn(context) * min(1, budget/latency).
GEN = 100.0
def outcome(attn, budget_ratio):
    catch = attn * min(1.0, budget_ratio)
    lex = GEN / 2
    non = GEN / 2 * (1 - catch)
    return lex, non
def ratio(a, b): return a / b
ATTN = {"mixed": 0.72, "pure": 0.20}   # fitted so full-time counts match 36:14 and 40:32 shapes
res = {}
for ctx, a in ATTN.items():
    for br in (1.0, 0.5, 0.25, 0.0):
        l, n = outcome(a, br)
        res[(ctx, br)] = ratio(l, n)
        print(f"monitor ctx={ctx} budget={br}: lex={l:.1f} non={n:.1f} ratio={res[(ctx,br)]:.2f}")
# feedback account: fixed bias independent of context and of time
fb = {c: ratio(*outcome(0.5, 1.0)) for c in ATTN}
print("feedback", fb)
ok1 = res[("mixed", 1.0)] > 2.3 and res[("pure", 1.0)] < 1.4       # context sensitivity
ok2 = abs(res[("mixed", 0.0)] - 1.0) < 1e-9 and res[("mixed", 0.25)] < 1.3  # no time -> no bias (BREAK)
ok3 = fb["mixed"] == fb["pure"]                                      # feedback cannot give context gap
print("RESULT: %s monitor ratio mixed %.2f vs pure %.2f; bias gone at budget 0 (%.2f); feedback flat %.2f"
      % ("PASS" if ok1 and ok2 and ok3 else "FAIL", res[("mixed",1.0)], res[("pure",1.0)], res[("mixed",0.0)], fb["mixed"]))
