"""Model (assumptions stated, not discovered): 12 claims, each with sources {id: (derived_from|None, alias_of|None, fetchable, quotes_claim)}.
BATCH: one pass over claims in order with budget of FETCH_BUDGET fetches; a blocked (unfetchable) primary source aborts the rest of the pass;
       unfetched claims get a recalled 'verified' verdict with no quote. Confidence = number of source names.
ATOMIC: one agent per claim, own budget; a block only loses that claim; verdict needs a verbatim quote; confidence = distinct ROOTS
       (derived_from chains followed with a cycle guard; aliases normalized).
Prediction (before run): atomic files a quote for every claim whose root is fetchable (>= 10/12) vs batch <= 6/12; batch files >= 3 verified
with no quote, atomic 0; the two false echo-chain claims score high (>=3) by name count and low (1) by roots; BREAK 1: a false claim
with 2 independent but equally wrong roots scores 2 (high) by roots - independence is not truth; BREAK 2: an alias pair
counted by raw roots gives 2 where normalized gives 1; a cycle terminates with the guard."""
FETCH_BUDGET = 6

def S(derived=None, alias=None, ok=True, quote=True):
    return dict(derived=derived, alias=alias, ok=ok, quote=quote)

claims = {}
for i in range(1, 9):                       # c1..c8 true, single fetchable primary, plus 1 derivative
    claims[f"c{i}"] = dict(true=True, src={f"p{i}": S(), f"d{i}": S(derived=f"p{i}")})
claims["c3"]["src"]["p3"] = S(ok=False)     # blocked primary (bot detection) on a true claim
claims["c9"] = dict(true=False, src={"w": S(), "f": S(derived="w"), "a": S(derived="f"), "n": S(derived="a")})   # echo chain, one root, false
claims["c10"] = dict(true=False, src={"w2": S(), "b2": S(derived="w2"), "g2": S(derived="b2")})                    # echo chain, false
claims["c11"] = dict(true=False, src={"r1": S(), "r2": S()})                                                         # two independent roots, BOTH wrong
claims["c12"] = dict(true=True, src={"x": S(), "x_mirror": S(alias="x"), "y": S(derived="x_mirror"), "cyc1": S(derived="cyc2"), "cyc2": S(derived="cyc1")})

def root(src, sid, normalize=True, guard=True):
    seen = set()
    while True:
        s = src[sid]
        if normalize and s["alias"]: sid = s["alias"]; continue
        if s["derived"] is None: return sid
        if guard:
            if sid in seen: return "CYCLE"
            seen.add(sid)
        sid = s["derived"]

def primaries(c):
    return [k for k, s in c["src"].items() if s["derived"] is None and s["alias"] is None]

order = list(claims)
# BATCH
batch_quote, batch_noquote, budget, aborted = 0, 0, FETCH_BUDGET, False
for cid in order:
    c = claims[cid]
    if aborted or budget == 0:
        batch_noquote += 1; continue            # recalled verdict, no quote
    budget -= 1
    p = primaries(c)[0]
    if not c["src"][p]["ok"]:
        aborted = True; batch_noquote += 1; continue
    batch_quote += 1
# ATOMIC
atom_quote = atom_lost = 0
for cid in order:
    c = claims[cid]
    got = [p for p in primaries(c) if c["src"][p]["ok"] and c["src"][p]["quote"]]
    if got: atom_quote += 1
    else: atom_lost += 1
print(f"batch: quotes {batch_quote}/12, verified-without-quote {batch_noquote}; atomic: quotes {atom_quote}/12, lost {atom_lost} (stated as unverified)")

def name_conf(c): return len(c["src"])
def root_conf(c, **kw): return len({root(c["src"], k, **kw) for k in c["src"]} - {"CYCLE"})
rows = {cid: (name_conf(claims[cid]), root_conf(claims[cid])) for cid in order}
for cid in ("c9", "c10", "c11", "c12"): print(cid, "names/roots", rows[cid])
raw12 = root_conf(claims["c12"], normalize=False)
print("c12 roots without alias normalization:", raw12, "with:", rows["c12"][1])
try:
    root(claims["c12"]["src"], "cyc1", guard=True); cyc_ok = True
except Exception: cyc_ok = False

ok = (atom_quote >= 10 and batch_quote <= 6 and batch_noquote >= 3
      and rows["c9"][0] >= 3 and rows["c9"][1] == 1 and rows["c10"][0] >= 3 and rows["c10"][1] == 1
      and rows["c11"][1] == 2 and not claims["c11"]["true"]
      and raw12 == 2 and rows["c12"][1] == 1 and cyc_ok)
print(f"RESULT: {'PASS' if ok else 'FAIL'} atomic quotes {atom_quote}/12 vs batch {batch_quote}/12 (batch {batch_noquote} no-quote); false echo claims names/roots {rows['c9']} {rows['c10']}; independent-but-wrong c11 roots {rows['c11'][1]} (high); alias roots raw {raw12} vs normalized {rows['c12'][1]}")
