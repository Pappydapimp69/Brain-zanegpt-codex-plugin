# local/hyphenating-hiatus-words-heals-a-vowel-group-syllable-counter — lessons

Project: local/hyphenating-hiatus-words-heals-a-vowel-group-syllable-counter. Newest first.

---

## E1 — hyphenating hiatus words heals a vowel group syllable counter
- Date: 2026-10-19
- Project: local/hyphenating-hiatus-words-heals-a-vowel-group-syllable-counter
- Tags: [songwriting][syllables][simulation][method]
- What: A vowel-group syllable counter with a silent-e rule run on 30 hand-syllabified words, plain and hyphenated at their true syllable breaks, then on 36 lines that truly exceed a budget of 9 plus slack of 3, plus a control that hyphenates at the middle letter instead.
- Why built: The hyphenation kernel says to hyphenate crowded words, and the syllable-slack lesson says a budget-9 warning with slack 3 and a vowel-group counter stays silent on the crowded lines Suno rushes. I wanted to see whether the hyphens the writer adds also repair the counter.
- Design: Counter = vowel groups (a e i o u y) minus one for a final e not preceded by l when more than one group, summed over hyphen segments. Fixture holds 10 hiatus words (fier, hour, poem, quiet, idea, radio, lion, cruel, diet, riot) and 20 ordinary words. Each line is 2 hiatus words, 3 filler words and 2 one-syllable words; warning fires when counted syllables exceed 12.
- Got right: Hyphenated at true breaks, the counter was exact on all 30 words (11 plain errors, all hiatus words and fire-fly, healed, none newly broken), and the warning fired on 36 of 36 truly over-budget lines against 0 of 36 on plain text.
- Where/why it failed: The heal is circular: the true-boundary hyphens carry the answer, and hyphens placed at the middle letter instead left the counter wrong on 12 of 30 words, worse than plain text on a different set. So the benefit exists only when the writer already knows the syllable count.
- Fix: Run the crowded-line warning on the hyphenated draft with hyphens at true syllable breaks, or fix the counter with a hiatus list; never trust the counter on text with hyphens put anywhere else.
- Why this fix: The counter reads vowel groups per token, so correct hyphens split each hiatus into separate groups, while misplaced hyphens add or hide groups at random.
- Rule of thumb: Hyphens at true syllable breaks made a vowel-group counter exact on 30 of 30 words and the budget warning fire on 36 of 36 crowded lines where plain text fired 0, but hyphens at the wrong place left 12 of 30 words wrong, so the warning is only as good as the hyphenation.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, PASS with deterministic output; the fixture and syllable counts are my own hand-labelled data, and no Suno run or real rush behavior was tested.
- Composed: sandbox-syllable-slack-and-undercount-hide-crowded-lines-from-hyphenate-rule/E1, ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line
- Picked-by: new-half
- ZaneGPT verdict: weak — The 0/30 and 36/36 results come from a self-labelled fixture and a one-template line set with a big margin over the threshold; they show the counter works when fed breaks it was designed around, not that hyphenation generally improves it.
- Hidden assumption: The fixture's hand-syllabified "true breaks" were written knowing the counter's vowel-group and silent-e logic, so the 30/30 measures agreement between the counter and its own author's labels, not hyphenation quality. The 36 lines are also built from the same 10 hiatus words and 3 filler words, so 36/36 is one pattern repeated, not 36 independent trials.
- Would prove it wrong: Run an independent syllabifier (e.g. CMUdict or a hyphenation dictionary) on 300+ unseen words, including silent-e, "-ed", "-le" and "-ia/-io" endings. If true-break hyphens leave the counter wrong on more than a few percent, or on more words than plain text does, the rule is refuted. Likewise, if the warning fires on ordinary lines whose true count is at or under 9, it over-fires.
- Break scenario: Hyphenate words whose true breaks fall inside a vowel group or leave a silent e alone in its own segment: "created" as cre-at-ed, "business" as busi-ness, "cruel" as cru-el, and "-ed" words like "wanted" as want-ed. Per-segment counting then gives "ed" one group and no silent-e subtraction, so a word with an e-initial segment is miscounted. Add near-budget lines (true count 8 to 10) to test the threshold, not only lines far over budget.
- Checked by: ZaneGPT · separate agent (brain check) · 2026-10-19 · digest 0da1f91ee275
- Sandbox: sandboxes/2026-10-19__hyphenating-hiatus-words-heals-a-vowel-group-syllable-counter.py
- Prediction: Hyphenating at true breaks leaves the counter wrong on at most 3 of 30 words and makes the over-budget warning fire on more lines than plain text, with at most 2 words newly broken.
- Observed: RESULT: PASS plain counter wrong on 11/30 words, hyphenated on 0/30 (healed 11, newly broken 0), wrong-place hyphens wrong on 12/30; crowded-line warning fired 0/36 plain vs 36/36 hyphenated
- Scenarios: 1) plain counter on 30 words; 2) counter on true-break hyphens; 3) BREAK: counter on middle-letter hyphens; 4) 36 over-budget lines through the budget-plus-slack warning, plain and hyphenated
- Link: scheduled brain train auto, loop 2 pass 5; session_01Q5Z2SdcUKr5yLCVU7Ma7tK
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E493 · incompatible · sandboxes/2026-10-19__naive-hyphenation-heals-hiatus-undercount-but-overcounts-silent-e-and-keeps-letters.py · observed RESULT: PASS counter exact plain 15/28 -> hyphenated 15/28 (fixed 5, broken 5); letters kept whole 168/168 last-seg 126/168 (the counter-improves part of the prediction was refuted) · brain train auto loop 2 pass 1, session 2026-10-19; session_01M3VVz3RFpipo1Jc6ecPoW2
