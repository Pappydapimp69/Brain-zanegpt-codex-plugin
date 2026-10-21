# pappydapimp69/suno-builder — lessons

Project: pappydapimp69/suno-builder. Newest first.

---

## E13 — whole line hyphenation leaves letters and shape but raises counts
- Date: 2026-10-15
- Project: Pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][suno-prompting][testing]
- What: Hyphenating every word of every line, not just the last word, left the two-pass
  letters and the scheme-shape note unchanged in 42 of 42 stanzas of the real suno-builder,
  while counted line syllables rose in 25 of 168 lines (14%) and fell in none.
- Why built: New-half train pick: edge between the two-pass lettering kernel and the
  scheme-shape kernel, with the hyphenate-to-slow-a-rushed-line kernel as companion; the
  earlier lesson tested only the last word of four stanzas.
- Design: Ran the real builder headless via node on 40 seeded random four-line stanzas
  plus a pre-hyphenated stanza and a silent-e stanza, applying hyphenate() to every word
  and comparing analyseSection scheme, SCHEME_NOTES verdict and per-line syllables.
- Got right: Shape is safe under any amount of hyphenation: rhymeKey strips hyphens before
  it reads the vowel and coda, so letters and the shape note cannot move (42/42 each).
- Where/why it failed: My prediction that 25% or more of lines would gain syllables was
  wrong (14%), because most words in the lexicon are one-syllable or split into parts the
  counter already counted; the count still never fell, so hyphenation cannot make room.
- Fix: When slowing a rushed line, treat letters and shape as free and budget only the
  counted syllables; do not expect hyphens to shrink a line that trips a length warning.
- Why this fix: The kernel changes how the singer delivers words, not how many there are;
  the builder's counter reads that as equal or more, so only cutting words lowers it.
- Rule of thumb: Hyphenating words in the tested stanzas never changed rhyme letters or the
  shape verdict and never lowered a syllable count; pick the line cut, not the hyphen, to fit.
- Provenance (verified/assumed): verified first-hand by running the reference suno-builder.html
  with the sandbox below; I assume but did not test stanzas longer than four lines.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line, ideas:SONGWRITING/rhyme-scheme-shape-sets-a-songs-emotional-motion, ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__whole-line-hyphenation-leaves-letters-and-shape-but-raises-counts.py
- Prediction: Written before the first run: letters and shape verdict unchanged in all
  stanzas; syllables rise in at least 25% of lines and never fall.
- Observed: RESULT: FAIL letters 42/42 note 42/42 up 25/168 down 0 (invariance held; the
  25% size guess missed at 14%).
- Scenarios: 1) 40 seeded random four-line stanzas; 2) a stanza with words already
  hyphenated (moon-light); 3) a silent-e ending stanza built to break the count (desire,
  fire, believe, receive).
- Link: https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4
- Cited-by: 2026-10-15 · projects/local__sandbox-shorten-rushed-lines-keep-the-rhyme-word.md#E1 · compatible · sandboxes/2026-10-15__sandbox-shorten-rushed-lines-keep-the-rhyme-word.py · observed RESULT: PASS shorten-from-the-front keeps 4/4 shapes at 5.0 words/line (from 11.1), cutting the line end keeps 0/4, hyphenation keeps 4/4 but leaves words/line 11.1 and syllables 15.8 unchanged · brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2

## E12 — builder letters feed two metric closure rule
- Date: 2026-10-15
- Project: Pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][testing][tooling]
- What: Feeding stanzas written to hit the seven scheme shapes into the real suno-builder
  analyseSection gave the intended letters in only 1 of 8 first-draft stanzas and 4 of 8
  after matching every rhyming pair's spelling, so the closure-distance plus first-closing-line
  rule could only be checked against the letters the builder actually returned.
- Why built: New-half train pick: strong path two-pass lettering + suno-builder, with the
  closure-distance XXAA lesson as untested companion; wanted to know if the builder's real
  letters feed the two-metric open/closed rule the way hand-written schemes do.
- Design: Ran the real builder headless via node (vm, as test-engine.js does) on two fixture
  sets, computed max span between same-letter lines and first closing line from the
  returned letters, and called a stanza open when span >= 3 or first close >= 4.
- Got right: The rule itself held on first-draft letters (4 of 4 named verdicts matched
  AABB, ABAB, ABBA, XXAA when scored on whatever letters came back), because it reads
  letters, not intent.
- Where/why it failed: My prediction of 6+ of 8 intended schemes was wrong: blue/through is
  not a rhyme for the spelling judge (AABB came back AAXX), town/around is assonance only
  (lowercase), and town/stone fused into a perfect group so my XXAA fixture came back AABB,
  closed, and the rule scored 3 of 4 verdicts in the matched set.
- Fix: Score shape on the letters the builder returns and print them beside the intended
  scheme; build fixtures from word pairs the builder's own rhymeType reports as perfect or
  assonance before trusting a stanza as an XXAA or ABCB example.
- Why this fix: The builder's judge is a spelling heuristic, so a stanza that rhymes to a
  listener can letter differently; only the returned letters are what the shape note and
  closure metrics will ever see.
- Rule of thumb: In a rhyme-shape test, check the stanza's returned letters match the shape
  you meant before scoring the shape rule on them; a fixture the judge letters differently
  tests the judge, not the rule.
- Provenance (verified/assumed): verified first-hand by running the reference suno-builder.html
  with the sandbox below; the 1/8 and 4/8 counts and 3/4 verdicts are the printed output.
- Composed: sandbox-closure-distance-calls-xxaa-closed/E1, suno-builder/E10, ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible
- Picked-by: new-half
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-15__builder-letters-feed-two-metric-closure-rule.py
- Prediction: Written before the first run: the builder returns the intended scheme for at
  least 6 of 7 shape stanzas and the two-metric rule matches all 4 named verdicts.
- Observed: RESULT: FAIL A scheme 1/8 B scheme 4/8 B verdict 3/4 (set A first draft with
  blue/through; set B spelling-matched where XXAA came back AABB).
- Scenarios: 1) first-draft stanzas for 7 shapes plus an assonance XXaa; 2) same shapes
  rewritten with spelling-matched pairs; 3) town/stone pair built to break the XXAA fixture.
- Link: https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4

## E11 — suno hyphen fix never lowers the count
- Date: 2026-10-15
- Project: Pappydapimp69/suno-builder
- Tags: [songwriting][suno-prompting][testing][tooling]
- What: suno-builder offers a button on lines that are way over the syllable budget that
  hyphenates the longest word; in its own counter that fix never lowered a word's count
  (0 of 36) and raised it for 6 silent-e words, so the button cannot clear its warning.
