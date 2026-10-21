# local/sandbox-compress-words-not-syllables-to-keep-a-repeated-rhythm — lessons

Project: local/sandbox-compress-words-not-syllables-to-keep-a-repeated-rhythm. Newest first.

---

## E1 — sandbox compress words not syllables to keep a repeated rhythm
- Date: 2026-09-30
- Project: local/sandbox-compress-words-not-syllables-to-keep-a-repeated-rhythm
- Tags: [songwriting][structure][testing]
- What: Deterministic check that the retreat-compression kernel (shrinking lines signal withdrawal) and the repeated-rhythm hook (lines with near-identical syllable counts) conflict only when compression is done in syllables. Cutting words gives words 7, 5, 2, 1 with syllables 8, 5, 5, 2 (spread 6, rhythm broken). Compressing in words while holding syllables gives words 7, 5, 2, 2 with syllables 8, 8, 8, 8 (spread 0), satisfying both.
- Why built: The two kernels look like they pull in opposite directions in the same section, one shrinking the line and one holding its length, so this tests whether they can coexist and where they stop.
- Design: sb/music/t9_compression_rhythm.py with hand-counted syllables per word. Three 4-line drafts: compress by cutting words, compress by swapping in longer words, and hold both. Compression means word counts never rise and end below the start; repeated rhythm means syllable spread of 1 or less. Also computes the fewest words that can carry a 6, 8 or 10 syllable line when the longest word has 5 syllables.
- Got right: The longer-word draft (honestly unbelievably; eventually nevermind) holds 8 syllables per line while dropping from 7 words to 2, so both kernels hold at once.
- Where/why it failed: The compression floors at 2 words for any 6 to 10 syllable rhythm with a 5-syllable longest word, so the classic one-word last line (goodbye) always breaks a repeated rhythm. It also changes texture: the short lines become long, Latinate words, which may read as the opposite of withdrawal.
- Fix: When a chorus must keep a repeated rhythm, compress by word count and hold the syllable count, stop at two words, and save the one-word collapse for a section that is not the hook.
- Why this fix: The two kernels measure different units (words versus syllables), so they only collide when a writer lets both units shrink together.
- Rule of thumb: Compression and repeated rhythm coexist if you shrink words but hold syllables (7 to 2 words at 8 syllables each); the one-word last line always breaks the rhythm, so keep it out of the hook.
- Provenance (verified/assumed): Verified first-hand by running sb/music/t9_compression_rhythm.py; counts are observed output from hand syllable counts. Whether listeners hear long-word lines as withdrawal is not tested.
- Composed: ideas:SONGWRITING/structure/retreat-compression, ideas:SONGWRITING/hooks/five-named-techniques-for-a-memorable-melodic-hook
- Link: scheduled training session, music batch
- Reverified: 2026-09-30 · fail · sandboxes/2026-09-30__rebuild-compress-words-hold-syllables.py · observed RESULT: FAIL cut-syllables spread 7, hold-syllables spread 0, one ordinary word spread 6, one 8-syllable word spread 0 (the 'always breaks' part is refuted by a long single word) · Own fixture: four hand-counted drafts (cut words and syllables together; 7/5/2/2 words at 8 syllables each; a one-word last line of an ordinary 2-syllable word; and a one-word last line carrying 8 syllables, incomprehensibility, as the break case). The original used three drafts and assumed the longest available word has 5 syllables (read only after the run). The main claim reproduces: cutting syllables gives spread 7, while holding syllables gives 7/5/2/2 words at 8/8/8/8 with spread 0, so compression and repeated rhythm coexist. But the rule says the one-word last line always breaks the rhythm, and a single 8-syllable word keeps spread 0. The always part rests on the original's 5-syllable word cap. The rule should be narrowed: a one-word line breaks an N-syllable rhythm unless one word carries N syllables, which is rare for N of 6 or more. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
- Cited-by: 2026-09-30 · projects/local__sandbox-new-idea-count-needs-stems-and-stopwords.md#E1 · compatible · sandboxes/2026-09-30__new-idea-count-needs-stems-and-stopwords.py · observed RESULT: FAIL raw new-token count off on 9/12, stem+stopword count off on 7/12, over-three flag off on 0/12; compressed long-word lines score 2 each · https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
