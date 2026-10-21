"""Sandbox L10: do Suno Trending choruses repeat verbatim, and is variation saved for the last chorus?

Kernels: ideas:SONGWRITING/development/each-verse-changes-what-the-chorus-means (the verse moves, the
chorus meaning shifts) and ideas:SONGWRITING/chorus/false-resolution/stable-words-changing-verdict
(same words, new verdict) both assume chorus TEXT is stable. Per song, derived in-page from stored
lyrics (no text kept): ni = chorus instances; verb = all instances identical after normalising;
lastDiff = last instance differs from the first; midDiff = second differs from first (ni >= 3).
Same 54 songs and chorus locator as loop 9. Deterministic, stdlib only.

PREDICTION (written after seeing the encoded rows, before computing any rate):
  P1 among songs with >= 2 chorus instances, verbatim share <= 40%
  P2 among songs with >= 3 instances, lastDiff rate exceeds midDiff rate by >= 15 points
  P3 break: midDiff rate >= 40% (variation starts at the first repeat, not saved for the end)
  P4 collapsing identical rows keeps the P1 verdict
"""
NOW = "001,010,2,1,0,- ; 101,011,9,0,1,1 ; 011,001,2,0,1,- ; -,-,0,-,-,- ; 101,000,4,0,1,1 ; 000,000,3,0,1,1 ; -,-,3,0,1,1 ; -,-,0,-,-,- ; 110,101,3,1,0,0 ; 001,101,2,0,1,- ; -,-,2,1,0,- ; 100,100,3,0,1,0 ; 111,111,4,0,1,1 ; -,-,3,0,1,1 ; -,-,0,-,-,- ; 000,001,2,0,1,- ; 100,110,3,0,1,0 ; 100,110,3,0,1,0 ; -,-,0,-,-,- ; 111,101,3,0,1,1 ; 011,001,3,0,1,0 ; 100,101,3,0,1,0 ; 111,100,9,0,1,0 ; 000,101,2,1,0,- ; 011,000,3,1,0,0 ; 111,100,3,0,1,0 ; -,-,0,-,-,- ; 100,-,3,0,1,1"
WEEKLY = "100,110,3,0,1,0 ; 111,001,2,1,0,- ; 111,000,2,1,0,- ; 110,100,2,0,1,- ; 111,001,6,0,1,1 ; 100,101,2,0,1,- ; 011,-,2,0,1,- ; 011,-,1,-,-,- ; 111,101,2,1,0,- ; 111,-,1,-,-,- ; 000,100,2,0,1,- ; 011,001,3,0,1,1 ; 100,110,3,0,1,0 ; 101,111,4,0,1,1 ; 100,101,6,0,1,1 ; 100,100,3,0,1,0 ; 001,001,2,1,0,- ; 011,111,2,1,0,- ; 000,011,3,0,1,1 ; 100,001,2,1,0,- ; 111,001,3,0,1,0 ; -,-,0,-,-,- ; -,-,0,-,-,- ; 100,101,1,-,-,- ; 100,-,1,-,-,- ; 100,110,3,0,1,0"
ROWS = [r.strip() for r in (NOW + " ; " + WEEKLY).split(";")]


def stats(rows):
    P = []
    for r in rows:
        _, _, ni, verb, last, mid = r.split(",")
        P.append((int(ni), None if verb == "-" else int(verb), None if last == "-" else int(last), None if mid == "-" else int(mid)))
    two = [p for p in P if p[0] >= 2]
    three = [p for p in P if p[0] >= 3]
    verb = sum(p[1] for p in two) / len(two)
    last3 = sum(p[2] for p in three) / len(three)
    mid3 = sum(p[3] for p in three) / len(three)
    return len(two), verb, len(three), last3, mid3


n2, verb, n3, last3, mid3 = stats(ROWS)
dn2, dverb, *_ = stats(list(dict.fromkeys(ROWS)))
res = [("P1 verbatim <= 40%", verb <= 0.40, f"{verb:.0%} of {n2}"),
       ("P2 last exceeds mid by >= 15 pts", last3 - mid3 >= 0.15, f"last {last3:.0%} vs mid {mid3:.0%} (n {n3})"),
       ("P3 break: mid variation >= 40%", mid3 >= 0.40, f"{mid3:.0%}"),
       ("P4 dedupe keeps P1", (dverb <= 0.40) == (verb <= 0.40), f"deduped {dverb:.0%} of {dn2}")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; verbatim {verb:.0%} (n {n2}); with 3+ instances last-differs {last3:.0%} vs second-differs {mid3:.0%} (n {n3}); deduped verbatim {dverb:.0%}")