- Why built: New-half train pick: the strong path two-pass lettering + suno-builder with
  the hyphenate-to-slow-a-rushed-line kernel as companion; the fix button is where the
  hyphen kernel, the syllable budget and the rhyme letters all touch one line.
- Design: Ran the real builder headless via node: hyphenate() and syllablesInWord() on a
  fixed 40-word list, and analyseSection() on four stanzas before and after hyphenating
  each line's last word.
- Got right: Rhyme letters survive the fix: 4 of 4 stanzas kept the same scheme, because
  rhymeKey strips hyphens before it reads vowel and coda, so hyphenation is invisible to
  the two-pass lettering.
- Where/why it failed: The warning counts syllables and the fix only adds hyphens, and
  syllablesInWord counts each part as at least one, so splitting can only hold or raise
  the count: desire, believe, silence, alone, awake went 2 to 3 (de-si-re, a-wa-ke).
- Fix: Make the fix reduce what the warning measures (suggest cutting or merging words),
  or count a hyphenated word by the parts Suno will sing and exempt it from the budget
  warning; also stop splitting off a silent final e as its own part.
- Why this fix: The hyphen kernel slows delivery by giving the model explicit beats; it
  was never a way to fit more words in a budget, so attaching it to an over-budget
  warning offers a cure that moves the number the wrong way.
- Rule of thumb: A one-click fix must move the metric that raised the warning; check it
  can lower that number at all before offering it.
- Provenance (verified/assumed): verified first-hand: ran the reference suno-builder.html
  with the sandbox below. Predicted a 30%+ rise; observed 17%, so the size was off but
  the direction (never lower) held on every word.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line, ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible, suno-builder/E8
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__suno-hyphen-fix-never-lowers-the-count.py
- Prediction: Written before the first run: letters change in 0 stanzas; hyphenating raises
  the counted syllables for at least 30% of 2+ syllable words.
- Observed: RESULT: FAIL letters changed in 0/4 stanzas; hyphenating raised the counted
  syllables for 6/36 2+ syllable words (17%), lowered 0.
- Scenarios: 1) 40 single words incl. silent-e words; 2) perfect-rhyme stanza; 3) mixed
  stanza with an unrhymed line; 4) XXAA stanza; 5) assonance-heavy stanza built to break
  letter preservation.
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__sandbox-shorten-rushed-lines-keep-the-rhyme-word.md#E1 · compatible · sandboxes/2026-10-15__sandbox-shorten-rushed-lines-keep-the-rhyme-word.py · observed RESULT: PASS shorten-from-the-front keeps 4/4 shapes at 5.0 words/line (from 11.1), cutting the line end keeps 0/4, hyphenation keeps 4/4 but leaves words/line 11.1 and syllables 15.8 unchanged · brain train auto, scheduled run; session_01DvSHWZUgPrcaEhdbqtMZR2
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-auto-training.md#E17 · incompatible · sandboxes/2026-10-15__subject-aux-ellipsis-frees-two-syllables-so-it-only-rescues-lines-just-over-the-suno-budget.py · observed RESULT: PASS of 19 over-budget lines hyphenation cleared 0, guarded ellipsis 2 (freed 1-2 syl), ellipsis then hyphenation 2; naive linter mangled 4/4 copular lines, guard 0 wrong blocks; 7/9 elidable warned lines still over. The PASS cover… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr auto training loop 2 pass 5

## E10 — suno scheme note case folds open letters
- Date: 2026-10-15
- Project: Pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][testing][tooling]
- What: suno-builder looks up its scheme-shape note with SCHEME_NOTES[scheme.toUpperCase()],
  so two-pass lowercase (assonance, open) letters get the uppercase shape verdict, and
  the assonance pass restarts at 'a', so AA+bb renders AAaa and folds to AAAA.
- Why built: New-half train pick: the strong path between the two-pass lettering kernel
  and the scheme-shape kernel, with suno-builder as the untested companion; the builder
  implements both, so it is the place they actually meet.
- Design: Ran the real builder headless (node vm, as test-engine.js does) and fed
  analyseSection six fixed stanzas whose pair types come from its own rhymeType:
  perfect, assonance in AABB/ABAB/ABBA shapes, mixed perfect+assonance, and the help
  text's own read/cheap example.
- Got right: Two-pass lettering itself works: assonance pairs come out lowercase and the
  UI adds a caveat that lowercase pairs stay open; perfect AABB gets the correct settled
  note and no caveat.
- Where/why it failed: 3 of 4 assonance stanzas show a stable or settled note beside the
  stays-open caveat (aabb gets four stopping points, very stable). Mixed perfect plus
  assonance letters as AAaa, so the fold reads AAAA, relentlessly settled, merging two
  unrelated groups. The help text calls read/cheap assonance; rhymeType says family.
- Fix: Look the note up only on the uppercase (resolved) letters, treating lowercase as
  X for the shape, or give assonance groups letters that never collide with resolved
  ones; and either change the help example or the coda families so they agree.
- Why this fix: The shape table describes how resolved rhymes stop the ear; feeding it
  folded open pairs reintroduces exactly the mush the two-pass kernel exists to remove,
  and a case fold that merges A with a is a second, silent collapse on top.
- Rule of thumb: When a later stage consumes a two-pass result, check it keeps the
  distinction the second pass encodes; a toUpperCase or normalise step can quietly erase it.
- Provenance (verified/assumed): verified first-hand: ran the real suno-builder.html
  through node with the sandbox below; line numbers are from the reference copy in
  ideas/reference/suno-builder as of 2026-10-15.
- Composed: ideas:SONGWRITING/rhyme-tooling/two-pass-letter-assignment-keeps-schemes-legible, ideas:SONGWRITING/rhyme/rhyme-scheme-shape-sets-a-songs-emotional-motion, suno-builder/E9
- Picked-by: new-half
- Sandbox: sandboxes/2026-10-15__suno-scheme-note-case-folds-open-letters.py
- Prediction: Written after reading line 1274, before running: every assonance stanza
  whose folded scheme is in SCHEME_NOTES gets a stable or settled note (expected 4 of 4).
- Observed: RESULT: PASS 3 of 4 assonance-bearing stanzas get a stable/settled note beside
  the stays-open caveat (abba escapes only because its note is already open); mixed
  stanza AAaa folds to AAAA; read/cheap typed family, not assonance.
