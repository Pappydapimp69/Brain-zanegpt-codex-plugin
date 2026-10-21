# local/sandbox-title-position-report-all-hits — lessons

Project: local/sandbox-title-position-report-all-hits. Newest first.

---

## E1 — title position report all hits
- Date: 2026-09-30
- Project: local/sandbox-title-position-report-all-hits
- Tags: [songwriting][lyrics][testing]
- What: A title-placement check built from the power-positions kernel needs the content-word, both-hyphen-views title matcher and must report every line the title hits; exact substring found the right first/last placement in 4 of 8 choruses and a first-hit-only report in 2 of 8.
- Why built: Compose the title-in-power-positions kernel with the content-word subsequence title matcher and the split-and-join hyphen views lesson, to see whether placement can be reported reliably.
- Design: Eight 4-line choruses hand-labelled with the positions (first, last) that carry the title drop, including a stutter hook, timing hyphens, a tense shift, a plural and titles that also appear mid-chorus. Compared exact substring, the content-word matcher with both hyphen views, and a report of only the first matching line.
- Got right: The content-word matcher with both hyphen views placed the title correctly in 7 of 8 choruses and caught the stutter (bye-bye-bye) and timing (to-night) drops that substring missed.
- Where/why it failed: It missed held for Hold The Line, the irregular past the matcher lesson already names, so my 8 of 8 prediction was wrong; a first-hit-only report was right on 2 of 8 because a chorus framed by the title at first and last line cannot be described by one position.
- Fix: Report all title positions per chorus and judge first and last separately; add a small irregular-verb table (held, ran, left, gone) to the matcher's stemming.
- Why this fix: Framing the chorus with the title at both ends is the kernel's strongest case, and only a report of every hit can show it; the remaining miss is a known stemming gap with a direct fix.
- Rule of thumb: Report every line a title hits and judge first and last separately: a first-hit-only placement report was right on 2 of 8 choruses and exact substring on 4 of 8, while content-word matching with both hyphen views got 7 of 8.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; counts are copied from its output. The listener effect of title placement is the kernel's claim and is outside this sandbox.
- Composed: ideas:SONGWRITING/title/title-sits-in-the-choruss-power-positions, sandbox-lyrics-structure/E3, sandbox-title-matcher-stutter-split-vs-timing-hyphen-join/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__title-position-report-all-hits.py
- Prediction: substring finds the labelled placement in at most 4/8; content-word with both views 8/8; first-hit-only mislabels at least 2.
- Observed: RESULT: FAIL substring 4/8, content-word both views 7/8, first-hit-only 2/8, middle hits in 2/8
- Scenarios: 1) exact title at first and last line; 2) stutter and timing-hyphen drops; 3) tense shift (held) built to break the matcher; 4) one-word titles repeated mid-chorus.
- Link: https://claude.ai/code/session_01FPKwCG4xnKWiiLWPC1nvdo
- Cited-by: 2026-09-30 · projects/local__suno.md#E9 · incompatible · sandboxes/2026-09-30__trending-lyrics-test-title-position-and-contrast.py · observed RESULT: FAIL 2/4; title first/last 0.89 vs chance 0.78 (n 18; deduped 0.86 vs 0.72, n 14); chorus shorter 0.62 (n 45; deduped 0.59); text-vs-tag agree 0.93 (n 14), text-repeat empty in 14 · session 2026-09-30 brain train, related pass on songwriting kernels
- Audited: 2026-10-08 · fail · Read the entry and reran sandboxes/2026-09-30__title-position-report-all-hits.py (same 4/8, 7/8, 2/8 output). The substring and content-word figures are computed from the matchers against hand-labelled choruses, so those hold for the 8 fixtures. The first-hit-only figure of 2/8 is built in: the reporter returns one position and is scored by whether that single position equals the whole labelled set, so it can never be right on the six choruses labelled first plus last; only Stay and Home (single-position labels) can score, giving 2 by construction whatever the matcher does. The Rule of thumb states this number as a finding about first-hit reporting, which the model does not test; a fair score would credit the first hit as correct for the first position and show what it misses. The content-word miss on Hold The Line is real and honestly reported. The claim about listener effect is out of scope, as the entry says. · scheduled training session, audit pass 3
