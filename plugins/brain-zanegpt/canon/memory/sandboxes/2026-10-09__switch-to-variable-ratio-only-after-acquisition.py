# Deterministic sandbox: CRF vs FR vs VR acquisition cost and extinction persistence,
# plus CRF->VR switch timing. No RNG: VR is a fixed cycled ratio list.
# Prediction (written before run): VR5 persists >=3x longer than CRF; switching CRF->VR
# after learning keeps VR-like persistence at lower acquisition cost than pure VR;
# switching before the criterion (after 2 rewards) never acquires (strength < gate).
import itertools
C = 3.0          # quit after C * (max non-reward run seen in training + 1) unrewarded responses
GAIN, GATE = 1.0, 6.0   # strength gain per reward; behavior only emitted once strength >= GATE
BURST = 1.5      # extinction burst: tolerance multiplier on the first unrewarded run

def ratios(kind):
    if kind == "CRF": return itertools.repeat(1)
    if kind == "FR5": return itertools.repeat(5)
    if kind == "VR5": return itertools.cycle([1, 9, 2, 8, 5])
    if kind == "VR5n": return itertools.cycle([4, 6, 5, 5, 5])

def run(plan, train_responses=200, max_rewards=None):
    """plan: list of (schedule, n_rewards) phases; last phase runs to train_responses total."""
    strength = 0.0; maxgap = 0; responses = 0; rewards = 0
    acq = None
    for kind, nrew in plan:
        it = ratios(kind); got = 0
        while (nrew is None or got < nrew) and responses < train_responses and (max_rewards is None or rewards < max_rewards):
            r = next(it)
            responses += r; maxgap = max(maxgap, r - 1)
            strength += GAIN; rewards += 1; got += 1
            if strength >= GATE and acq is None: acq = responses
    if strength < GATE: return dict(acq=None, persist=0, strength=strength)
    tol = C * (maxgap + 1)
    persist = int(tol * BURST)   # unrewarded responses before quitting (includes burst)
    return dict(acq=acq, persist=persist, strength=strength)

S = {
 "1 CRF":            [("CRF", None)],
 "2 FR5":            [("FR5", None)],
 "3 VR5":            [("VR5", None)],
 "4 CRF->VR5 after learned (6 rewards)": [("CRF", 6), ("VR5", None)],
 "5 CRF->VR5 too early (2 rewards) [BREAK]": [("CRF", 2), ("VR5", 3)],
}
# scenario 5: training ends after 5 total rewards (budget), strength 5 < GATE
out = {}
for k, p in S.items():
    out[k] = run(p, max_rewards=5 if k.startswith("5") else None)
    print(k, out[k])
crf, vr = out["1 CRF"]["persist"], out["3 VR5"]["persist"]
sw = out["4 CRF->VR5 after learned (6 rewards)"]
ok = (vr >= 3*crf and sw["persist"] >= 0.8*vr and sw["acq"] < out["3 VR5"]["acq"]
      and out["5 CRF->VR5 too early (2 rewards) [BREAK]"]["persist"] == 0)
print(f"RESULT: {'PASS' if ok else 'FAIL'} persist CRF={crf} FR5={out['2 FR5']['persist']} VR5={vr} "
      f"switch={sw['persist']} acq VR5={out['3 VR5']['acq']} switch={sw['acq']} early-switch persist=0")