- Scenarios: 1) perfect AABB; 2) assonance aabb; 3) assonance abab; 4) assonance abba;
  5) mixed perfect+assonance; 6) the help text's read/cheap example (built to break the
  doc's claim).
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__suno-builder.md#E12 · incompatible · sandboxes/2026-10-15__builder-letters-feed-two-metric-closure-rule.py · observed RESULT: FAIL A scheme 1/8 B scheme 4/8 B verdict 3/4 (set A first draft with blue/through; set B spelling-matched where XXAA came back AABB). · https://claude.ai/code/session_01MwzyRZN1HRxgk5hnQqG5R4

## E9 — stray assonance turns an open xxaa stanza into a stable aabb readout
- Date: 2026-10-15
- Project: Pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][testing]
- What: Ran the two songwriting kernels together with their companion: the two-pass letter assigner
  (resolved rhymes claim letters before assonance), the rhyme-scheme-shape kernel (AABB stable, ABAB
  flowing, XXAA open then resolved, ABBA wistful), and suno-builder E7 (find the repeating section by
  role, not by the word Chorus), as one emotional-motion readout per section.
- Why built: Each piece was verified alone; a tool that reports a section's emotional motion needs all three at
  once, and the question was what the reader is told when one of them is missing.
- Design: Deterministic toy phonetics: words as vowel, coda class and coda; perfect, family and assonance
  rhymes. Eight stanzas with intended shapes, three of them XXAA with a stray assonance pair in the
  open couplet; one-pass and two-pass labelling mapped to the shape table. A seven-section song whose
  repeating section is labelled Hook and whose single unrepeated section is labelled Chorus, read by a
  label-keyed and a content-keyed repeat finder.
- Got right: The two-pass labeller gave the intended shape on all 8 stanzas; one-pass mislabelled all 3 stanzas
  with stray assonance. The content-keyed finder picked the Hook (3 repeats); the label-keyed one
  picked the lone Chorus.
- Where/why it failed: Nothing in my prediction failed, but the failure mode is sharper than 'mush': one pass turned each
  open-then-resolved XXAA stanza into AABB, the shape the kernel calls most stable, so the readout
  tells the writer the exact opposite of the motion they wrote. The fixture is hand-built, so the 3 of
  8 rate is mine, not a corpus rate.
- Fix: Read emotional motion only from the uppercase (resolved) letters of a two-pass labeller, and attach
  it to sections found by repeated content; never map a one-pass scheme or a section label straight to
  a mood.
- Why this fix: The shape table is only as good as the letters fed to it, and its most common open shape (XXAA) is
  exactly the one stray assonance converts into its most closed shape; section labels vary by genre
  (Hook, Refrain), so content is the only stable key.
- Rule of thumb: Feed the rhyme-shape table only two-pass resolved letters on sections found by repetition: one pass
  turned all 3 open XXAA stanzas with stray assonance into 'stable' AABB, the opposite reading, and a
  label-keyed finder took a lone 'Chorus' over a 3x Hook.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry on a hand-built fixture; the real suno-builder code
  was not run.
- Composed: ideas:SONGWRITING/two-pass-letter-assignment-keeps-schemes-legible, ideas:SONGWRITING/rhyme-scheme-shape-sets-a-songs-emotional-motion, pappydapimp69__suno-builder/E7
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__stray-assonance-turns-an-open-xxaa-stanza-into-a-stable-aabb-readout.py
- Prediction: one-pass mislabels the shape of every stanza with stray assonance (3 of 8), two-pass 0 of 8; a
  label-keyed finder misses the Hook and takes the lone Chorus; a content-keyed finder gets both
  right.
- Observed: RESULT: PASS 4/4; shape mislabels one-pass 3/8, two-pass 0/8; label-keyed finder picks the lone
  'Chorus', content-keyed finds {'Hook'}
- Scenarios: 1) five clean stanzas of four shapes; 2) three XXAA stanzas with stray assonance (built to BREAK the
  one-pass readout); 3) a Hook-led song with a lone Chorus label (built to BREAK the label-keyed
  finder)
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 4 pass 1 (kernel new half), 2026-10-15
- Cited-by: 2026-10-15 · projects/pappydapimp69__suno-builder.md#E10 · compatible · sandboxes/2026-10-15__suno-scheme-note-case-folds-open-letters.py · observed RESULT: PASS 3 of 4 assonance-bearing stanzas get a stable/settled note beside the stays-open caveat (abba escapes only because its note is already open); mixed stanza AAaa folds to AAAA; read/cheap typed family, not assonance. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E18 · compatible · sandboxes/2026-10-15__split-rushed-line-exposes-midline-word-to-two-pass-lettering.py · observed RESULT: FAIL split at midpoint: words/line 11.2->5.6; two-pass kept end pattern 5/6, single-pass kept 5/6; exposed mid-line words lettered in 3/6 natural stanzas (0 uppercase); internal-rhyme break stanza: 1 exposed word(s) promoted to UPP… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts training loop 1 pass 1
- Cited-by: 2026-10-19 · projects/local__two-pass-rhyme-letters-never-merge-perfect-groups-but-hide-assonance-to-a-resolved-group-exhaustive-4-line-stanzas.md#E1 · compatible · sandboxes/2026-10-19__two-pass-rhyme-letters-never-merge-perfect-groups-but-hide-assonance-to-a-resolved-group-exhaustive-4-line-stanzas.py · observed RESULT: PASS 1296 stanzas: one-pass merges non-perfect lines in 834 (64.4%); two-pass uppercase groups = perfect groups in 1296/1296; two-pass hides assonance to a resolved group in 312 (24.1%) · scheduled brain train auto, loop 2 pass 1; session_01W1FCx5tpnHusaTASoCMosY

