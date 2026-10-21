"""Sandbox: do stored songwriting kernels hold on real Suno Trending lyrics?

Data: 54 unique songs from suno.com Trending (Weekly 26 + Now 28), 2026-09-30. Features were
computed in-page from each clip's stored lyrics; only derived numbers are kept here (no lyric text).
Row: [latin_title, latin_lyrics, has_tags, chorus_method(0 none,1 text-repeat,2 tag),
      text_vs_tag_agree(1 agree, 0 disagree, -1 text found nothing, None n/a), title_content_words,
      chorus_lines_n, title_hit_lines_in_first_chorus_h, title_in_first_line_any_chorus,
      title_in_last_line_any_chorus, title_anywhere_in_chorus, verse_chars_per_line, chorus_chars_per_line]
Chorus = sections tagged chorus/hook/refrain, else the most-repeated first line (tie -> more lines);
untagged lyrics split on blank lines. Title match = ordered content-word subsequence, hyphens split,
stopwords dropped (per lyrics-structure E3 and title-position lessons). Deterministic, stdlib only.

PREDICTION (written before the first run):
  P1 title power position: of Latin songs whose title appears in the chorus, >= 70% have it in the
     first or last chorus line, AND that rate beats the random-placement expectation by >= 20 pts.
  P2 section contrast: chorus chars/line < verse chars/line in >= 60% of songs having both.
  P3 chorus detection: among tagged songs where text-repeat found a group, it agrees with the tag
     choice in >= 90% (the structure-by-role lesson reported 8/8).
  P4 break: collapsing identical feature rows (contest remixes reuse one lyric) leaves the P1 and
     P2 verdicts unchanged.
"""
from math import comb

R = [
    [1,1,0,1,None,2,1,1,1,1,1,12.3,10],[1,1,1,2,1,1,4,0,1,0,1,18.3,21.8],[1,1,1,2,1,2,6,0,0,0,0,24.7,10.3],
    [1,0,1,2,-1,1,5,1,1,0,1,58.8,42.6],[0,0,1,2,0,0,None,None,None,None,None,21.3,8.3],[1,1,1,2,-1,3,2,0,1,0,1,31.2,28],
    [1,1,1,2,1,1,2,0,0,0,0,20.8,10.5],[1,1,1,2,-1,3,6,0,0,0,0,14.5,20.3],[1,1,0,1,None,2,9,3,0,0,1,21.6,21.2],
    [1,1,1,2,-1,2,4,2,1,1,1,35,19.8],[0,0,1,2,-1,0,None,None,None,None,None,13.2,14.3],[1,1,0,1,None,2,4,1,1,0,1,25.1,28.5],
    [1,1,0,1,None,2,1,1,1,1,1,12.3,10],[0,0,1,2,1,0,None,None,None,None,None,12.6,4.8],[1,0,0,1,None,3,2,1,1,0,1,17.7,19],
    [1,0,0,1,None,2,10,2,0,0,1,19.6,16.5],[0,0,1,2,-1,0,None,None,None,None,None,12,10],[1,1,1,2,1,2,6,0,0,0,1,12.5,13.3],
    [0,0,1,2,-1,1,4,1,0,1,1,13.5,16.8],[1,0,1,2,1,2,6,0,0,0,0,27.5,17],[1,0,1,2,1,2,4,0,0,0,0,27,24.5],
    [0,0,0,0,None,0,None,None,None,None,None,None,None],[1,0,1,2,-1,1,2,0,0,0,0,19.3,28],[1,0,1,2,1,1,3,0,1,0,1,25.2,32.7],
    [0,0,1,2,-1,0,None,None,None,None,None,20.4,15.8],[1,1,0,1,None,2,1,1,1,1,1,12.3,10],[1,1,1,2,1,1,4,0,0,0,0,39.8,44],
    [1,1,1,2,1,2,2,1,1,0,1,24.1,22.5],[1,0,1,2,-1,3,6,0,1,1,1,29.6,27.7],[0,0,1,0,None,0,None,None,None,None,None,None,None],
    [1,0,0,1,None,1,2,0,0,0,0,15.9,16],[1,0,0,1,None,1,4,0,0,0,0,17.2,22],[1,1,1,1,None,2,7,2,1,0,1,None,None],
    [1,1,0,0,None,1,None,None,None,None,None,None,None],[0,0,1,2,-1,3,8,0,0,0,0,22.6,21.3],[1,0,1,2,-1,3,6,0,0,0,1,22.1,25.3],
    [0,0,1,1,None,4,4,0,0,0,0,None,None],[1,0,0,1,None,1,8,0,0,0,0,14.6,13.6],[1,1,1,2,1,1,17,0,0,0,0,16.9,3.4],
    [1,0,1,1,None,2,3,0,0,0,0,None,None],[1,1,0,0,None,2,None,None,None,None,None,None,None],[0,0,1,2,-1,0,None,None,None,None,None,28,30.5],
    [1,1,0,1,None,2,1,1,1,1,1,12.3,10],[1,1,0,1,None,2,1,1,1,1,1,12.3,10],[1,1,0,0,None,2,None,None,None,None,None,None,None],
    [0,0,1,2,-1,0,None,None,None,None,None,7.2,7.8],[1,1,0,1,None,2,8,4,1,0,1,22.9,16.1],[1,1,1,2,1,1,4,0,1,0,1,18.6,17],
    [1,1,0,1,None,2,2,2,1,1,1,10.8,13],[1,1,0,1,None,2,5,0,0,0,0,17.9,22.2],[1,1,0,1,None,1,10,3,0,1,1,27.2,25.3],
    [1,1,0,1,None,2,10,7,1,1,1,36.9,14.9],[0,0,1,0,None,0,None,None,None,None,None,None,None],[1,0,1,2,1,3,8,0,0,0,0,19.4,15.3],
]


