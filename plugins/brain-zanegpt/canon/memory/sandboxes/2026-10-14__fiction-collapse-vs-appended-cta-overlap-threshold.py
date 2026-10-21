"""Toy model: ending a fictional-scenario pitch by (B) collapsing the fiction onto the room's literal situation vs (A) exiting the
fiction and appending a CTA. All constants assumed except attention loss rates borrowed from sandbox-pitch-opening-joke-order-rule/E1
(0.05 per slot while a motivating frame is held, 0.14 per slot without one).
Overlap = Jaccard of the fiction's structural features with the audience's real situation (computed, not typed in).
uptake = attention_at_ask * ask_clarity * (1 - SEAM*seam_present) * (1 - OBJ*unanswered_objection)
A: 6 fiction slots, 2 slots out of frame (CTA), ask clarity 1.0, seam present, objection 'it does not exist' left hanging unless overlap answers it (no).
B: 8 slots in frame, ask clarity = overlap (the fiction IS the ask only as far as it maps), no seam, objection answered iff overlap >= 0.5 (preempt-objections: raise and answer)."""
SEAM, OBJ = 0.15, 0.30
def jaccard(a, b): return len(a & b) / len(a | b)
REAL = {"owner", "tight-margin", "stock-choice", "weekly-cash", "no-staff", "must-decide-now"}
def fiction(k):   # fiction shares k of the 6 real features, plus (6-k) invented ones
    base = list(sorted(REAL))
    return set(base[:k]) | {f"x{i}" for i in range(6 - k)}
def uptake_A():
    att = 1.0
    for _ in range(6): att -= 0.05 * att
    for _ in range(2): att -= 0.14 * att
    return att * 1.0 * (1 - SEAM) * (1 - OBJ)
def uptake_B(ov):
    att = 1.0
    for _ in range(8): att -= 0.05 * att
    return att * ov * (1 - (0 if ov >= 0.5 else OBJ))
rows = []
for k in range(0, 7):
    ov = jaccard(fiction(k), REAL)
    rows.append((k, round(ov, 3), round(uptake_B(ov), 3)))
A = uptake_A()
print("A appended CTA uptake %.3f" % A)
for r in rows: print("k=%d overlap %.3f B uptake %.3f %s" % (r[0], r[1], r[2], "B>A" if r[2] > A else "B<=A"))
cross = min(r[0] for r in rows if r[2] > A)
full = rows[-1][2] > A
low = rows[1][2] < A
print(f"RESULT: {'PASS' if full and low else 'FAIL'} collapse beats appended CTA only once fiction shares >= {cross} of 6 real features (overlap {rows[cross][1]}): B {rows[cross][2]} vs A {A:.3f}; at k=1 B {rows[1][2]} loses; at k=6 B {rows[6][2]}")