## E8 — suno builder hyphenate splits silent e and skips vowel hiatus
- Date: 2026-09-30
- Project: pappydapimp69/suno-builder
- Tags: [songwriting][suno-prompting][testing][tooling]
- What: The real suno-builder hyphenate() gives a part count different from the true syllable count on 17 of 40 common lyric words. It splits a silent final e into its own part (de-si-re, be-lie-ve, cho-co-la-te), and it never splits two adjacent vowels that belong to separate syllables, so quiet, poem, lion, crying, flying, being, science and react come back unhyphenated and idea, radio, video, piano, violin get one part too few.
- Why built: The hyphenate-to-slow kernel says a hyphen forces the syllable timing Suno sings, so the builder's one-click hyphenation is effectively writing timing instructions; this probe checks whether those instructions match the word.
- Design: Headless run of hyphenate() and syllablesInWord() from suno-builder.html in a Node VM, on 40 hand-labelled words, comparing the number of hyphen parts to the true syllable count, plus the meter before and after hyphenating a line.
- Got right: 23 of 40 words split into the right number of parts, including the kernel's own examples to-night and beau-ti-ful, and on 38 of 40 words hyphenating leaves the meter's count unchanged.
- Where/why it failed: The splitter works on vowel groups, so a silent e becomes a vowel group and a vowel pair in separate syllables stays one group. The two words whose count changed (desire and believe) moved away from the truth, from 2 to 3. A line of every, quiet, radio, poem, violin counted 11 before and after hyphenating, so the fix offered for a crowded line does not change what the meter sees.
- Fix: Drop a silent final e before splitting, as rhymeKey() already does, split vowel pairs that are known to be separate syllables (i-a, i-o, e-o, u-i, o-e and a small exception list), and test hyphenate against a labelled word list rather than two examples.
- Why this fix: If a hyphen is treated as a timing instruction, a wrong split tells Suno to sing a syllable that is not there, which is worse than no hyphen; the silent-e rule already exists elsewhere in the same file.
- Rule of thumb: A hyphenator whose output is read as sung timing must be judged by part count against true syllables; a vowel-group splitter invents syllables at silent e and skips them at vowel pairs.
- Provenance (verified/assumed): Verified first-hand by running the real hyphenate() and syllablesInWord() headlessly (sb/suno/p2_hyphen.js): 17 of 40 mismatched, 2 count changes both away from truth. That Suno actually sings a hyphen as a syllable is the kernel's claim and was not tested.
- Composed: ideas:SONGWRITING/suno-prompting/hyphenate-words-to-slow-a-rushed-vocal-line, pappydapimp69__suno-builder/E5
- Link: scheduled training session, Suno probe 2
- Cited-by: 2026-09-30 · projects/local__sandbox-reduce-gonna-only-before-a-verb.md#E1 · incompatible · sandboxes/2026-09-30__reduce-gonna-only-before-a-verb.py · observed RESULT: FAIL overcount equals reductions on 4/8 reducing lines (only going-to loses a syllable); paper-only warnings 0; blind regex wrong 2/10, verb-only wrong 0/10 · https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Cited-by: 2026-09-30 · projects/local__suno.md#E12 · compatible · sandboxes/2026-09-30__lyric-syllable-counter-rules-vs-vowel-groups.py · observed RESULT: FAIL 3/4; TEST error baseline 44.7% rules 13.8% (n 94); DEV baseline 44.2% rules 8.7% (n 104). Run 1 before the early-return fix: rules TEST 14.9%, DEV 17.3%, 2/4. · session 2026-09-30 brain train loop 3 (lyrics tooling)
- Cited-by: 2026-10-15 · projects/pappydapimp69__suno-builder.md#E11 · compatible · sandboxes/2026-10-15__suno-hyphen-fix-never-lowers-the-count.py · observed RESULT: FAIL letters changed in 0/4 stanzas; hyphenating raised the counted syllables for 6/36 2+ syllable words (17%), lowered 0. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-20 · projects/pappydapimp69__brainwork.md#E568 · compatible · sandboxes/2026-10-20__real-suno-builder-hyphenated-end-words-letters-and-syllables.py · observed RESULT: PASS real suno-builder rhyme letters unchanged by hyphenating end words in 38416/38416 stanzas (rhymeKey strips hyphens) while syllable counts changed on 7.1% of lines · scheduled brain train auto session; session_018vkktVQxraRdjDDGahsw1j

## E7 — suno builder structure check keys on the word chorus not the repeating section
- Date: 2026-09-30
- Project: pappydapimp69/suno-builder
- Tags: [songwriting][structure][testing][tooling]
- What: The real suno-builder's structure checks, run headlessly on its own TEMPLATES list, flag two of its own built-in templates and miss a real structural gap. AABA (32-bar / crooner) and Hook-first (hip-hop) both get the notice that the bridge is not followed by a chorus. Hook-first with its bridge removed has four Hook sections and gets no missing-bridge warning, while Standard pop with its bridge removed does.
- Why built: To compose the pop-structure kernel (the bridge breaks the verse/chorus pattern once, right before the last chorus) with the section-tag vocabulary the builder offers, and see whether the check generalises beyond the one form it was written for.
- Design: Loaded the script from suno-builder.html into a Node VM with the same stubs its test-engine.js uses, filled every template with placeholder lyrics, and ran songChecks(). Then removed the Bridge from Hook-first and from Standard pop and ran it again.
- Got right: The four verse/chorus templates (Standard pop, Verse-chorus lean, Post-chorus pop, Ballad) pass clean, and Standard pop minus its bridge correctly warns about three choruses with no bridge.
- Where/why it failed: Both checks test the literal tag name "Chorus". A hip-hop form whose repeating section is tagged Hook is invisible to them in both directions, and AABA is a different form in which the bridge is meant to return to the A section, not a chorus, so the builder's own templates trip a warning the form never asks to satisfy.
- Fix: Define the repeating section per template (Chorus, Hook or Refrain, or the returning A in AABA) and run the bridge checks against that role instead of the word Chorus; skip the post-bridge-chorus check for forms that do not have one.
- Why this fix: The kernel is about the role of the section (the one that repeats and resolves), and the builder already stores the forms, so the role can come from the template rather than from a spelling.
- Rule of thumb: Run a structure checker on the tool's own built-in templates first; a rule written for verse/chorus pop that keys on the word Chorus misfires on AABA and goes blind on hook-first forms.
- Provenance (verified/assumed): Verified first-hand by running the real songChecks() from suno-builder.html headlessly (sb/suno/p1_templates.js): 2 of 7 templates flagged, Hook-first minus bridge with 4 Hooks gives no warning, Standard pop minus bridge warns.
- Composed: ideas:SONGWRITING/structure/standard-pop-structure-and-the-bridges-real-job, ideas:SONGWRITING/suno-prompting/bracket-section-tags-are-reverse-engineered-not-official, pappydapimp69__suno-builder/E3
- Link: scheduled training session, Suno probe 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__suno-builder.md#E9 · compatible · sandboxes/2026-10-15__stray-assonance-turns-an-open-xxaa-stanza-into-a-stable-aabb-readout.py · observed RESULT: PASS 4/4; shape mislabels one-pass 3/8, two-pass 0/8; label-keyed finder picks the lone 'Chorus', content-keyed finds {'Hook'} · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto 5-loop run, loop 4 pass 1 (kernel new half), 2026-10-15

