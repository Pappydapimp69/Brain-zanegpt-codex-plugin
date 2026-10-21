"""Sandbox L9: does verse/chorus contrast show up in Suno Trending lyrics, and on which axis?

Kernel ideas:SONGWRITING/section-contrast/verse-and-chorus-differ-in-line-length-rhythm-and-rhyme (change
at least two of length, density, scheme at the chorus); settles the open tension filed earlier today
(chorus shorter lines only 62%/59%). Per song, derived in-page from stored lyrics (no text kept):
  ax  = chorus vs verse 1 on [shorter lines, more repeated line-endings, more token repetition]
  ctl = verse 2 vs verse 1 on the same three axes (control: two sections that should NOT contrast)
Chorus = tag chorus/hook/refrain excluding pre-/post-, else most-repeated first line. 54 songs
(Now 28 + Weekly 26), 2026-09-30. Deterministic, stdlib only.

PREDICTION (written after seeing the encoded rows, before computing any rate):
  P1 >= 60% of songs show >= 2 of 3 axes in the chorus direction
  P2 that share beats the verse2-vs-verse1 control by >= 20 points
  P3 token repetition is the most frequent contrast axis (above line length)
  P4 break: collapsing identical rows leaves the P1 verdict unchanged
"""
NOW = "001,010,2,1,0,- ; 101,011,9,0,1,1 ; 011,001,2,0,1,- ; -,-,0,-,-,- ; 101,000,4,0,1,1 ; 000,000,3,0,1,1 ; -,-,3,0,1,1 ; -,-,0,-,-,- ; 110,101,3,1,0,0 ; 001,101,2,0,1,- ; -,-,2,1,0,- ; 100,100,3,0,1,0 ; 111,111,4,0,1,1 ; -,-,3,0,1,1 ; -,-,0,-,-,- ; 000,001,2,0,1,- ; 100,110,3,0,1,0 ; 100,110,3,0,1,0 ; -,-,0,-,-,- ; 111,101,3,0,1,1 ; 011,001,3,0,1,0 ; 100,101,3,0,1,0 ; 111,100,9,0,1,0 ; 000,101,2,1,0,- ; 011,000,3,1,0,0 ; 111,100,3,0,1,0 ; -,-,0,-,-,- ; 100,-,3,0,1,1"
WEEKLY = "100,110,3,0,1,0 ; 111,001,2,1,0,- ; 111,000,2,1,0,- ; 110,100,2,0,1,- ; 111,001,6,0,1,1 ; 100,101,2,0,1,- ; 011,-,2,0,1,- ; 011,-,1,-,-,- ; 111,101,2,1,0,- ; 111,-,1,-,-,- ; 000,100,2,0,1,- ; 011,001,3,0,1,1 ; 100,110,3,0,1,0 ; 101,111,4,0,1,1 ; 100,101,6,0,1,1 ; 100,100,3,0,1,0 ; 001,001,2,1,0,- ; 011,111,2,1,0,- ; 000,011,3,0,1,1 ; 100,001,2,1,0,- ; 111,001,3,0,1,0 ; -,-,0,-,-,- ; -,-,0,-,-,- ; 100,101,1,-,-,- ; 100,-,1,-,-,- ; 100,110,3,0,1,0"
ROWS = [r.strip() for r in (NOW + " ; " + WEEKLY).split(";")]


def parse(rows):
    out = []
    for r in rows:
        ax, ctl, *_ = r.split(",")
        out.append(([int(c) for c in ax] if ax != "-" else None, [int(c) for c in ctl] if ctl != "-" else None))
    return out


def stats(rows):
    P = parse(rows)
    withax = [a for a, c in P if a]
    two = sum(1 for a in withax if sum(a) >= 2) / len(withax)
    pairs = [(a, c) for a, c in P if a and c]
    ch2 = sum(1 for a, c in pairs if sum(a) >= 2) / len(pairs)
    ct2 = sum(1 for a, c in pairs if sum(c) >= 2) / len(pairs)
    axis = [sum(a[i] for a in withax) / len(withax) for i in range(3)]
    return len(withax), two, len(pairs), ch2, ct2, axis


n, two, npairs, ch2, ct2, axis = stats(ROWS)
dn, dtwo, *_ = stats(list(dict.fromkeys(ROWS)))
res = [("P1 >=2 axes in >= 60%", two >= 0.60, f"{two:.0%} of {n}"),
       ("P2 beats control by >= 20 pts", ch2 - ct2 >= 0.20, f"chorus {ch2:.0%} vs verse2 {ct2:.0%} (n {npairs})"),
       ("P3 repetition axis most frequent", axis[2] > axis[0], f"length {axis[0]:.0%}, end-repeat {axis[1]:.0%}, token-repeat {axis[2]:.0%}"),
       ("P4 break: dedupe keeps P1", (dtwo >= 0.60) == (two >= 0.60), f"deduped {dtwo:.0%} of {dn}")]
for name, ok, d in res:
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {d}")
k = sum(ok for _, ok, _ in res)
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; >=2 axes {two:.0%} (n {n}); paired chorus {ch2:.0%} vs control {ct2:.0%} (n {npairs}); "
      f"axes length {axis[0]:.0%} end-repeat {axis[1]:.0%} token-repeat {axis[2]:.0%}; deduped {dtwo:.0%}")
