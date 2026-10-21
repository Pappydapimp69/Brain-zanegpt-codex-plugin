# local/sandbox-closure-distance-calls-xxaa-closed — lessons

Project: local/sandbox-closure-distance-calls-xxaa-closed. Newest first.

---

## E1 — sandbox closure distance calls xxaa closed
- Date: 2026-09-30
- Project: local/sandbox-closure-distance-calls-xxaa-closed
- Tags: [songwriting][rhyme][testing]
- What: Re-verification of the closure-distance metric (lyrical-composition E8) against the rhyme-scheme-shape kernel's full list of four named schemes. The metric reproduces AABB stable and ABBA open, but it scores XXAA as closed (max distance 1), while the kernel calls XXAA an open journey with a surprise resolution.
- Why built: E8 checked closure distance against six schemes but the kernel names four with verdicts, and XXAA was the one named scheme whose openness comes from delay rather than distance, so it was the case most likely to separate the metric from the claim.
- Design: Deterministic Python (sb/music/t3_closure_vs_xxaa.py) computing for each scheme the closure distances, the max, the number of unrhymed lines, and the line on which the first rhyme closes, across AABB, ABAB, ABBA, XXAA, AAAA, ABCB and XAXA.
- Got right: Closure distances match E8 exactly (AABB [1,1], ABAB [2,2], ABBA [1,3], AAAA [1,1,1], ABCB [2]), and with an open threshold of max distance 3 or more, AABB, ABAB and ABBA get the kernel's verdict.
- Where/why it failed: XXAA has closure [1], so distance calls it closed. Its openness comes from the first resolution arriving only on line 4. The first-close line alone does not work either, because ABAB and ABBA both first close on line 3.
- Fix: Use two measurements: max closure distance for ABBA-style openness, and the first line that closes for XXAA-style delay. The rule open if max distance is 3 or more, or if nothing closes before the last line, matches all four of the kernel's named verdicts.
- Why this fix: The kernel describes two different ways a stanza stays open (pairs held far apart, and resolution held back), and each one is invisible to the other's metric.
- Rule of thumb: Closure distance misses stanzas that stay open by delaying the first rhyme (XXAA scores 1 like AABB); pair it with first-closing line before labelling a scheme open or stable.
- Provenance (verified/assumed): Verified first-hand by running sb/music/t3_closure_vs_xxaa.py; all printed distances and first-close lines are observed output. Whether listeners hear XXAA as open is the kernel's claim, not tested here.
- Composed: sandbox-lyrical-composition/E8, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion
- Link: scheduled training session, music batch
- Reverified: 2026-09-30 · pass · sandboxes/2026-09-30__rebuild-closure-distance-xxaa.py · observed RESULT: PASS XXAA distance 1 = AABB 1, ABBA 3; first-close separates them (4 vs 2); other distance-1 late closers: ['XAAA', 'XAAX', 'XXAA']; 6-line XXXXAA also distance 1 first-close 6 · Own fixture: exhaustive enumeration of all 15 set partitions of 4 lines (singletons as X) plus four 6-line schemes, with my own definition of closure distance as the max gap between consecutive members of a rhyme group; the original hand-listed 7 schemes (AABB, ABAB, ABBA, XXAA, AAAA, ABCB, XAXA) (read only after the run). XXAA scores distance 1 exactly like AABB while ABBA scores 3, and first-closing line separates them (4 against 2). The enumeration found the blind spot is wider than XXAA: XAAA and XAAX also tie AABB on distance while closing later, and the 6-line XXXXAA scores 1 with first close on line 6. So pairing distance with first-closing line, as the rule says, is needed for a whole class of late-opening schemes, not just XXAA. · https://claude.ai/code/session_01PXuEX9SfJcr8Mxg6sK6stu
- Cited-by: 2026-09-30 · projects/local__sandbox-one-stray-merge-flips-open-verdicts.md#E1 · compatible · no sandbox · scheduled training session, music batch
- Cited-by: 2026-09-30 · projects/local__suno.md#E14 · compatible · sandboxes/2026-09-30__rhyme-scheme-openness-needs-wait-age-not-pending-count.py · observed RESULT: PASS 4/4; L AABB/ABAB/ABBA 0.50/1.00/1.00, A 0/1/2; 4-line L-shared 80%, triple-shared 13%; 6-line triple-shared 74% · session 2026-09-30 brain train loop 5 (rhyme)
- Cited-by: 2026-10-15 · projects/pappydapimp69__suno-builder.md#E12 · incompatible · sandboxes/2026-10-15__builder-letters-feed-two-metric-closure-rule.py · observed RESULT: FAIL A scheme 1/8 B scheme 4/8 B verdict 3/4 (set A first draft with blue/through; set B spelling-matched where XXAA came back AABB). · https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E12 · incompatible · sandboxes/2026-10-15__line-splitting-for-suno-pace-flips-abab-open-under-closure-distance.py · observed RESULT: PASS wrong verdicts out of 8: hyphenate 0, split-all raw 2 ['ABAB#2', 'ABAB#3'], partial split raw 2 ['ABAB#2', 'ABAB#3'], halve-distances fix 0 all / 1 partial, source-line-end fix 0/0; break XXAA raw stable vs fixC open. · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 5 pass 5
