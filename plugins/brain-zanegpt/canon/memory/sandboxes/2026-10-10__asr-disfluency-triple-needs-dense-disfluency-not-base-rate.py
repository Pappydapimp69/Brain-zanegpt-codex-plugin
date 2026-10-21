"""Toy ASR error model (NOT a measurement of any real recogniser). Real Levenshtein alignment gives S/D/I.
Reference = verbatim transcript with disfluencies. Disfluency types from the base-rate kernel (per 100 words:
fillers 2.56, repeats 1.47, restarts 1.94 = 5.97); a restart = reparandum + editing term + repair (Levelt),
and 23% of restarts cut a word mid-word (partial word fragment).
Baseline recogniser: clean words get substitution on every 10th word (10% S); fillers are recognised; a repeat's second copy
is kept; a partial-word fragment is decoded as FRAG_INS spurious whole words (default 2) - the only added mechanism.
Prediction (before run): at the 5.97/100 base rate the WER ratio disfluent/clean is below 1.6 (not 3); insertions are the
largest error class on a dense set; the ratio reaches 3.0 only at a disfluency density of at least 20 per 100 words with
FRAG_INS=2; the insertion share at 3x is >= 0.45; removing fragment hallucination (FRAG_INS=0, the '<pw> tag' stand-in)
cuts the ratio at density 30/100 by at least a third; with FRAG_INS=0 insertions are no longer the largest class (BREAK)."""
VOCAB = ["the", "red", "dot", "above", "a", "blue", "square", "next", "to", "green", "circle", "and", "then", "left", "of", "it"]
def clean_utts(n=400, length=15):
    u = []
    for i in range(n):
        u.append([VOCAB[(i * 7 + j * 5 + (i // 3)) % len(VOCAB)] + ("" if j % 4 else str(j % 3)) for j in range(length)])
    return u
def add_disfluencies(utts, per100, seed_step=1):
    """deterministic accumulator placement; mix 2.56:1.47:1.94, 23% of restarts partial-word"""
    mix = [("filler", 2.56), ("repeat", 1.47), ("restart", 1.94)]
    tot = sum(w for _, w in mix); acc = 0.0; k = 0; kinds_order = []
    out_ref, out_hyp_meta = [], []
    cnt = {"filler": 0, "repeat": 0, "restart": 0, "partial": 0}
    wi = 0; acc_t = {m: 0.0 for m, _ in mix}; part_acc = 0.0
    refs = []
    for u in utts:
        ref, meta = [], []   # meta: parallel list of tags: 'w', 'f' (frag), 'x' (other disfluent kept)
        for w in u:
            for m, wt in mix:
                acc_t[m] += per100 * wt / tot / 100.0
            if acc_t["filler"] >= 1:
                acc_t["filler"] -= 1; ref.append("uh"); meta.append("x"); cnt["filler"] += 1
            if acc_t["repeat"] >= 1:
                acc_t["repeat"] -= 1; ref.append(w); meta.append("x"); cnt["repeat"] += 1
            if acc_t["restart"] >= 1:
                acc_t["restart"] -= 1; cnt["restart"] += 1; part_acc += 0.23
                if part_acc >= 1:
                    part_acc -= 1; ref.append(w[:1] + "-"); meta.append("f"); cnt["partial"] += 1
                else:
                    ref.append(w); meta.append("x")
                ref.append("uh"); meta.append("x")
            ref.append(w); meta.append("w")
        refs.append((ref, meta))
    return refs, cnt
def recognise(ref, meta, frag_ins, derail=0):
    hyp = []; k = 0; bad = 0
    for w, m in zip(ref, meta):
        if m == "f": bad = derail
        if m == "w":
            k += 1
            if bad > 0:
                hyp.append(w + "!"); bad -= 1   # derailed: substitution in the words after a fragment
            else:
                hyp.append(w + "~" if k % 10 == 0 else w)   # substitution on every 10th clean word
        elif m == "f":
            hyp.extend(["spur%d" % i for i in range(frag_ins)])   # hallucinated whole words
        else:
            hyp.append(w)
    return hyp
def align(r, h):
    n, m = len(r), len(h)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): d[i][0] = i
    for j in range(m + 1): d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i-1][j-1] + (r[i-1] != h[j-1]), d[i-1][j] + 1, d[i][j-1] + 1)
    i, j, S, D, I = n, m, 0, 0, 0
    while i or j:
        if i and j and d[i][j] == d[i-1][j-1] + (r[i-1] != h[j-1]):
            S += r[i-1] != h[j-1]; i -= 1; j -= 1
        elif i and d[i][j] == d[i-1][j] + 1: D += 1; i -= 1
        else: I += 1; j -= 1
    return S, D, I
def wer(per100, frag_ins, derail=0):
    refs, cnt = add_disfluencies(clean_utts(), per100)
    S = D = I = N = 0
    for ref, meta in refs:
        s, d, i = align(ref, recognise(ref, meta, frag_ins, derail)); S += s; D += d; I += i; N += len(ref)
    return (S + D + I) / N, (S, D, I), cnt
base, bc, _ = wer(0.0, 2)
print(f"clean WER {base:.3f} {bc}")
rows = {}
for dens in (5.97, 10, 20, 30, 40):
    w, (S, D, I), cnt = wer(dens, 2)
    tot = S + D + I
    rows[dens] = (w / base, I / tot, w)
    print(f"density {dens:5.2f}/100 FRAG_INS=2 WER {w:.3f} ratio {w/base:.2f} S/D/I share {S/tot:.2f}/{D/tot:.2f}/{I/tot:.2f} partial={cnt['partial']}")
w0, (S0, D0, I0), _ = wer(30, 0)
t0 = S0 + D0 + I0
print(f"density 30/100 FRAG_INS=0 WER {w0:.3f} ratio {w0/base:.2f} S/D/I share {S0/t0:.2f}/{D0/t0:.2f}/{I0/t0:.2f}")
print("-- iteration 2 (added after the first-run FAIL): fragment also derails the next K words --")
kneed = {}
for dens in (5.97, 30):
    for K in (0, 2, 4, 8, 16, 32, 64):
        w, (S, D, I), _ = wer(dens, 2, K)
        tot = S + D + I
        kneed.setdefault(dens, []).append((K, round(w / base, 2), round(I / tot, 2)))
    print(f"density {dens}: (K, ratio, insertion share) {kneed[dens]}")
reach = next((d for d in sorted(rows) if rows[d][0] >= 3.0), None)
k3 = next((K for K, r, _ in kneed[30] if r >= 3.0), None)
print("derail words per fragment needed for 3x at density 30:", k3, "; at base rate:", next((K for K, r, _ in kneed[5.97] if r >= 3.0), None))
ok = (rows[5.97][0] < 1.6 and reach is not None and reach >= 20 and rows[reach][1] >= 0.45
      and (w0 / base) <= (rows[30][0]) * (2 / 3) and I0 / t0 < max(S0, D0) / t0)
print("RESULT:", "PASS" if ok else "FAIL", f"ratio at base rate {rows[5.97][0]:.2f}; first density with 3x: {reach}; insertion share there {rows[reach][1] if reach else None}; FRAG_INS=0 ratio at 30: {w0/base:.2f} vs {rows[30][0]:.2f}; derail K for 3x at density 30: {k3}")
