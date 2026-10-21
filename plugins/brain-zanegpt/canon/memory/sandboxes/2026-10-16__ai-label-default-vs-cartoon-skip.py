"""Toy: label policy for AI videos. Each video has realism 0..10 (10 = photoreal) and a product_exact flag.
Platform detector flags a video as 'needs label' when realism >= DETECT (a parameter, 5 and 7 tried).
Viewer is misled by an unlabeled video when realism >= 6. Policies: label-always, skip-cartoons(<=T), none.
Deterministic grid of 11 realism levels x 2 product flags. Compliance needs BOTH label rule and product accuracy."""
VIDEOS = [(r, p) for r in range(11) for p in (True, False)]
def violations(policy_skip_below, detect, product_gate=True):
    miss_label = misled = product_fail = 0
    for r, p in VIDEOS:
        labeled = r >= policy_skip_below                  # label when at/above the skip threshold
        if (not labeled) and r >= detect: miss_label += 1
        if (not labeled) and r >= 6: misled += 1
        if product_gate and not p: product_fail += 1       # label does not repair a wrong product
    return miss_label, misled, product_fail
out = {}
for name, skip in (("label always", 0), ("skip cartoons below 4", 4), ("skip below 8 (photoreal only)", 8)):
    for detect in (5, 7):
        m, mis, pf = violations(skip, detect)
        out[(skip, detect)] = (m, mis, pf)
        print(f"{name:30s} detector>={detect}: unlabeled-but-flagged {m}/22, viewers misled {mis}/22, wrong-product {pf}/22")
always = out[(0,5)]
ok = (always[0] == 0 and always[1] == 0
      and out[(4,5)][0] == 0 and out[(4,7)][0] == 0       # sensible cartoon skip is safe at either detector
      and out[(8,5)][0] > out[(8,7)][0] > 0       # BREAK: aggressive skip fails against both detectors, worse when stricter (first guess "0 at detector 7" was wrong: realism 7 videos slip)
      and always[2] == 11)                               # label never fixes wrong product
print("RESULT: PASS" if ok else "RESULT: FAIL",
      f"always-label misses {always[0]}; skip<8 vs detector>=5 misses {out[(8,5)][0]}/22 (vs detector>=7 {out[(8,7)][0]}); wrong-product stays {always[2]}/22 under every label policy")
