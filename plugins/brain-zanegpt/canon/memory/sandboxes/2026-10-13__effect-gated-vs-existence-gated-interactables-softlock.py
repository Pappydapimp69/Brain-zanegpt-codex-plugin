# Prediction (before run): quest chain Q1->well1, Q2->well2, Q3->well1 (well1 reused). Player prefix = any sequence
# of 1..6 touches over 3 wells (1092 sequences) before a perfect solver finishes the chain.
# Existence gating (a well exists only while its quest is active) = 0 soft-locks and 0 early-hint touches.
# Effect gating that checks the CURRENT quest = 0 soft-locks, many early-hint touches (>0).
# BREAK: effect gating with a per-well 'already touched' flag set on ANY touch soft-locks every sequence that
# touches well1 before Q3 is active but after... (predict > 0 soft-locks, and none if the prefix never touches well1).
import itertools
CHAIN = [1, 2, 1]
def play(prefix, mode):
    q = 0; touched = set(); hints = 0
    def touch(w):
        nonlocal q, hints
        if q >= len(CHAIN): return
        need = CHAIN[q]
        if mode == "existence":
            if w != need: return                 # other wells do not exist yet
            q += 1
        elif mode == "effect":
            if w == need: q += 1
            else: hints += 1
        elif mode == "flag":
            if w == need and w not in touched: q += 1
            elif w != need: hints += 1
            touched.add(w)                        # flag set on ANY touch, even a non-effect one
    for w in prefix: touch(w)
    for _ in range(4):                            # perfect solver tries the needed well, up to 4 times
        if q < len(CHAIN): touch(CHAIN[q])
    return q == len(CHAIN), hints
res = {}
seqs = [p for n in range(1, 7) for p in itertools.product((1, 2, 3), repeat=n)]
for mode in ("existence", "effect", "flag"):
    locks = early = 0
    for p in seqs:
        done, h = play(p, mode)
        locks += (not done); early += (h > 0)
    res[mode] = (locks, early)
    print("S %-9s soft-locks %4d / %d, sequences that drew a hint %4d" % (mode, locks, len(seqs), early))
no_w1 = [p for p in seqs if 1 not in p]
flag_clean = all(play(p, "flag")[0] for p in no_w1)
print("S4 BREAK flag mode, prefixes that never touch well1: %d sequences, all complete %s" % (len(no_w1), flag_clean))
ok = res["existence"] == (0, 0) and res["effect"][0] == 0 and res["effect"][1] > 0 and res["flag"][0] > 0 and flag_clean
print("RESULT: %s soft-locks existence %d, effect(current quest) %d, touched-flag %d of %d; early hints existence %d, effect %d; flag mode clean when well1 untouched: %s"
      % ("PASS" if ok else "FAIL", res["existence"][0], res["effect"][0], res["flag"][0], len(seqs), res["existence"][1], res["effect"][1], flag_clean))