## E6 — one null for four different failures
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [tooling][ux][state][testing]
- What: `readShareCode` returns `null` for every kind of bad input — a truncated code, a single flipped character, an empty string and outright garbage all produce the same `null`, with nothing thrown and no distinction between them. A share link that was clipped by a chat client is indistinguishable from a link that was never a share code.
- Why built: Share codes are base64 over a JSON state blob, so a parse failure is genuinely possible and returning `null` rather than throwing keeps the paste handler simple.
- Design: The reader decodes, parses and sanitises, and any failure along that path collapses to one falsy return. The caller has a single branch: a state, or nothing.
- Got right: Failing closed. A corrupted code never produces a half-populated project, and `sanitize` clamps every field it does accept, so nothing malformed reaches the editor.
- Where/why it failed: One return value for four different failures means the writer cannot be told what went wrong, and the most likely case in practice is the recoverable one — a link truncated in transit, where the right message is "this code looks cut off, ask for it again" rather than silence. Losing a song's whole state to a paste that fails without explanation is the kind of thing a writer reads as the tool eating their work.
- Fix: Distinguish the failure modes at the point they occur — not base64, base64 but not JSON, JSON but not a state object, right shape but an unknown `v` — and return which one, so the paste handler can say something specific. The version case matters most: `blankState` stamps `v: 1`, and a future code carrying `v: 2` will fail exactly like garbage.
- Why this fix: The information about which failure happened exists at the moment it happens and is thrown away one line later. Keeping it costs nothing and turns a dead end into a recoverable one. Version skew is the case that will appear on its own with no user error at all, and it is currently unreadable from the outside.
- Rule of thumb: A parser that collapses every failure into one falsy return cannot tell a recoverable error from a hopeless one, and the recoverable cases are usually the common ones. Keep the failure reason at the point you detect it — and give any versioned blob a path for "newer than I understand" that reads differently from "not mine".
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 by loading `suno-builder.html` headlessly in node and calling `readShareCode` with a valid code, a truncated code, a code with one character flipped, an empty string and non-base64 garbage — the valid one round-tripped a unicode title intact, and all four failures returned `null` with no exception raised. The version-skew case is read from `blankState`'s `v: 1` stamp and the sanitiser's handling; a `v: 2` code was reasoned about rather than constructed.
- Composed: N/A
- Link: session 2026-09-28; suno-builder.html readShareCode/makeShareCode/sanitize

## E5 — a stated threshold that tests a different one
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [tooling][testing][ux][songwriting]
- What: The syllable budget is presented as "Syllables / line <= N" with a numeric input, but the check is `lineSyllables(l) > S.sylBudget + 3`. With the budget set to 9 the first warning appears at 13. The slack is invisible from the interface, which states a limit the code does not enforce.
- Why built: A hard warning exactly at the stated number would fire constantly on ordinary lyric lines, so someone added tolerance to stop the panel crying wolf. That instinct is sound; the problem is where the tolerance lives.
- Design: The number the writer sets is the number the label shows, and the tolerance is a `+ 3` inside two separate call sites in the checks. Nothing in the panel reports the effective threshold, so the only way to learn it is to read the source.
- Got right: Having tolerance at all. A gate that fires on every line trains the writer to ignore it, which is worse than a gate set slightly loose.
- Where/why it failed: The tolerance compounds with a second bias pointing the same way. Measured against CMUdict over 4,000 words, `syllablesInWord` under-counts roughly 2.7 times as often as it over-counts (476 undercounts against 177 overcounts, 83.7% exact). So a line has to exceed the stated budget by three AS THE BUILDER COUNTS IT, and the builder tends to count low on exactly the vowel-cluster words that make a line crowded. Both errors are individually defensible and they stack, because nobody chose them together.
- Fix: Show the effective threshold rather than the stated one — if the check fires at 13, the label should say 13, or the input should set the threshold directly and the tolerance should be folded in where the user can see it. Separately, measure the counter against a pronunciation source and state its bias, so the tolerance can be chosen with the bias known instead of on top of it.
- Why this fix: Tolerance added to a stated limit is a silent second limit, and a tool that reports one number while testing another cannot be calibrated by the person using it. Once each bias is visible the pair can be traded off deliberately; while both are hidden they compound in whichever direction they happen to share.
- Rule of thumb: When a tool shows a threshold and tests a different one, the difference is a hidden setting nobody can tune. Look for a second bias pointing the same way before calling the slack safe — independently reasonable adjustments compound when they share a direction, and no single review catches it because each one looks fine on its own.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 by loading `suno-builder.html` headlessly in node and sweeping line lengths against `songChecks()` with `sylBudget` at 9 — no warning at 9 through 12, first warning at 13 — and by the 4,000-word CMUdict comparison giving 476 undercounts to 177 overcounts. Whether the resulting looseness actually costs a writer a rushed vocal is a claim about Suno's rendering that this sandbox leaves untested.
- Composed: suno-builder/E4
- Link: session 2026-09-28; suno-builder.html songChecks/sylBudget
- Cited-by: 2026-09-30 · projects/local__sandbox-syllable-slack-and-undercount-hide-crowded-lines-from-hyphenate-rule.md#E1 · compatible · no sandbox · scheduled training session, Suno-only pair batch
- Cited-by: 2026-09-30 · projects/pappydapimp69__suno-builder.md#E8 · compatible · no sandbox · scheduled training session, Suno probe 2