def p_power_by_chance(n, h):
    """P(at least one of h hit lines lands on line 1 or line n) if hits are placed at random."""
    h = max(1, min(h, n))
    if n <= 2:
        return 1.0
    return 1 - comb(n - 2, h) / comb(n, h)


def p1(rows):
    s = [r for r in rows if r[0] and r[1] and r[10] == 1]
    power = sum(1 for r in s if r[8] or r[9])
    exp = sum(p_power_by_chance(r[6], r[7]) for r in s)
    rate, chance = power / len(s), exp / len(s)
    return len(s), rate, chance, (rate >= 0.70 and rate - chance >= 0.20)


def p2(rows):
    s = [r for r in rows if r[11] is not None and r[12] is not None]
    shorter = sum(1 for r in s if r[12] < r[11])
    rate = shorter / len(s)
    return len(s), rate, rate >= 0.60


def p3(rows):
    s = [r for r in rows if r[3] == 2 and r[4] in (0, 1)]
    agree = sum(1 for r in s if r[4] == 1)
    nothing = sum(1 for r in rows if r[3] == 2 and r[4] == -1)
    return len(s), agree / len(s), nothing, agree / len(s) >= 0.90


def dedupe(rows):
    seen, out = set(), []
    for r in rows:
        k = tuple(r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


n1, r1, c1, ok1 = p1(R)
n2, r2, ok2 = p2(R)
n3, a3, none3, ok3 = p3(R)
D = dedupe(R)
dn1, dr1, dc1, dok1 = p1(D)
dn2, dr2, dok2 = p2(D)
ok4 = (dok1 == ok1) and (dok2 == ok2)

print(f"P1 title power position: {'PASS' if ok1 else 'FAIL'}  n {n1}, first/last {r1:.2f}, chance {c1:.2f}")
print(f"P2 chorus shorter lines: {'PASS' if ok2 else 'FAIL'}  n {n2}, rate {r2:.2f}")
print(f"P3 text-repeat agrees with tag: {'PASS' if ok3 else 'FAIL'}  n {n3}, agree {a3:.2f}, text found nothing in {none3} tagged songs")
print(f"P4 break (dedupe {len(R)}->{len(D)}): {'PASS' if ok4 else 'FAIL'}  P1 n {dn1} rate {dr1:.2f} chance {dc1:.2f} ({'PASS' if dok1 else 'FAIL'}); "
      f"P2 n {dn2} rate {dr2:.2f} ({'PASS' if dok2 else 'FAIL'})")
k = sum([ok1, ok2, ok3, ok4])
print(("RESULT: PASS " if k == 4 else "RESULT: FAIL ") +
      f"{k}/4; title first/last {r1:.2f} vs chance {c1:.2f} (n {n1}; deduped {dr1:.2f} vs {dc1:.2f}, n {dn1}); "
      f"chorus shorter {r2:.2f} (n {n2}; deduped {dr2:.2f}); text-vs-tag agree {a3:.2f} (n {n3}), text-repeat empty in {none3}")
