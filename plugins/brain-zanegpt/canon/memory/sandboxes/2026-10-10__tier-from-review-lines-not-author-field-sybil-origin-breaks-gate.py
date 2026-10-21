# Sandbox: derive trust tier from review lines only (kernel ideas:VERIFICATION/trust/derive-trust-from-review-records-not-author-fields)
# Prediction (before run): author-set tier ignored; same-origin review held; any fail => disputed;
# modeled-audit pass tops out at 'audited' (never 'confirmed'); sybil origins (distinct strings, same person) defeat the origin gate.
def tier(rec):
    lines = rec["reviews"]
    if any(l["verdict"] == "fail" for l in lines): return "disputed"
    if any(l["kind"] == "rebuild" and l["verdict"] == "pass" for l in lines): return "confirmed"
    if any(l["kind"] == "audit" and l["verdict"] == "pass" for l in lines): return "audited"
    return "provisional"

def intake(rec):  # gate: reject new record carrying review lines or a self-set tier
    return not rec["reviews"]

def apply_review(rec, rv):  # gate: hold review whose origin matches record's own
    if rv["origin"] == rec["origin"]: return False
    rec["reviews"].append(rv); return True

def new(origin, claimed_tier=None, reviews=None):
    return {"origin": origin, "tier": claimed_tier, "reviews": reviews or []}

ok = []
# S1 author-set field ignored
r = new("alice", claimed_tier="confirmed"); ok.append(("author field ignored", tier(r) == "provisional"))
# S2 pre-reviewed record rejected at intake
r = new("alice", reviews=[{"origin":"alice","kind":"rebuild","verdict":"pass"}]); ok.append(("prereviewed rejected", intake(r) is False))
# S3 self review held
r = new("alice"); ok.append(("self review held", apply_review(r, {"origin":"alice","kind":"rebuild","verdict":"pass"}) is False and tier(r)=="provisional"))
# S4 tier ladder + fail dominance + modeled audit is not confirmed (E54: easy-half check)
r = new("alice"); apply_review(r, {"origin":"bob","kind":"audit","verdict":"modeled"}); t_mod = tier(r)
apply_review(r, {"origin":"bob","kind":"audit","verdict":"pass"}); t_aud = tier(r)
apply_review(r, {"origin":"carol","kind":"rebuild","verdict":"pass"}); t_con = tier(r)
apply_review(r, {"origin":"dave","kind":"audit","verdict":"fail"}); t_dis = tier(r)
ok.append(("ladder", (t_mod, t_aud, t_con, t_dis) == ("provisional","audited","confirmed","disputed")))
# S5 BREAK: sybil -- alice reviews her own record under origin 'alice2'; gate cannot see it
r = new("alice"); passed = apply_review(r, {"origin":"alice2","kind":"rebuild","verdict":"pass"})
sybil_confirmed = passed and tier(r) == "confirmed"
ok.append(("sybil breaks origin gate (expected True)", sybil_confirmed))
# S6 rebuild on same substrate (copy of author's code) is indistinguishable: tier rule has no substrate field
ok.append(("tier rule has no substrate input", "substrate" not in r["reviews"][0]))
for n, v in ok: print(n, v)
allp = all(v for _, v in ok)
print("RESULT: %s 6 scenarios; fields ignored, ladder provisional>audited>confirmed>disputed holds; sybil origin 'alice2' reaches confirmed (gate boundary)" % ("PASS" if allp else "FAIL"))
