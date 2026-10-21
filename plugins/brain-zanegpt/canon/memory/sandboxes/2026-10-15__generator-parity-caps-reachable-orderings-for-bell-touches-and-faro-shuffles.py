"""Sandbox: change-ringing parity kernel (bobs-only Plain Bob Minor stops at 360 of 720)
x brainwork/E216 (plain-course row counts) x zanegpt/E11 (faro shuffles). Is "check the
parity of your generators before searching" a cross-domain rule? Deterministic, stdlib."""
from math import factorial
def parity(p):  # 0 even, 1 odd
    seen, cyc = set(), 0
    for i in range(len(p)):
        if i not in seen:
            cyc += 1; j = i
            while j not in seen: seen.add(j); j = p[j]
    return (len(p) - cyc) % 2
def compose(p, q): return tuple(p[i] for i in q)   # apply q's positions to p's row

# --- bells: place notation -> change permutations
def change(n, places):
    row, i = list(range(n)), 0
    while i < n:
        if (i + 1) in places or i + 1 >= n: i += 1; continue
        row[i], row[i + 1] = row[i + 1], row[i]; i += 2
    return tuple(row)
def lead(n, notation, lead_end):
    seq = []
    for pn in notation: seq.append(change(n, set() if pn == "x" else {int(c) for c in pn}))
    seq.append(change(n, {int(c) for c in lead_end}))
    return seq
def apply_lead(row, changes):
    rows = []
    for ch in changes: row = compose(row, ch); rows.append(row)
    return rows
def plain_course(n, notation, le):
    rows, row = set(), tuple(range(n)); rnds = row; L = lead(n, notation, le)
    while True:
        rr = apply_lead(row, L); rows.update(rr); row = rr[-1]
        if row == rnds: return len(rows)
def reachable_rows(n, notation, ends):
    leads = [lead(n, notation, e) for e in ends]; start = tuple(range(n))
    heads, todo, rows = {start}, [start], set()
    while todo:
        h = todo.pop()
        for L in leads:
            rr = apply_lead(h, L); rows.update(rr)
            if rr[-1] not in heads: heads.add(rr[-1]); todo.append(rr[-1])
    return len(rows)
minor = ["x", "16"] * 5 + ["x"]
pc_minor = plain_course(6, minor, "12")
pc_minimus = plain_course(4, ["x", "14", "x", "14", "x", "14", "x"], "12")
pc_doubles = plain_course(5, ["x", "15"] * 4 + ["x"], "125")
le_par = {e: parity(change(6, {int(c) for c in e})) for e in ("12", "14", "1234")}
r_bobs = reachable_rows(6, minor, ["12", "14"]); r_single = reachable_rows(6, minor, ["12", "14", "1234"])
print(f"S1 plain courses: minimus {pc_minimus}/24, doubles {pc_doubles}/120, minor {pc_minor}/720; lead-end parity {le_par}")
print(f"S2 rows reachable at all: plain+bob {r_bobs}/720, plus single {r_single}/720")
ok = (pc_minimus, pc_doubles, pc_minor) == (24, 40, 60) and r_bobs == 360 and r_single == 720
ok &= le_par["12"] == 0 and le_par["14"] == 0 and le_par["1234"] == 1

# --- faros
def faro(n, out):
    h = n // 2; first, second = (range(h), range(h, n)) if out else (range(h, n), range(h))
    return tuple(c for pair in zip(first, second) for c in pair)
def group_size(gens, cap=3_000_000):
    start = tuple(range(len(gens[0]))); seen = {start}; todo = [start]
    while todo and len(seen) < cap:
        p = todo.pop()
        for g in gens:
            q = compose(p, g)
            if q not in seen: seen.add(q); todo.append(q)
    return len(seen), any(parity(p) for p in seen)
print("S3 faro generator parity and reachable orderings (out+in):")
rows = []
for n in (4, 6, 8, 10, 12, 14, 16, 20, 24, 52):
    po, pi = parity(faro(n, True)), parity(faro(n, False))
    size, has_odd = group_size([faro(n, True), faro(n, False)]) if n <= 24 else (None, None)
    rows.append((n, po, pi, size, has_odd))
    capped = size is not None and size >= 3_000_000
    frac = ("not enumerated" if size is None else f">= {size} (search capped)" if capped
            else f"{size}/{n}! = {size / factorial(n):.2e} of all, {size / (factorial(n) // 2):.2e} of the even half")
    print(f"   {n:2d} cards: out {'odd' if po else 'even'}, in {'odd' if pi else 'even'}; reachable {frac}; contains odd perm={has_odd}")
# parity bound must hold: if both generators even, nothing odd is reachable
ok &= all(not h for n, po, pi, s, h in rows if s is not None and po == 0 and pi == 0)
# tightness: for bells the parity bound is reached exactly (360 = 720/2); for faros it is not
ok &= r_bobs == factorial(6) // 2 and [s for n, po, pi, s, h in rows if n == 8][0] < factorial(8) // 2
ok &= all(h for n, po, pi, s, h in rows if s is not None and (po or pi))
both_even = [n for n, po, pi, s, h in rows if po == 0 and pi == 0]
p52 = [(po, pi) for n, po, pi, s, h in rows if n == 52][0]
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" bells: minimus 24/24, doubles 40/120, minor plain 60/720; bob and plain lead ends even so plain+bob reach {r_bobs}/720, single (odd) reaches {r_single};"
      f" faros: decks whose out and in are both even {both_even} never reach an odd ordering, but 8 cards reach only 24 of 20160 even orderings (bound not tight); 52 cards out/in parity {p52}")
