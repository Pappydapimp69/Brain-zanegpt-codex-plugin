# Enumerate every video as 4 booleans; ground truth from the recorded rules (tiktok-shop/E14): AI allowed if real product
# shown accurately AND AI labelled; claims must be non-prohibited.
from itertools import product
def violates(ai, product_altered, labelled, bad_claim):
    return (ai and product_altered) or (ai and not labelled) or bad_claim
gates = {
 "label-only":   lambda ai, alt, lab, bc: not (ai and not lab),
 "accuracy-only":lambda ai, alt, lab, bc: not (ai and alt),
 "claims-only":  lambda ai, alt, lab, bc: not bc,
 "all-three":    lambda ai, alt, lab, bc: not (ai and not lab) and not (ai and alt) and not bc,
}
vids = list(product([0, 1], repeat=4)); vids = [v for v in vids if not (v[1] and not v[0])]  # altered implies AI
bad = [v for v in vids if violates(*v)]
print("videos", len(vids), "violating", len(bad))
res = {}
for g, f in gates.items():
    passed_bad = sum(1 for v in bad if f(*v)); res[g] = passed_bad
    print(g, "lets through", passed_bad, "of", len(bad), "violations")
# mix-real-and-AI mode: AI used only for scenes/dubbing, so product_altered is 0 by construction
mix = [v for v in vids if not v[1]]; mix_bad = [v for v in mix if violates(*v)]
print("mix mode videos", len(mix), "violating", len(mix_bad))
ok = res["all-three"] == 0 and all(res[g] > 0 for g in ["label-only", "accuracy-only", "claims-only"]) and len(mix_bad) < len(bad)
print("RESULT: %s violations let through label=%d accuracy=%d claims=%d all-three=%d of %d; mix mode %d/%d violating vs %d/%d" % (
  "PASS" if ok else "FAIL", res["label-only"], res["accuracy-only"], res["claims-only"], res["all-three"], len(bad), len(mix_bad), len(mix), len(bad), len(vids)))