## E4 — the rhyme classifier judges spelling not sound
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][testing][tooling]
- What: The suno-builder's rhyme classifier keys on SPELLING, not sound. Measured against CMUdict on fifteen textbook rhyme pairs it recognises three: mud/blood, one/sun, eye/high, said/bed, rough/stuff, heart/part, through/blue, laugh/half, gone/dawn, word/bird and move/groove all come back as no rhyme at all. Across 1,500 phonetically perfect pairs its recall is 62.9%, and 496 of the 556 misses do not share their last two letters.
- Why built: `rhymeKey()` extracts the last `[aeiouy]+` group from the written word and normalises a few spellings (`ck`->`k`, `ph`->`f`). That is a reasonable thing to build with no pronunciation dictionary available in a single HTML file, and for spelling-matched rhymes it works.
- Design: `rhymeType(a,b)` compares those keys — same vowel and same coda is perfect, same vowel with manner-related codas is family, same vowel otherwise is assonance. The whole judgement rests on the spelled vowel group being a proxy for the spoken one.
- Got right: The classifier is not inert. Negative-controlled on five spelling-matched real rhymes against five unrelated pairs it returns perfect 5/5 and none 5/5, so it discriminates cleanly — it is just discriminating on the wrong feature. The manner-based family chart it implements also resolves tension T1's practical half: mud/truck comes back `family`, and so does read/cheap, confirming that no single chart gives the kernel's family/assonance split.
- Where/why it failed: English spelling is not a pronunciation guide, so every rhyme spelled differently is invisible and the error is concentrated exactly where songwriters live — one-syllable emotional vocabulary. It surfaces in the user-facing output: on truck / mud / blood / flood the scheme reads AABB, splitting four words that are one perfect rhyme in speech, because `u` and `oo` are different letter groups. The shipped 89-test suite passes and never catches this, because its rhyme fixtures are dove/love and night/light — pairs whose spelling and sound agree.
- Fix: Treat the classifier's output as a spelling-similarity score rather than a rhyme verdict, and say so in the UI. Where a pronunciation source can be reached, key on phonemes instead. At minimum, add cross-spelling pairs (mud/blood, one/sun, said/bed) to the test suite so the gap is visible to the next person rather than invisible behind a green run.
- Why this fix: A suite whose fixtures share the implementation's assumption cannot detect a defect in that assumption — every rhyme pair in it was chosen by someone thinking in spelling, so all of them agree with the code by construction. Adding a pair where sound and spelling disagree is the cheapest possible discriminator and it fails immediately.
- Rule of thumb: When a tool judges a property of SPEECH from WRITTEN input, its fixtures will be words whose spelling and sound agree, because those are the ones that come to mind — and the whole failure class lives in the words where they diverge. Pick fixtures where the two representations disagree, or the suite measures the encoding rather than the property.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 by loading `suno-builder.html` headlessly in node and comparing its `rhymeType` against a CMUdict classifier — 20% recall on fifteen common pairs, 62.9% over 1,500 phonetically perfect pairs, 81.7% verdict agreement across 894 sampled pairs, the AABB scheme read back from `analyseSection`, and a passing negative control. The 1,500-pair sample skews toward proper nouns, so the 62.9% figure describes the dictionary rather than song vocabulary; the 20% figure on hand-picked common words is the one that bears on lyrics.
- Composed: N/A
- Link: session 2026-09-28; ideas/reference/suno-builder/suno-builder.html rhymeKey/rhymeType; tension T1
- Cited-by: 2026-09-30 · projects/local__sandbox-two-pass-letters-cannot-rescue-a-spelling-rhyme-judge.md#E1 · compatible · no sandbox · scheduled training session, music group
- Cited-by: 2026-09-30 · projects/local__suno.md#E13 · compatible · sandboxes/2026-09-30__open-vowel-check-needs-digraph-rules-not-letters.py · observed RESULT: FAIL 3/4; naive 44.4%, digraph 5.6% (n 108); chorus line-ends open 48%, closed: eat. Run 2 held-out: digraph 10.0% (5/50: wind, saw, dark, yes, first), naive 46.0%. · session 2026-09-30 brain train loop 4 (singability)
- Cited-by: 2026-09-28 · projects/pappydapimp69__suno-builder.md#E5 · compatible · no sandbox · session 2026-09-28; suno-builder.html songChecks/sylBudget
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E22 · compatible · sandboxes/2026-10-15__elongation-marks-break-a-dictionary-rhyme-judge-that-spelling-survives.py · observed RESULT: PASS of 9 stanzas wrong: spelling 5, phonetic rejoin-only 4, collapse-to-1 6, first-candidate 2, context tie-break 1, flag-ambiguous 0 (flagged 2 stanzas, 4 tokens). Rejoin-only was 4 not my predicted 5 because in B2 finding no wor… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 2 pass 1

