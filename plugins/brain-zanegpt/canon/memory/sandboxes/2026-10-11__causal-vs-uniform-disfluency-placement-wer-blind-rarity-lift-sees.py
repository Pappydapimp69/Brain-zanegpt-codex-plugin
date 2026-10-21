# Same disfluency RATE, two placements: uniform vs causal (before hard-to-retrieve rare words).
# Tests whether a rate-matched ASR WER benchmark can tell them apart, and what can.
N_UTT, L = 400, 15
RARE_SHARE = 0.30

def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def rare(g):  # deterministic rarity of the g-th word overall
    return (g * 7919 + 13) % 100 >= 100 * (1 - RARE_SHARE)

def build(rate, mode):
    """returns list of (ref_tokens, flags) per utterance; flags[k]=True if token k is a clean word that is rare and
    directly follows a disfluency."""
    acc, kind, g, utts, n_dis, n_words = 0.0, 0, 0, [], 0, 0
    for u in range(N_UTT):
        toks, meta = [], []
        for i in range(L):
            w, r = "w%d" % g, rare(g)
            credit = rate if mode == "uniform" else (rate / RARE_SHARE if r else 0.0)
            acc += credit
            prev_dis = False
            if acc >= 1.0:
                acc -= 1.0
                k = kind % 3; kind += 1; n_dis += 1
                if k == 0:
                    toks.append("uh"); meta.append("dis")
                elif k == 1 and toks and meta[-1] == "word":
                    toks.append(toks[-1]); meta.append("dis")
                else:
                    toks.append(w[:2] + "_"); meta.append("dis")
                prev_dis = True
            toks.append(w); meta.append(("rare_after" if (r and prev_dis) else "word")); g += 1; n_words += 1
        acc = min(acc, 1.0)
        utts.append((toks, meta))
    return utts, n_dis / n_words * 100

def recognise(toks, meta, sensitive):
    hyp, clean_i = [], 0
    for t, m in zip(toks, meta):
        if m == "dis":
            hyp.append("frag" if t.endswith("_") else t)  # fragments hallucinated as another word
        else:
            clean_i += 1
            bad = (clean_i % 10 == 0) or (sensitive and m == "rare_after")
            hyp.append("x" + t if bad else t)
    return hyp

def wer(utts, sensitive):
    e = n = 0
    for toks, meta in utts:
        hyp = recognise(toks, meta, sensitive)
        e += levenshtein(toks, hyp); n += len(toks)
    return e / n

def lift(utts):
    after = tot = 0
    # next-word rarity after a disfluency, from meta/rarity of the following clean word
    for toks, meta in utts:
        for k, m in enumerate(meta):
            if m == "dis":
                j = k + 1
                while j < len(meta) and meta[j] == "dis": j += 1
                if j < len(meta):
                    tot += 1; after += (meta[j] == "rare_after")
    return (after / tot) / RARE_SHARE if tot else 0.0

res, out = {}, []
for rate_pct in (5.97, 20, 40):
    rate = rate_pct / 100
    clean, _ = build(0.0, "uniform")
    base_a, base_b = wer(clean, False), wer(clean, True)
    row = {}
    for mode in ("uniform", "causal"):
        u, achieved = build(rate, mode)
        row[mode] = dict(achieved=achieved, a=wer(u, False) / base_a, b=wer(u, True) / base_b, lift=lift(u))
    res[rate_pct] = row
    out.append("rate %.2f: " % rate_pct + " | ".join("%s ach=%.1f blindx=%.2f sensx=%.2f lift=%.2f" % (m, r['achieved'], r['a'], r['b'], r['lift']) for m, r in row.items()))
print("\n".join(out))
t = res[5.97]
c1 = abs(t['uniform']['a'] - t['causal']['a']) < 0.03   # blind WER cannot tell placements apart at equal rate
c2 = t['causal']['lift'] > 2.5 and t['uniform']['lift'] < 1.5   # rarity lift can
c3 = t['causal']['b'] > t['uniform']['b'] * 1.02            # a rarity-sensitive recogniser does separate them
c4 = res[40]['causal']['lift'] < 0.85 * res[5.97]['causal']['lift']  # break: at 40/100 causal placement spills onto non-rare words
print("c1_blind_wer_equal", c1, "c2_lift_separates", c2, "c3_sensitive_wer_separates", c3, "c4_causal_lift_erodes_at_density", c4)
print(("RESULT: PASS" if all([c1, c2, c3, c4]) else "RESULT: FAIL"),
      "rate-matched blind WER x%.2f vs x%.2f; rarity lift %.2f vs %.2f; sensitive WER x%.2f vs x%.2f; causal lift at 40/100 %.2f"
      % (t['uniform']['a'], t['causal']['a'], t['uniform']['lift'], t['causal']['lift'], t['uniform']['b'], t['causal']['b'], res[40]['causal']['lift']))
