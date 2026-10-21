"""Sandbox L7: does a declared-target rhyme checker's verdict depend on how codas are compared?

Kernels: ideas:SONGWRITING/prompt-tooling/declared-emotional-target-cross-checks-the-craft-choices,
ideas:SONGWRITING/rhyme/rhyme-type-controls-emotional-resolution-not-just-sound (perfect and family
resolve, assonance leaves it open), ideas:SONGWRITING/rhyme/family-rhyme-is-same-vowel-same-manner-coda.
Words are labelled (vowel, coda) in ARPAbet. Two defensible coda rules:
  R_last: compare only the LAST coda consonant (same phone -> perfect, same manner -> family)
  R_full: compare the whole coda (identical -> perfect, same length and manner sequence -> family)
Stable = perfect or family. Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 >= 15% of same-vowel pairs flip stable/unstable between the two rules
  P2 R_last calls at least 10 points more pairs stable than R_full
  P3 the song's final-chorus pair ask/back flips (R_last stable, R_full unstable)
  P4 break: the song's intentionally stable chorus pair wall/all does NOT flip
"""
from itertools import combinations

MANNER = {**{c: "stop" for c in "P B T D K G".split()}, **{c: "fric" for c in "F V S Z SH TH DH".split()},
          **{c: "nasal" for c in "M N NG".split()}, **{c: "liquid" for c in "L R".split()},
          **{c: "affric" for c in "CH JH".split()}}
W = {  # word: (vowel, coda tuple)
    "eat": ("IY", ("T",)), "cheap": ("IY", ("P",)), "seed": ("IY", ("D",)), "leaf": ("IY", ("F",)), "feel": ("IY", ("L",)),
    "dream": ("IY", ("M",)), "clean": ("IY", ("N",)), "beast": ("IY", ("S", "T")), "week": ("IY", ("K",)), "please": ("IY", ("Z",)),
    "back": ("AE", ("K",)), "ask": ("AE", ("S", "K")), "that": ("AE", ("T",)), "map": ("AE", ("P",)), "hand": ("AE", ("N", "D")),
    "last": ("AE", ("S", "T")), "thank": ("AE", ("NG", "K")), "sad": ("AE", ("D",)), "man": ("AE", ("N",)), "am": ("AE", ("M",)),
    "up": ("AH", ("P",)), "stuff": ("AH", ("F",)), "sun": ("AH", ("N",)), "blood": ("AH", ("D",)), "truck": ("AH", ("K",)),
    "lunch": ("AH", ("N", "CH")), "must": ("AH", ("S", "T")), "from": ("AH", ("M",)), "love": ("AH", ("V",)), "dull": ("AH", ("L",)),
    "time": ("AY", ("M",)), "fine": ("AY", ("N",)), "eyes": ("AY", ("Z",)), "night": ("AY", ("T",)), "ride": ("AY", ("D",)),
    "life": ("AY", ("F",)), "like": ("AY", ("K",)), "mind": ("AY", ("N", "D")), "lights": ("AY", ("T", "S")), "alive": ("AY", ("V",)),
    "slow": ("OW", ()), "alone": ("OW", ("N",)), "road": ("OW", ("D",)), "cold": ("OW", ("L", "D")), "ghost": ("OW", ("S", "T")),
    "hope": ("OW", ("P",)), "smoke": ("OW", ("K",)), "knows": ("OW", ("Z",)), "boat": ("OW", ("T",)), "home": ("OW", ("M",)),
    "wall": ("AO", ("L",)), "all": ("AO", ("L",)), "small": ("AO", ("L",)),
}


def r_last(a, b):
    ca, cb = W[a][1], W[b][1]
    la, lb = (ca[-1] if ca else None), (cb[-1] if cb else None)
    if la == lb:
        return "perfect"
    if la and lb and MANNER[la] == MANNER[lb]:
        return "family"
    return "assonance"


def r_full(a, b):
    ca, cb = W[a][1], W[b][1]
    if ca == cb:
        return "perfect"
    if len(ca) == len(cb) and ca and all(MANNER[x] == MANNER[y] for x, y in zip(ca, cb)):
        return "family"
    return "assonance"


stable = lambda t: t in ("perfect", "family")
pairs = [(a, b) for a, b in combinations(W, 2) if W[a][0] == W[b][0]]
flips = [(a, b) for a, b in pairs if stable(r_last(a, b)) != stable(r_full(a, b))]
s_last = sum(stable(r_last(a, b)) for a, b in pairs) / len(pairs)
s_full = sum(stable(r_full(a, b)) for a, b in pairs) / len(pairs)
ab = (r_last("ask", "back"), r_full("ask", "back"))
wa = (r_last("wall", "all"), r_full("wall", "all"))
res = [("P1 flips >= 15%", len(flips) / len(pairs) >= 0.15, f"{len(flips)}/{len(pairs)} = {len(flips) / len(pairs):.0%}"),
       ("P2 R_last >= 10 pts more stable", s_last - s_full >= 0.10, f"R_last {s_last:.0%} vs R_full {s_full:.0%}"),
       ("P3 ask/back flips", stable(ab[0]) and not stable(ab[1]), f"R_last {ab[0]}, R_full {ab[1]}"),
       ("P4 break: wall/all steady", stable(wa[0]) and stable(wa[1]), f"{wa[0]} / {wa[1]}")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
print("sample flips:", ", ".join(f"{a}/{b}" for a, b in flips[:10]))
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; flips {len(flips)}/{len(pairs)} ({len(flips) / len(pairs):.0%}); stable R_last {s_last:.0%} R_full {s_full:.0%}; "
      f"ask/back {ab[0]} vs {ab[1]}; wall/all {wa[0]}")
