"""Sandbox L1: missing-reply kernel under an online order-2 listener.

Kernel (ideas:SONGWRITING/silence/missing-reply): remove one half of a learned pattern.
Question: in a real song outline ("Did You Eat?"), does the first omitted reply stand out against
the final chorus's other novelty (new lines), and do later omissions keep their force?

Listener: predicts each line-level event from the previous two, learning online as the song plays.
P(w|a,b) = 0.6*ML(w|a,b) + 0.3*ML(w|b) + 0.1*add1(w) when contexts were seen; unseen context
weight is moved down to the next order. Vocabulary = all event types in the song (fixed).
Surprise = -log2 P. Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 first omission surprise > surprise of the final chorus's first new line
  P2 second and third omissions are each >= 40% less surprising than the first (fast habituation)
  P3 break: with only one Q-R per earlier chorus and no intro (pattern heard 2x not 7x), the first
     omission is NOT more surprising than the new line
  P4 the outro omission is <= half the first omission's surprise
"""
import math
from collections import defaultdict

FULL = (["Q", "R"] + ["v1a", "v1b", "v1c", "v1d", "p1", "p2"] +
        ["Q", "R", "Q", "R", "c1a", "c1b", "Q", "R"] +
        ["v2a", "v2b", "v2c", "v2d", "p3", "p4"] +
        ["Q", "R", "Q", "R", "c2a", "c2b", "Q", "R"] +
        ["b1", "b2", "b3", "b4", "b5", "BRK"] +
        ["Q", "SIL", "Q", "SIL", "f1", "f2", "Q", "SIL"] +
        ["Q", "SIL"])
SPARSE = (["v1a", "v1b", "v1c", "v1d", "p1", "p2"] +
          ["Q", "R", "c1a", "c1b"] +
          ["v2a", "v2b", "v2c", "v2d", "p3", "p4"] +
          ["Q", "R", "c2a", "c2b"] +
          ["b1", "b2", "b3", "b4", "b5", "BRK"] +
          ["Q", "SIL", "f1", "f2", "Q", "SIL"] +
          ["Q", "SIL"])


def surprises(seq):
    vocab = sorted(set(seq))
    V = len(vocab)
    c1, c2 = defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(int))
    uni = defaultdict(int)
    total = 0
    out = []
    for i, w in enumerate(seq):
        a = seq[i - 2] if i >= 2 else None
        b = seq[i - 1] if i >= 1 else None
        p0 = (uni[w] + 1) / (total + V)
        w2 = w1 = 0.0
        p2 = p1 = 0.0
        if b is not None and sum(c1[b].values()):
            p1, w1 = c1[b][w] / sum(c1[b].values()), 0.3
        if a is not None and sum(c2[(a, b)].values()):
            p2, w2 = c2[(a, b)][w] / sum(c2[(a, b)].values()), 0.6
        w0 = 1.0 - w1 - w2
        p = w2 * p2 + w1 * p1 + w0 * p0
        out.append((w, -math.log2(p)))
        uni[w] += 1
        total += 1
        if b is not None:
            c1[b][w] += 1
        if a is not None:
            c2[(a, b)][w] += 1
    return out


def summarize(seq):
    s = surprises(seq)
    sil = [x for w, x in s if w == "SIL"]
    f1 = next(x for w, x in s if w == "f1")
    return sil, f1


sil, f1 = summarize(FULL)
ssil, sf1 = summarize(SPARSE)
first, second, third, outro = sil[0], sil[1], sil[2], sil[3]
res = [
    ("P1 first omission beats new line", first > f1, f"omission {first:.2f} bits vs new line {f1:.2f}"),
    ("P2 later omissions drop >=40%", second <= 0.6 * first and third <= 0.6 * first,
     f"2nd {second:.2f}, 3rd {third:.2f} vs 1st {first:.2f}"),
    ("P3 break: sparse pattern loses to new line", not (ssil[0] > sf1), f"sparse omission {ssil[0]:.2f} vs new line {sf1:.2f}"),
    ("P4 outro <= half of first", outro <= 0.5 * first, f"outro {outro:.2f}"),
]
for n, ok, d in res:
    print(f"{n}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; full: omissions {first:.2f}/{second:.2f}/{third:.2f}/outro {outro:.2f} bits, new line {f1:.2f}; "
      f"sparse: omission {ssil[0]:.2f} vs new line {sf1:.2f}")
