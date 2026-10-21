"""Sandbox: ranking two 7s cut-downs of a 12s fixable-fail ad (hook 2s, gameplay 5s, fail 3s, end card 2s).
 B = cut by beats (hook + fail + end card), C = cut by clock (first 7s: hook + gameplay, loses fail and end card).
 Rankers: IPM only; IPM x measured D1; IPM x D1 predicted from a HAND-COPIED sidecar tag `fail_ending`
 (copied from the parent, so stale on C); IPM x D1 predicted from a tag DERIVED from the cut's beats.
 Prediction (before run): the stale-tag ranker picks exactly the same variant as IPM-only in every grid cell;
 derived-tag ranker equals measured ranker in every cell; IPM-only is wrong only where the fail bonus to D1
 outweighs the IPM gap, and with a flat D1 (bonus 0) all four agree. Deterministic, stdlib only."""
BEATS = {"P": ["hook", "gameplay", "fail", "endcard"], "B": ["hook", "fail", "endcard"], "C": ["hook", "gameplay"]}
SIDECAR = {"P": True, "B": True, "C": True}      # hand-copied from the parent when the cut was made

def derived_tag(v): return "fail" in BEATS[v]

def ipm(v, g):
    w = {"hook": 2.0, "gameplay": g, "fail": 1.0, "endcard": 0.8}
    return 0.5 + sum(w[b] for b in BEATS[v])

def d1(v, bonus):
    # fail ending sets the honest expectation the game then meets; a gameplay-only ad promises more than it shows
    return 0.18 + bonus * (1 if derived_tag(v) else 0)

def d1_pred(v, bonus, tag):
    return 0.18 + bonus * (1 if tag(v) else 0)

def pick(score):
    return max(("B", "C"), key=score)

cells = 0; ipm_wrong = 0; stale_eq_ipm = 0; derived_eq_meas = 0; stale_wrong = 0; derived_wrong = 0
flat_agree = True; example = None
for gi in range(10, 31):            # g 1.0 .. 3.0
    g = gi / 10
    for bi in range(0, 21):         # bonus 0 .. 0.20
        b = bi / 100
        cells += 1
        true = pick(lambda v: ipm(v, g) * d1(v, b))
        p_ipm = pick(lambda v: ipm(v, g))
        p_stale = pick(lambda v: ipm(v, g) * d1_pred(v, b, lambda x: SIDECAR[x]))
        p_der = pick(lambda v: ipm(v, g) * d1_pred(v, b, derived_tag))
        ipm_wrong += p_ipm != true
        stale_wrong += p_stale != true
        derived_wrong += p_der != true
        stale_eq_ipm += p_stale == p_ipm
        derived_eq_meas += p_der == true
        if b == 0 and not (true == p_ipm == p_stale == p_der): flat_agree = False
        if example is None and p_ipm != true: example = (g, b, p_ipm, true)
print("cells:", cells)
print("IPM-only wrong vs measured IPM x D1: %d" % ipm_wrong)
print("stale-sidecar ranker wrong: %d, identical to IPM-only: %d" % (stale_wrong, stale_eq_ipm))
print("derived-tag ranker wrong: %d, equal to measured: %d" % (derived_wrong, derived_eq_meas))
print("flat D1 (bonus 0): all four agree =", flat_agree)
print("first cell where IPM-only is wrong (g, bonus, ipm_pick, true_pick):", example)
ok = stale_eq_ipm == cells and derived_eq_meas == cells and flat_agree and ipm_wrong > 0
print("RESULT: %s stale sidecar tag made IPM x D1 identical to IPM-only in %d/%d cells (wrong in %d) while a beats-derived tag matched measured in %d/%d; flat D1 all agree=%s"
      % ("PASS" if ok else "FAIL", stale_eq_ipm, cells, stale_wrong, derived_eq_meas, cells, flat_agree))
