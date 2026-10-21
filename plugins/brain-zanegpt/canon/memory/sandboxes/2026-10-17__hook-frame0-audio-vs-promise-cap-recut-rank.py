"""Sandbox: does a frame-0 audio hit (film) change which cold-open promise wins when
recuts are ranked by IPM alone vs IPM x D1 (rank-ipm-times-d1) with promise capped at
delivery (cold-open-promise-matches-delivery)?
Prediction (written before first run): IPM x D1 keeps picking promise 0.5 (= delivery)
in all 3 scenarios, because a silent-hook penalty is a multiplier on IPM and D1 does
not move; IPM alone picks 1.0 with frame-0 hits and 0.6 when only the high-promise
(phase-synced audio) recuts are silent. Assumption: the silent-hook cost is
independent of delivery. BREAK scenario: C (silence only on high-promise recuts)."""
PROMISES = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
DELIVERY = 0.5
SILENT_COST = 0.6   # film lesson: silent first second, RMS 0.001 vs 0.20 -> hook lost

def ipm(p, silent):
    return 10.0 * (0.5 + p) * ((1 - SILENT_COST) if silent else 1.0)

def d1(p):
    return 0.40 * (1 - 1.5 * max(0.0, p - DELIVERY))   # linear overpromise penalty

def pick(silent_fn, key):
    return max(PROMISES, key=lambda p: key(p, silent_fn(p)))

scen = {
    "A all recuts have a frame-0 hit": lambda p: False,
    "B all recuts silent first second": lambda p: True,
    "C BREAK: only phase-synced high-promise recuts (p>=0.7) silent": lambda p: p >= 0.7,
}
ok = True
for name, fn in scen.items():
    a = pick(fn, lambda p, s: ipm(p, s))
    b = pick(fn, lambda p, s: ipm(p, s) * d1(p))
    print(f"{name}: IPM-alone={a} IPM*D1={b}")
    ok &= (b == 0.5)
alone = [pick(f, lambda p, s: ipm(p, s)) for f in scen.values()]
print("IPM-alone picks:", alone)
ok &= alone == [1.0, 1.0, 0.6]
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" IPM*D1 picked promise 0.5 in 3/3 scenarios; IPM alone picked {alone}")
