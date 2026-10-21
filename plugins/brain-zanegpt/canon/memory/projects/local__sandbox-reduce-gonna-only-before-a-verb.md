# local/sandbox-reduce-gonna-only-before-a-verb — lessons

Project: local/sandbox-reduce-gonna-only-before-a-verb. Newest first.

---

## E1 — reduce gonna only before a verb
- Date: 2026-09-30
- Project: local/sandbox-reduce-gonna-only-before-a-verb
- Tags: [songwriting][lyrics][suno-prompting][testing]
- What: Refutes most of the reduced-forms kernel's syllable claim: of gonna, wanna, kinda and hafta only going to becomes shorter (3 to 2 syllables), so writing full forms misstated the count on 4 of 8 reducing lines, not all of them, and no line crossed the slack-3 warning either way.
- Why built: Compose the write-the-reduced-form kernel with the syllable-slack lesson and the hyphenate mis-split lesson to see whether full forms on the page flip crowded-line warnings.
- Design: Ten hand-transcribed lines as written and as sung, hand syllable counts, budget 9 with a warning above 12 syllables. Compared page and sung counts per line, and two automatic reducers: a blind regex rewriting every going to, want to, kind of and have to, and a rule that reduces going to, want to and have to only before a bare verb.
- Got right: The verb-only reducer matched the sung form on 10 of 10 lines; the blind regex was wrong on 2 of 10, turning going to the store and going to church into gonna, which nobody sings.
- Where/why it failed: The prediction that the page overcounts by one syllable per reduction was wrong: want to, kind of and have to are two syllables before and after reduction, so only going to changes the count, and no line crossed the warning threshold, so the kernel's warning-flip mechanism never appeared.
- Fix: Count syllables from the sung form but expect a difference only for going to (and because to cause); reduce going to only before a bare verb, never before a noun phrase of motion.
- Why this fix: The sandbox showed the syllable risk is confined to one common reduction, while the misapplied rewrite changes meaning, which is the larger error for a tool that auto-reduces lyrics.
- Rule of thumb: Of gonna, wanna, kinda and hafta only gonna saves a syllable (going to is 3, the others stay 2), so the real risk is rewriting going to the store as gonna; reduce going to only before a bare verb.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are hand syllable counts copied from its output. How Suno pronounces full versus reduced forms is outside this sandbox.
- Composed: ideas:SONGWRITING/diction/write-the-reduced-form-you-will-sing, sandbox-syllable-slack-and-undercount-hide-crowded-lines-from-hyphenate-rule/E1, suno-builder/E8
- Polarity: incompatible
- Sandbox: sandboxes/2026-09-30__reduce-gonna-only-before-a-verb.py
- Prediction: page overcounts by exactly one per reduction; at least 2 lines warn on paper but not sung; the blind regex undercounts 2 motion lines and the verb-only rule reduces none.
- Observed: RESULT: FAIL overcount equals reductions on 4/8 reducing lines (only going-to loses a syllable); paper-only warnings 0; blind regex wrong 2/10, verb-only wrong 0/10
- Scenarios: 1) future going to before a verb; 2) wanna, kinda and hafta lines; 3) going to before a place (motion), built to break the blind reducer; 4) lines with no reduction.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Audited: 2026-10-12 · modeled · Read the entry and its stored sandbox and re-ran it (RESULT: FAIL, matching the entry's Observed line, which is the honest outcome for its own prediction). The counting part computes: page versus sung syllable differences and the two reducers are real code, and the refuted prediction was reported rather than hidden. Two weaknesses cap it at modeled. First, the central finding that only going to loses a syllable is built into the hand-written syllable table (going 2 plus to 1 against gonna 2, while want plus to, kind plus of and have plus to equal their reduced forms), so the sandbox restates the table rather than measuring pronunciation. Second, the verb-only reducer scoring 10 of 10 depends on a VERBS set and a set of sung forms that the author wrote for these same ten lines, so it fits the fixture and does not show the rule works on unseen lyrics. The claim concerns how real singers and Suno pronounce these forms, which no real source was consulted for. · scheduled brain train auto loop 2 pass 3 (audit mode), session_01AmRWsr5yjKRMmEK2r9Dtgx
