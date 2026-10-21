"""Independent re-model of 'a mid-pitch joke absorbs more than an opening joke'
(kernel HUMOR-STYLES/pitch-opening/...). Different structure from the earlier
sandboxes: attention decays GEOMETRICALLY toward a floor, beats have values, the
change beat must come first to set the frame; a joke refills a fraction of the gap
and costs one slot (the last beat is dropped). Deterministic, stdlib only.

PREDICTION (written before first run):
 P1 default grid: mid (slot 3) beats opening (slot 0) in >= 90% of cells.
 P2 with NO frame benefit (framed decay == unframed decay) mid still wins >= 50%.
 P3 mid loses when the attention floor is high and refill is tiny (<=0.1): the
    slot cost dominates, so no-joke beats both and mid vs opening is a near-tie.
 P4 the pitch length breaks it: at 4 slots, a mid joke sits too late -> opening wins in some cells.
"""
import itertools

def absorbed(n, joke_slot, a0, refill, d_unf, d_fr, floor, values=None):
    """Beats occupy slots; a joke takes one slot, pushing later beats back and dropping
    the last beat. Beat 0 is the change beat: once delivered, decay becomes d_fr.
    Returns summed attention*value over delivered beats."""
    values = values or [1.0] * n
    a = a0; framed = False; total = 0.0; beat = 0
    for slot in range(n):
        if joke_slot == slot:
            a = a + refill * (1 - a)          # joke slot: refill, no content
        else:
            if beat < n - (1 if joke_slot is not None else 0):
                total += a * values[beat]
                if beat == 0: framed = True
                beat += 1
        d = d_fr if framed else d_unf
        a = floor + (a - floor) * (1 - d)
    return total

def grid(n, mid, frame_benefit=True, floors=(0.0, 0.2, 0.4), refills=(0.05, 0.1, 0.3, 0.6, 0.9),
         a0s=(0.35, 0.55, 0.75, 0.95), d_unf=0.15):
    d_fr = 0.05 if frame_benefit else d_unf
    wins = loses = ties = 0; nojoke_best = 0; cells = 0
    for fl, r, a0 in itertools.product(floors, refills, a0s):
        if a0 < fl: continue
        cells += 1
        op = absorbed(n, 1 if False else 0, a0, r, d_unf, d_fr, fl)
        # opening joke occupies slot 0 -> change beat can only come at slot 1
        md = absorbed(n, mid, a0, r, d_unf, d_fr, fl)
        nj = absorbed(n, None, a0, r, d_unf, d_fr, fl)
        if md > op + 1e-9: wins += 1
        elif op > md + 1e-9: loses += 1
        else: ties += 1
        if nj >= max(op, md) - 1e-9: nojoke_best += 1
    return cells, wins, loses, ties, nojoke_best

out = {}
c, w, l, t, nb = grid(6, 3); out['P1'] = (w / c, c, w, l, t, nb)
print("P1 n=6 mid=3 default: mid>open %d/%d (loses %d ties %d), no-joke best in %d" % (w, c, l, t, nb))
c, w, l, t, nb = grid(6, 3, frame_benefit=False); out['P2'] = (w / c, c, w, l, t, nb)
print("P2 no frame benefit: mid>open %d/%d (loses %d ties %d), no-joke best in %d" % (w, c, l, t, nb))
c, w, l, t, nb = grid(6, 3, floors=(0.4,), refills=(0.05, 0.1), a0s=(0.55, 0.75, 0.95)); out['P3'] = (nb / c, c, w, l, t, nb)
print("P3 high floor + tiny refill: no-joke best in %d/%d, mid>open %d loses %d ties %d" % (nb, c, w, l, t))
for n, mid in ((4, 2), (4, 3), (5, 3), (8, 4), (8, 6)):
    c, w, l, t, nb = grid(n, mid)
    out[(n, mid)] = (w, l)
    print("P4 n=%d mid=%d: mid>open %d/%d loses %d ties %d" % (n, mid, w, c, l, t))
# where does mid lose? list the losing cells for n=6 mid=3
losers = []
for fl, r, a0 in itertools.product((0.0, 0.2, 0.4), (0.05, 0.1, 0.3, 0.6, 0.9), (0.35, 0.55, 0.75, 0.95)):
    if a0 < fl: continue
    op = absorbed(6, 0, a0, r, 0.15, 0.05, fl); md = absorbed(6, 3, a0, r, 0.15, 0.05, fl)
    if op > md + 1e-9: losers.append((fl, r, a0, round(op - md, 3)))
print("n=6 mid=3 cells where OPENING wins:", losers[:8], "count", len(losers))
# break: moving the joke slot later keeps winning? sweep slot for n=6
print("slot sweep n=6 (cells where slot beats opening):", [(s, grid(6, s)[1]) for s in range(1, 6)])

by_a0 = {}
for fl, r, a0, d in losers: by_a0[a0] = by_a0.get(a0, 0) + 1
print("opening-wins by initial attention (n=6 mid=3):", sorted(by_a0.items()))
p1 = out['P1'][0] >= 0.9
p2 = out['P2'][0] >= 0.5
p3 = out['P3'][0] >= 0.9
p4 = any(out[k][1] > 0 for k in out if isinstance(k, tuple))
print("PREDICTIONS held:", p1, p2, p3, p4)
print("RESULT: %s P1=%.2f P2=%.2f P3=%.2f P4=%s (predictions held: %d/4)" % (
    "PASS" if (p1 and p2 and p3 and p4) else "FAIL", out['P1'][0], out['P2'][0], out['P3'][0], p4, sum([p1, p2, p3, p4])))
