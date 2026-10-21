# Rebuild of: retreat compression and a repeated-rhythm hook coexist if you shrink WORDS but hold SYLLABLES; the
# one-word last line ALWAYS breaks the rhythm. Own lines with hand-written per-word syllables.
# BREAK: a single long word that carries the full syllable count.
def spread(lines): s = [sum(x) for x in lines]; return max(s) - min(s), s
CUT_SYLL = [[1, 1, 1, 2, 1, 1, 1], [1, 2, 1, 1, 1], [1, 2], [1]]            # cut words and syllables together
HOLD = [[1, 1, 1, 2, 1, 1, 1], [2, 1, 2, 1, 2], [4, 4], [3, 5]]             # 7,5,2,2 words at 8 syllables each
ONE_WORD_TYPICAL = [[1, 1, 1, 2, 1, 1, 1], [2, 1, 2, 1, 2], [4, 4], [2]]      # last line one ordinary word
ONE_WORD_LONG = [[1, 1, 1, 2, 1, 1, 1], [2, 1, 2, 1, 2], [4, 4], [8]]         # "incomprehensibility" = 8 syllables
for name, L in [("cut syllables", CUT_SYLL), ("hold syllables", HOLD), ("one-word typical", ONE_WORD_TYPICAL), ("BREAK one long word", ONE_WORD_LONG)]:
    sp, s = spread(L); print(f"{name:20s} words {[len(x) for x in L]} syllables {s} spread {sp}")
a, b, c, d = (spread(x)[0] for x in (CUT_SYLL, HOLD, ONE_WORD_TYPICAL, ONE_WORD_LONG))
ok = a > 0 and b == 0 and c > 0 and d > 0
print("RESULT: %s cut-syllables spread %d, hold-syllables spread %d, one ordinary word spread %d, one 8-syllable word spread %d (the 'always breaks' part is refuted by a long single word)" % ("PASS" if ok else "FAIL", a, b, c, d))
