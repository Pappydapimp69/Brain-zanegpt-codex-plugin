"""CARD-MAGIC/faro-shuffle kernel assumes PERFECT faros. How fragile are its two
uses to one human slip? (1) eight out-faros restore 52 cards; (2) Elmsley binary
in/out sequence moves the top card to position p. Slips modelled: an off-by-one
cut (26/26 becomes 25/27 or 27/25, extras dropped last) and one double drop (at
interleave step k two cards fall together from the half due, the rest continue
alternating). Exactly one slip per routine, swept over every shuffle and every k.
Deterministic, exhaustive.
Iteration 2 (after the first run refuted the prediction): survival by target band.
PREDICTION (written before running): any single slip in the eight-faro restore
leaves under 10% of cards home on average; Elmsley still lands the top card at p
in under 30% of single-slip cases."""
N = 52

def faro(deck, out=True, cut=None, double_at=None):
    c = len(deck) // 2 if cut is None else cut
    top, bot = deck[:c], deck[c:]
    first, second = (top, bot) if out else (bot, top)
    res, i, j, turn, step = [], 0, 0, 0, 0
    while i < len(first) or j < len(second):
        src = first if turn == 0 else second
        k = i if turn == 0 else j
        if k >= len(src):                      # this half is empty: drain the other
            turn ^= 1; continue
        take = 2 if step == double_at else 1
        chunk = src[k:k + take]
        res += chunk
        if turn == 0: i += len(chunk)
        else: j += len(chunk)
        turn ^= 1; step += 1
    return res

def home_after_restore(slip_shuffle=None, slip=None):
    d = list(range(N))
    for s in range(8):
        if s == slip_shuffle:
            kind, val = slip
            d = faro(d, True, cut=val) if kind == "cut" else faro(d, True, double_at=val)
        else:
            d = faro(d, True)
    return sum(d[i] == i for i in range(N))

def elmsley(p, slip_shuffle=None, slip=None):
    bits = bin(p)[2:] if p else ""
    d = list(range(N))
    for s, b in enumerate(bits):
        out = b == "0"
        if s == slip_shuffle:
            kind, val = slip
            d = faro(d, out, cut=val) if kind == "cut" else faro(d, out, double_at=val)
        else:
            d = faro(d, out)
    return d.index(0) == p

assert home_after_restore() == N, "perfect restore"
assert all(elmsley(p) for p in range(N)), "perfect Elmsley"
slips = [("cut", 25), ("cut", 27)] + [("double", k) for k in range(0, 51)]
homes = [home_after_restore(s, sl) for s in range(8) for sl in slips]
avg_home = sum(homes) / len(homes) / N
cut_homes = [home_after_restore(s, sl) for s in range(8) for sl in slips[:2]]
late_dbl = [home_after_restore(s, ("double", k)) for s in range(8) for k in range(46, 51)]
hits = tot = 0
for p in range(1, N):
    for s in range(len(bin(p)) - 2):
        for sl in slips:
            hits += elmsley(p, s, sl); tot += 1
band = {}
for lo, hi in ((1, 13), (13, 26), (26, 39), (39, 52)):
    h = t = 0
    for q in range(lo, hi):
        for st in range(len(bin(q)) - 2):
            for sl in slips:
                h += elmsley(q, st, sl); t += 1
    band[(lo, hi - 1)] = h / t
print("Elmsley survival by target position:", {f"{a}-{b}": f"{v:.0%}" for (a, b), v in band.items()})
print(f"restore: single slips {len(homes)}, cards home on average {avg_home:.1%}; off-by-one cut only {sum(cut_homes)/len(cut_homes)/N:.1%}; "
      f"double drop in the last 5 steps {sum(late_dbl)/len(late_dbl)/N:.1%}")
print(f"Elmsley: top card still lands at p in {hits}/{tot} single-slip cases ({hits/tot:.1%})")
ok = avg_home < 0.10 and hits / tot < 0.30
print(f"RESULT: {'PASS' if ok else 'FAIL'} one slip leaves {avg_home:.1%} of cards home after the 8-faro restore; "
      f"Elmsley survives {hits/tot:.1%} of single slips")