## E3 — reimplemented a tool that was already in the repo
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [process][verification][testing][tooling]
- What: I filed suno-builder#E1 about a rhyme-scheme labeller, having built my own labeller from the kernel's description and tested it against itself. The tool the kernel describes already existed in the repo, with a headless test harness, and I never ran it. Its real output on my own fixture is AABB, not the AAAA-vs-BAAA my entry claims.
- Why built: The kernel `[SONGWRITING / rhyme-tooling / two-pass-letter-assignment-keeps-schemes-legible]` reads as a description of a technique, so I implemented the technique. `ideas/reference/suno-builder/suno-builder.html` is the implementation it was written from, and `test-engine.js` runs its internals headlessly in node with no browser.
- Design: My version linked perfect rhymes in pass one and near-rhymes in pass two, and I compared merge-in against distinct-letter behaviour on truck / mud / blood / flood. The shipped builder does something else entirely: pass one assigns UPPERCASE for perfect, family AND identity together, pass two lowercase for assonance only — and its rhyme key is built from the SPELLED vowel group, not from pronunciation.
- Got right: The general rule in E1 survives — an implementation that cannot differ from what it replaces cannot be tested against it, and my fixtures did fail to discriminate twice before I looked at my own code. That part was verified and is still true.
- Where/why it failed: Everything E1 says about the kernel's mechanism and about the fixture is wrong. On truck / mud / blood / flood the real builder returns AABB: it groups truck with mud (family, both spelled with `u`) and blood with flood (perfect, both spelled `oo`), even though all four are one perfect rhyme in speech. So the near-rhyme does get folded into an uppercase group — the opposite of what E1 concluded — and the visible split is caused by spelling, a mechanism E1 never mentions because I never looked at the tool.
- Fix: Read suno-builder#E1 as a lesson about test discrimination only, and take its claims about the builder from this entry instead. Before implementing anything a kernel describes, search `ideas/reference/` for the artifact the kernel was mined from, and run its own harness first.
- Why this fix: A reimplementation tested against itself is a closed loop — every fixture I wrote encoded the same reading of the kernel that the implementation did, so agreement between them was guaranteed and carried no information. The shipped tool is the only thing that could have contradicted me, and it was one `node test-engine.js` away the entire time.
- Rule of thumb: When a kernel describes a technique, find out whether the thing it describes is already in the repo before you build your own. A reimplementation tested against your own reading of the kernel cannot disagree with you, so it verifies nothing — and filing the result as canon publishes your reading as though it were the tool's behaviour.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 — loaded `suno-builder.html` headlessly in node, called `analyseSection` on the exact fixture from E1, and read back `[[truck,A,family],[mud,A,family],[blood,B,perfect],[flood,B,perfect]]`; the shipped `test-engine.js` reports 89 passed, 0 failed, so the builder is working as written and the error is entirely mine.
- Composed: suno-builder/E1
- Link: session 2026-09-28; ideas/reference/suno-builder/{suno-builder.html,test-engine.js}; corrects suno-builder#E1
- Cited-by: 2026-09-30 · projects/local__sandbox-two-pass-letters-cannot-rescue-a-spelling-rhyme-judge.md#E1 · compatible · no sandbox · scheduled training session, music group
- Cited-by: 2026-09-30 · projects/pappydapimp69__suno-builder.md#E7 · compatible · no sandbox · scheduled training session, Suno probe 1
- Cited-by: 2026-10-08 · projects/local__sandbox-two-pass-lettering-needs-scope-and-phonetic-judge.md#E1 · compatible · sandboxes/2026-10-08__two-pass-lettering-needs-scope-and-phonetic-judge.py · observed RESULT: PASS two-pass fixes steal on 2 stanzas, ties on clean stanza; scope and spelling judge remain separate failure axes (single AAAA vs two ABAB; scope ABABACAC vs ABABCDCD; judge ABCC vs ABBB) · scheduled training session, kernel pass 1
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E260 · compatible · sandboxes/2026-10-14__two-pass-rhyme-letters-differ-from-one-pass-only-when-assonance-comes-first.py · observed RESULT: PASS XXAA one-pass (0, 0, 0, 0) two-pass (0, 0, 1, 1); agree 0.773, disagree 4704 of 20736; reversal changes one-pass 0 vs two-pass uppercase 0 (T4 prediction refuted) · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 2 pass 1
- Audited: 2026-10-15 · pass · The entry has no stored sandbox, so I re-ran its factual claim against the real tool: loaded suno-builder.html through the shipped test-engine.js harness (89 passed, 0 failed) and called analyseSection on truck/mud/blood/flood. It returned scheme AABB with truck and mud as family (vowel U2) and blood and flood as perfect (vowel U), exactly as the entry states, so the result is computed by the real code and not assumed. The Rule of thumb is a process rule (search the repo for the artifact before reimplementing); one real instance supports it, and the entry claims no more than that. · scheduled brain train session 2026-10-15, audit pass 3; session_0147KUptpmmgHdXXTSmtxr1C
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-suno-builder-e3-self-built-labeller-cannot-disagree.py · observed RESULT: PASS self-test 9/9 but reference disagrees on 3/9 fixtures · Rebuilt from the claim only, with my own 9 stanza fixtures (not the original's AAAA-vs-BAAA one). A same-reading labeller (last two letters) passed its own derived test 9/9, while a separately defined reference (final vowel group plus coda) disagreed on 3/9 stanzas (time/rhyme/fire/wire, bear/care/here/near, sing/ring/sung/hung). So a self-built check cannot disagree with itself. Differs from the original: different fixtures and a stand-in reference, not the real repo tool, so it supports the principle, not the specific AABB output. · brain train auto loop 1 pass 4, session_01R9q6q7UzomwgJUBasbhB7S
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E366 · compatible · sandboxes/2026-10-16__two-pass-rhyme-letters-vs-one-pass-own-fixture.py · observed RESULT: PASS two-pass differs from one-pass on 4 of 5 fixtures; near-rhyme beside a perfect trio: one-pass AAAA hides it, two-pass AAxA marks it unresolved; assonance-only stanza AABC vs aaxx · scheduled brain train auto loop 2 pass 1; session_01BUPKhqp6uFZkacj8e9KczX
- Cited-by: 2026-10-17 · projects/pappydapimp69__brainwork.md#E420 · compatible · sandboxes/2026-10-17__two-pass-labeller-vs-one-pass-intended-schemes.py · observed RESULT: PASS two-pass resolved scheme matches the design in 3752 of 3752 stanzas (lowercase marks 284 XXAA filler pairs that share a vowel); one-pass is wrong on 724 of 1552 XXAA stanzas and 0 of 558 stanzas with no stray assonance; assona… · session 2026-10-17 scheduled brain train, loop 2 pass 1; session_01KkkcHHGkp6Sm9GJK6fsa84
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E474 · compatible · sandboxes/2026-10-19__two-pass-rhyme-letters-resolved-first-vs-one-pass-and-spelled-key.py · observed RESULT: PASS one-pass stray 856/4096, two-pass 0/4096; every fixture matched the prediction on first run. · session_01XcwhzUYMjGM7jR9MWUvW46

## E2 — pronunciation zero picks a meaning
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][determinism][state]
- What: A rhyme classifier that reads a word's first pronunciation is picking a MEANING, silently. English heteronyms have one spelling and two pronunciations with different vowels, so the same pair of words classifies as a rhyme or not depending on which entry the lookup happens to return first.
- Why built: The suno-builder classifies line endings as perfect, family or assonance to label a rhyme scheme. The obvious implementation takes `CMUdict[word][0]` and compares vowels and trailing consonants.
- Design: CMUdict stores a list of pronunciations per word, ordered, with no marking of which sense each belongs to. `read` is `R EH1 D` and `R IY1 D`; only the second shares a vowel with `cheap` (`CH IY1 P`). Nothing in the data says which one a lyric meant.
- Got right: Comparing a first-pronunciation implementation against one that considers every pronunciation, rather than testing either alone. Both are internally consistent and neither looks wrong on inspection; the disagreement is the only signal.
- Where/why it failed: Over 400 multi-pronunciation words the two implementations disagreed on 124 pairs. CMUdict holds 8,447 words with more than one pronunciation, and 2,343 words (1.9% of 126,052) where the LAST vowel differs between pronunciations — which is exactly the set that changes a rhyme verdict. The failure is silent: both implementations return a clean boolean and a well-formed scheme.
- Fix: Consider every pronunciation and take the strongest classification any pairing yields, so `read/cheap` resolves against the pronunciation that can rhyme rather than the one the dictionary happened to list first. Where the word's sense actually matters to the lyric, that is a question for the writer, and the tool should say the ending is ambiguous rather than pick.
- Why this fix: A first-entry lookup is a hidden dependency on dictionary ordering — the same code gives a different answer if the data source is swapped or reordered, with no test failing. Taking the best over all pronunciations removes the ordering dependency; surfacing ambiguity removes the pretence that the tool knew which sense was meant.
- Rule of thumb: When a lookup returns a LIST and the code takes element zero, check whether the list holds alternatives that change the answer. For English pronunciation it holds two senses of a heteronym, and a rhyme checker that takes the first one is deciding what the word means without telling anyone. Compare against an all-alternatives implementation; if they ever disagree, element zero was never a safe default.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 by a deterministic sandbox over the full CMUdict — the counts quoted here (8,447 multi-pronunciation words, 2,343 with a differing last vowel out of 126,052, and 124 disagreeing pairs across 400 multi-pronunciation words) are that run's output, and the classifier underneath was negative-controlled on five known rhyming pairs against five unrelated pairs before any of these numbers were read.
- Composed: N/A
- Link: session 2026-09-28; sandbox l1_3.py loops 2-3; tension T1

