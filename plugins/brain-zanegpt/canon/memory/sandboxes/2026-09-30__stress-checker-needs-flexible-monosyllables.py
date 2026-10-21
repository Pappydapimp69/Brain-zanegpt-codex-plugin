# Composes: the natural-word-stress kernel (stressed syllables on strong beats) with
# sandbox-lyrical-composition/E5 (syllable count is a coarse proxy that collapses stress position).
# PREDICTION (written before running): 12 lines, all 8 syllables, set to a strong-weak (trochaic) grid.
# 1) syllable-count proxy passes 12/12, including the 5 hand-labelled mis-set lines;
# 2) a stress checker using dictionary stress on every syllable flags all 5 mis-set lines, but also
#    flags at least 2 of the 7 well-set lines, because dictionary-style entries give many one-syllable
#    function words (I, to, my, you, and) primary stress;
# 3) treating one-syllable function words as flexible (fit either beat) keeps 5/5 hits and drops false flags to 0.
FUNC = {"i", "to", "my", "you", "and", "the", "a", "in", "on", "of", "for", "me", "we", "it", "your", "at", "but"}
# Dictionary-style stress per syllable (1 primary, 0 unstressed), hand-entered in CMUdict's style:
# many monosyllabic function words carry 1 there (I AY1, to T UW1, my M AY1, you Y UW1), some 0 (the, a).
LEX = {"i": "1", "to": "1", "my": "1", "you": "1", "and": "1", "the": "0", "a": "0", "in": "0", "on": "1",
       "of": "1", "for": "1", "me": "1", "we": "1", "it": "1", "your": "1", "at": "1", "but": "1",
       "because": "01", "tomorrow": "010", "away": "01", "never": "10", "morning": "10", "window": "10",
       "leaving": "10", "open": "10", "summer": "10", "river": "10", "running": "10", "hold": "1",
       "light": "1", "cold": "1", "home": "1", "down": "1", "slow": "1", "night": "1", "rain": "1",
       "again": "01", "believe": "01", "forget": "01", "alone": "01", "hello": "01", "along": "01",
       "coffee": "10", "table": "10", "letters": "10", "yellow": "10", "under": "10", "waiting": "10",
       "keep": "1", "burn": "1", "walk": "1", "call": "1", "stay": "1", "gone": "1", "know": "1", "said": "1"}
GRID = "10101010"  # trochaic: strong on syllables 1,3,5,7
def syl(line):
    out = []
    for w in line.lower().split():
        for ch in LEX[w]:
            out.append((w, ch))
    return out
def proxy_ok(line): return len(syl(line)) == len(GRID)
def flags(line, flexible):
    bad = 0
    for (w, s), g in zip(syl(line), GRID):
        if flexible and w in FUNC and len(LEX[w]) == 1:
            continue
        if s != g and (s == "1" or g == "1"):
            # primary stress on a weak beat, or an unstressed syllable on a strong beat
            if s == "1" and g == "0": bad += 1
            elif s == "0" and g == "1": bad += 1
    return bad
WELL = ["morning window coffee table",        # 10 10 10 10
        "never leaving summer river",
        "yellow letters under rain and",       # ends on function words: rain(1) and(1)->weak slot
        "hold me down and keep me waiting",    # hold me down and keep me wait ing
        "call me in the morning slow i",
        "walk the river night and morning",
        "burn the letters keep the coffee"]
MIS = ["because tomorrow away i",              # be-CAUSE starts weak syllable on strong beat
       "again believe forget alone",
       "hello along because away",
       "alone tomorrow again i",
       "forget the morning because i"]
assert all(len(syl(l)) == 8 for l in WELL + MIS), [len(syl(l)) for l in WELL + MIS]
p = sum(proxy_ok(l) for l in WELL + MIS)
strict_hit = sum(flags(l, False) > 0 for l in MIS); strict_fp = sum(flags(l, False) > 0 for l in WELL)
flex_hit = sum(flags(l, True) > 0 for l in MIS); flex_fp = sum(flags(l, True) > 0 for l in WELL)
print(f"proxy passes {p}/12 (mis-set passed: {sum(proxy_ok(l) for l in MIS)}/5)")
print(f"strict dictionary stress: mis-set flagged {strict_hit}/5, well-set falsely flagged {strict_fp}/7")
print(f"flexible function words: mis-set flagged {flex_hit}/5, well-set falsely flagged {flex_fp}/7")
for l in WELL: print("  well", flags(l, False), flags(l, True), l)
ok = p == 12 and strict_hit == 5 and strict_fp >= 2 and flex_hit == 5 and flex_fp == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL") +
      f" proxy 12/12 blind to stress; strict stress hits {strict_hit}/5 with {strict_fp}/7 false flags; flexible monosyllables hits {flex_hit}/5 with {flex_fp}/7")
