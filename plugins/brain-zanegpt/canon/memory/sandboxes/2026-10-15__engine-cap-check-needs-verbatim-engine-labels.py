"""Sandbox: the engine-first cap (max repeats ceil(k/8)) is checked by counting engine LABELS in a batch.
Entries: ideas:COMEDY-CRAFT/ideation/vary-the-comic-engine-not-the-topic (assign a different engine per idea,
check repeated engines), fake-ad-kernel-source-check/E1 (labels must be verbatim, paraphrases break lookups),
engine-repeat-above-eight-needs-new-skeleton-not-new-topic/E1 (cap makes a repeat legal; k=9 forces one).
PREDICTION (before first run): with free-text labels where each idea paraphrases its engine with probability
0.4, a label-count cap check misses at least 30% of batches that truly break the cap at k=16 with 3+ repeats of
one engine (true count 3 > cap 2); a closed vocabulary that rejects unknown labels misses 0%, at the cost of
rejecting a share of ideas near the paraphrase rate. BREAK: at paraphrase rate 0 both checks agree (0% miss), so
the miss rate comes from the paraphrase and not from the checker. Assumption: label strings are what the check
counts. Wrong if the free-text miss rate is under 30%."""
import random
ENG = ["escalation", "literalism", "role reversal", "anticlimax", "callback", "genre switch", "misdirection", "deadpan restraint"]
PARA = {"escalation": ["stakes go cosmic", "things get bigger"], "literalism": ["takes it literally", "word-for-word"],
        "role reversal": ["roles flipped", "swap who is in charge"], "anticlimax": ["big build then nothing", "letdown"],
        "callback": ["running gag", "earlier joke returns"], "genre switch": ["turns into a thriller", "changes genre"],
        "misdirection": ["fake-out", "wrong guess"], "deadpan restraint": ["flat delivery", "understated"]}
SYN = {p: e for e, ps in PARA.items() for p in ps}

def make(k, rate, rng):
    # truth: 3 ideas share one engine (breaking cap 2 at k=16), rest spread
    truth = [ENG[0]] * 3 + [ENG[1 + i % 7] for i in range(k - 3)]
    rng.shuffle(truth)
    label = [rng.choice(PARA[t]) if rng.random() < rate else t for t in truth]
    return truth, label

def breaks(labels, k):
    from collections import Counter
    return max(Counter(labels).values()) > -(-k // 8)

def run(rate, trials=2000, k=16):
    rng = random.Random(11); miss_free = miss_closed = rejected = 0
    for _ in range(trials):
        truth, label = make(k, rate, rng)
        assert breaks(truth, k)
        if not breaks(label, k): miss_free += 1
        kept = [l for l in label if l in ENG]                 # closed vocabulary: unknown labels rejected
        rejected += k - len(kept)
        resub = [l if l in ENG else None for l in label]
        # a rejected idea is sent back for a verbatim label; the author re-labels it truthfully
        fixed = [l if l in ENG else t for l, t in zip(label, truth)]
        if not breaks(fixed, k): miss_closed += 1
    return miss_free / trials, miss_closed / trials, rejected / (trials * k)

res = {}
for rate in (0.0, 0.2, 0.4, 0.6):
    res[rate] = run(rate)
    print("paraphrase %.1f  free-text miss %.3f  closed-vocab miss %.3f  ideas bounced %.3f" % ((rate,) + res[rate]))
ok = res[0.0][0] == 0 and res[0.4][0] >= 0.30 and res[0.4][1] == 0
print("RESULT: %s free-text miss at 0.4 = %.3f (at 0.0 = %.3f), closed-vocab miss = %.3f, bounced %.3f"
      % ("PASS" if ok else "FAIL", res[0.4][0], res[0.0][0], res[0.4][1], res[0.4][2]))
