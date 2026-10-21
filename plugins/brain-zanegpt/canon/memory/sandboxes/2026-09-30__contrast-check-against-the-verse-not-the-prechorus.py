# Composes: the verse-and-chorus-differ kernel (warn when the chorus differs from the section before it on
# fewer than two of: mean syllables per line, lines per section, rhyme scheme), sandbox-structure-check-by-
# section-role-not-tag-name/E1 (judge sections by role) and the standard-pop-structure kernel (V-PC-C form).
# PREDICTION (written before running): 6 song outlines, hand-labelled contrast ok / verse-1b.
# 1) comparing each chorus to the section immediately before it misjudges both songs that have a
#    pre-chorus that already ramps down to short lines (2 false warnings), and gets the 4 others right;
# 2) comparing each chorus to the most recent VERSE (by role) gets 6/6;
# 3) the one hand-labelled verse-1b song is caught by both methods.
def feats(sec):
    lines, syl, scheme = sec
    return (round(sum(syl) / len(syl)), lines, scheme)
def axes_differ(a, b):
    fa, fb = feats(a), feats(b)
    return sum([abs(fa[0] - fb[0]) >= 2, fa[1] != fb[1], fa[2] != fb[2]])
def sec(n, syl, scheme): return (n, [syl] * n, scheme)
SONGS = {  # list of (role, section); label True = chorus contrasts properly
 "classic":      ([("verse", sec(8, 11, "ABAB")), ("chorus", sec(4, 6, "AAAA"))], True),
 "verse-1b":     ([("verse", sec(4, 9, "ABAB")), ("chorus", sec(4, 9, "ABAB"))], False),
 "ramp-prechorus": ([("verse", sec(8, 11, "ABAB")), ("pre", sec(4, 6, "AABB")), ("chorus", sec(4, 6, "AAAA"))], True),
 "ramp-prechorus-2": ([("verse", sec(6, 12, "ABCB")), ("pre", sec(2, 7, "AA")), ("chorus", sec(4, 7, "AA"))], True),
 "long-chorus":  ([("verse", sec(4, 6, "AABB")), ("chorus", sec(8, 10, "ABAB"))], True),
 "scheme-only":  ([("verse", sec(4, 9, "ABAB")), ("pre", sec(2, 9, "AA")), ("chorus", sec(4, 9, "AABB"))], False),
}
prev_ok = role_ok = 0
for name, (secs, want) in SONGS.items():
    roles = [r for r, _ in secs]; ci = roles.index("chorus")
    prev = secs[ci - 1][1]; verse = [s for r, s in secs[:ci] if r == "verse"][-1]
    p = axes_differ(secs[ci][1], prev) >= 2; v = axes_differ(secs[ci][1], verse) >= 2
    prev_ok += p == want; role_ok += v == want
    print(f"{name:17} want {want!s:5} vs-previous {p!s:5} ({axes_differ(secs[ci][1], prev)} axes) vs-verse {v!s:5} ({axes_differ(secs[ci][1], verse)} axes)")
print(f"vs previous section {prev_ok}/6; vs verse by role {role_ok}/6")
ok = prev_ok == 4 and role_ok == 6
print(("RESULT: PASS" if ok else "RESULT: FAIL") + f" chorus-vs-previous-section right on {prev_ok}/6, chorus-vs-verse-by-role right on {role_ok}/6")
