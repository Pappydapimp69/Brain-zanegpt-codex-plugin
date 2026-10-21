"""Hand-maintained sidecar (label -> field id) silently loses the D1 field; the ranker ranks IPM*D1.
Three lessons together: collective-reference (sidecars drift silently; test against the real artifact),
rank-ipm-times-d1 (the product only changes the pick when retention opposes conversion), selftest-coverage
(coverage follows code age, so the old sidecar path is the least-tested).
PREDICTION (before run): over 300 deterministic variant sets, dropping D1 silently (missing field read as 1.0
by the ranker) changes the product pick in >= 30% of sets (only where D1 opposes IPM), changes the IPM-only pick
in 0 of 300; a test using a hand-typed stand-in artifact catches the drop in 0 of 300, a test built from the
real artifact catches 300 of 300; and in sets where D1 does NOT oppose IPM (flat D1) the drop changes nothing."""
def make_set(k, flat=False):
    v = []
    for i in range(8):
        ipm = 5 + ((i * 7 + k * 3) % 11)
        d1 = 0.40 if flat else 0.20 + 0.04 * ((i * 5 + k) % 9)
        v.append({"id": i, "ipm": float(ipm), "d1": d1})
    return v
REAL_FORM_FIELDS = {"IPM": "f_ipm", "Day-1 retention": "f_d1"}          # the real upstream artifact
SIDECAR = {"IPM": "f_ipm"}                                              # hand-maintained map lost "Day-1 retention"
STAND_IN_FORM = {"IPM": "f_ipm"}                                        # hand-typed stand-in has the same gap
def read(row, sidecar):
    return row["ipm"], row["d1"] if "Day-1 retention" in sidecar else None
def pick(rows, sidecar, product=True):
    def score(r):
        ipm, d1 = read(r, sidecar)
        return ipm * (d1 if (product and d1 is not None) else 1.0) if product else ipm   # missing d1 read as 1.0
    return max(rows, key=lambda r: (score(r), -r["id"]))["id"]
def derived_sidecar(form): return dict(form)                            # derive from the one real source
N = 300; changed_prod = changed_ipm = changed_flat = 0
for k in range(N):
    rows, flat = make_set(k), make_set(k, flat=True)
    full = derived_sidecar(REAL_FORM_FIELDS)
    changed_prod += pick(rows, SIDECAR) != pick(rows, full)
    changed_ipm += pick(rows, SIDECAR, product=False) != pick(rows, full, product=False)
    changed_flat += pick(flat, SIDECAR) != pick(flat, full)
catch_real = sum(set(REAL_FORM_FIELDS) != set(SIDECAR) for _ in range(N))        # end-to-end: compare to real artifact
catch_stand_in = sum(set(STAND_IN_FORM) != set(SIDECAR) for _ in range(N))        # stand-in drifted the same way
print("product pick changed %d/%d, IPM-only pick changed %d/%d, flat-D1 sets changed %d/%d" % (changed_prod, N, changed_ipm, N, changed_flat, N))
print("drop caught: real-artifact test %d/%d, hand-typed stand-in %d/%d" % (catch_real, N, catch_stand_in, N))

# audit order from the selftest-coverage lesson: audit old, high-reach, never-test-named functions first.
# reach for read()/sidecar = the picks it can change in this run (measured above); others are fixed stand-in counts.
funcs = [("make_set", 2, 0, True), ("derived_sidecar", 2, 300, True), ("read", 40, changed_prod, False),
         ("pick", 30, N, True), ("score", 30, N, False), ("report", 10, 5, False)]   # (name, age_days, reach, named_by_a_test)
order = [n for n, age, reach, named in sorted(funcs, key=lambda f: (f[3], -f[1], -f[2]))]
print("audit order (unnamed first, then oldest, then highest reach):", order)
audit_first = order[0] == "read"
ok = audit_first and changed_prod >= 0.3 * N and changed_ipm == 0 and catch_stand_in == 0 and catch_real == N and changed_flat == 0
print("RESULT: %s audit order puts the sidecar reader first; silent D1 drop flips the product pick in %d/%d sets, IPM-only 0, flat D1 %d; real-artifact test catches %d/%d, hand-typed stand-in %d/%d" % ("PASS" if ok else "FAIL", changed_prod, N, changed_flat, catch_real, N, catch_stand_in, N))
# NOTE: the catch counts are true by construction (the stand-in is defined with the same gap); the measured
# quantities are the pick-flip rates and the audit order.