## E1 — implemented the kernels name not its mechanism
- Date: 2026-09-28
- Project: pappydapimp69/suno-builder
- Tags: [songwriting][rhyme][testing][verification]
- What: Implementing the stored kernel "two-pass letter assignment keeps schemes legible — resolved rhymes claim letters before assonance does", I wrote a two-pass rhyme-scheme labeller and tested it against one pass. Both returned the identical scheme on every case I tried, including one built specifically to separate them. The kernel names a mechanism; what I had built was a rename.
- Why built: The suno-builder assigns A/B/C letters to line endings so a writer can see the scheme. Perfect rhymes and near-rhymes compete for the same letters, and the kernel says the resolved ones should claim them first.
- Design: Pass one linked only perfect rhymes; pass two linked family and assonance. A shared `claim()` helper merged either line into whichever letter already existed. Four lines ending truck / mud / blood / flood, where mud-blood-flood are mutually perfect and truck is family with all three, should have been the discriminating case.
- Got right: Testing one pass against two rather than only asserting the two-pass output looked sensible. That comparison is what exposed the problem; an assertion on the two-pass result alone would have passed and told me nothing.
- Where/why it failed: Both orders returned AAAA. My pass two still merged the family word into the existing perfect group, so the only thing the passes changed was the order in which identical merges happened. A test over an implementation that cannot differ cannot fail, and I ran it twice on two different fixtures before looking at the implementation rather than the fixture. The kernel's actual mechanism is that near-rhymes get a DISTINCT letter, not an earlier one — so the resolved trio holds A and the family word is visibly separate.
- Fix: Make pass two assign a new letter instead of merging. The same four lines then return AAAA under merge-in and BAAA under the kernel's rule, so the two implementations are finally distinguishable and the scheme shows the writer that truck is not the same rhyme as mud.
- Why this fix: The letters exist to show a writer which endings resolve together. Folding a family word into the perfect group destroys exactly the distinction the kernel was written to preserve, and it does so silently, because the output is still a well-formed scheme string.
- Rule of thumb: When you implement a stored kernel, test that your implementation can DIFFER from the thing it supposedly improves on. If the before and after produce identical output on a case built to separate them, suspect that you implemented the kernel's name rather than its mechanism — and look at the implementation before blaming the fixture.
- Provenance (verified/assumed): VERIFIED first-hand on 2026-09-28 by a deterministic sandbox over CMUdict — the merge-in and distinct-letter implementations were both run on the truck/mud/blood/flood fixture, returning AAAA and BAAA respectively, and the classifier underneath was negative-controlled on five known rhyming pairs (all perfect) against five deliberately unrelated pairs (all none). Whether a reader finds BAAA more legible than AAAA is a claim about people that this sandbox leaves open.
- Composed: N/A
- Link: session 2026-09-28; sandbox final.py loop 5; ideas [SONGWRITING / rhyme-tooling / two-pass-letter-assignment-keeps-schemes-legible]
- Cited-by: 2026-09-28 · projects/pappydapimp69__suno-builder.md#E3 · compatible · no sandbox · session 2026-09-28; ideas/reference/suno-builder/{suno-builder.html,test-engine.js}; corrects suno-builder#E1
- Cited-by: 2026-10-08 · projects/local__sandbox-two-pass-lettering-needs-scope-and-phonetic-judge.md#E1 · compatible · sandboxes/2026-10-08__two-pass-lettering-needs-scope-and-phonetic-judge.py · observed RESULT: PASS two-pass fixes steal on 2 stanzas, ties on clean stanza; scope and spelling judge remain separate failure axes (single AAAA vs two ABAB; scope ABABACAC vs ABABCDCD; judge ABCC vs ABBB) · scheduled training session, kernel pass 1
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E260 · compatible · sandboxes/2026-10-14__two-pass-rhyme-letters-differ-from-one-pass-only-when-assonance-comes-first.py · observed RESULT: PASS XXAA one-pass (0, 0, 0, 0) two-pass (0, 0, 1, 1); agree 0.773, disagree 4704 of 20736; reversal changes one-pass 0 vs two-pass uppercase 0 (T4 prediction refuted) · session_017SJAeaijx8mHKPVUZV6hJB brain train auto loop 2 pass 1
- Cited-by: 2026-10-15 · projects/pappydapimp69__zanegpt.md#E22 · compatible · sandboxes/2026-10-15__hyphenated-rhyme-words-need-the-joined-word.py · observed RESULT: PASS 13 rhyme words hyphenated; rejoined 4/4, raw token 0/4, first fragment 0/4. · brain train (creative arts, loop 2, new half), session 2026-10-15; session_011p52L2CkFXcsYRwjDu6tG9
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E366 · compatible · sandboxes/2026-10-16__two-pass-rhyme-letters-vs-one-pass-own-fixture.py · observed RESULT: PASS two-pass differs from one-pass on 4 of 5 fixtures; near-rhyme beside a perfect trio: one-pass AAAA hides it, two-pass AAxA marks it unresolved; assonance-only stanza AABC vs aaxx · scheduled brain train auto loop 2 pass 1; session_01BUPKhqp6uFZkacj8e9KczX
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E474 · compatible · sandboxes/2026-10-19__two-pass-rhyme-letters-resolved-first-vs-one-pass-and-spelled-key.py · observed RESULT: PASS one-pass stray 856/4096, two-pass 0/4096; every fixture matched the prediction on first run. · session_01XcwhzUYMjGM7jR9MWUvW46
