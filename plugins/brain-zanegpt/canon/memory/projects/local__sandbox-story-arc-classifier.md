# local/sandbox-story-arc-classifier — lessons

Project: local/sandbox-story-arc-classifier. Newest first.

---

## E1 — story arc classifier tie and lexicon misses
- Date: 2026-07-18
- Project: local/sandbox-story-arc-classifier
- Tags: [algorithm][testing][narrative]
- What: Seeding the "story writing" domain (`brain train new-domain`, 0 prior
  coverage) by testing a real, externally-verified claim — Reagan et al. 2016's
  six emotional-arc shapes (Rags-to-Riches, Tragedy, Man-in-a-Hole, Icarus,
  Cinderella, Oedipus) — with a deterministic lexicon-valence-scoring +
  reversal-counting classifier against 6 hand-constructed stories, one per
  shape. Result: 3/6 correct (50%), reproduced identically across two separate
  process invocations. Two distinct, real mechanisms explain all three misses.
- Why built: `brain train new-domain`'s rule requires sandbox verification, and
  this session's request specifically asked for "external research" — grounded
  the sandbox in a real, WebSearch-confirmed published finding (not a
  self-authored taxonomy, unlike the earlier zen-koan seed).
- Design: A fixed 16-word positive/16-word negative lexicon scores each
  sentence (word count in POS minus word count in NEG, exact string match, no
  stemming). The per-sentence score sequence is turned into direction signs
  (+/-) from consecutive diffs; consecutive same-sign runs collapse into a
  reversal-count and pattern string (e.g. "+-+"). Classification: 0 reversals
  → rise/fall by net sign; 1 reversal → man-in-a-hole ("-+") or icarus ("+-");
  2 reversals → cinderella ("+-+") or oedipus ("-+-").
- Got right: rags-to-riches, cinderella, and oedipus classified correctly —
  the algorithm's core idea (count genuine reversals, classify by pattern) is
  sound when the input signal is clean, which validates the shape-taxonomy
  approach is buildable, not just theoretically plausible.
- Where/why it failed: Two independent, real bugs, not "bad test data":
  (1) TIE-DEFAULT BUG — the reversal-counter's "carry the previous direction
  when a diff is exactly 0" rule initializes `last = None`, so the very FIRST
  diff, if it happens to be 0 (a genuine tie between the first two sentences'
  scores), silently defaults to "+" purely as an artifact of that
  initialization — there is no real "previous direction" to carry yet. The
  "tragedy" story opens with two sentences that both scored +3 by coincidence
  ("rich, happy, free" vs. "laughed, celebrated, success"), so the phantom
  leading "+" combined with the story's genuine subsequent monotonic fall
  produced a fabricated single reversal, misclassifying a simple fall as
  icarus. (2) LEXICON MORPHOLOGY GAP — the lexicon only matches exact base
  forms ("happy", "safe", "poor"); two stories' resolution sentences used
  inflected forms ("happier", "safer", "poorer") that scored 0 instead of
  positive/negative, creating a small artificial wiggle right at the story's
  climax that the classifier read as a second, unintended reversal (both the
  man-in-a-hole and icarus misses trace to this).
- Fix: Not applied (seed/demonstration sandbox, not shipping code) — flagging
  both mechanisms rather than patching this one classifier.
- Why this fix: N/A — no fix applied; see Fix and Rule of thumb.
- Rule of thumb: Building any shape/direction classifier from a noisy
  per-step signal (sentence sentiment, frame-to-frame delta, sensor readings)
  recurring failure modes, independent of domain: (1) an uninitialized
  "previous direction" state at a sequence's start will silently coerce a
  genuine TIE into a fabricated direction unless ties are explicitly
  represented as "undefined, no direction yet" rather than aliased to
  whichever sign the code happens to default to; (2) any fixed-vocabulary
  exact-match scoring step (a sentiment lexicon, a keyword classifier, a
  rule-based tagger) undercounts inflected/derived forms of its own
  vocabulary, and that undercounting is NOT uniformly distributed — it lands
  hardest exactly on the sentences carrying a resolution or climax, where
  intensified/comparative language ("happier," "far worse") is common. Both
  compound: raw, un-smoothed, exact-match-scored deltas are fragile enough
  that the real published methodology (Reagan et al.) uses matrix
  decomposition / Fourier-mode fitting over the WHOLE curve specifically to
  avoid trusting any single local delta — this sandbox's 50% miss rate is a
  small, concrete demonstration of why that heavier machinery is earned, not
  decorative.
- Provenance (verified/assumed): VERIFIED first-hand — built
  `arc_classifier.py`, ran it twice as separate process invocations,
  byte-identical output both times (3/6, same three misses). The six-shape
  taxonomy and its attribution to Reagan, Mitchell, Kiley et al. 2016 (*EPJ
  Data Science*, vol. 5, p. 31) is externally verified via WebSearch —
  multiple independent sources (arXiv, Springer, MIT Technology Review) agree
  on the same six shape names, the ~1,700-novel Project Gutenberg corpus, and
  the sentiment-window methodology. Direct WebFetch of the paper's own pages
  (arxiv.org, link.springer.com, pdodds.w3.uvm.edu, technologyreview.com) all
  returned HTTP 403 (proxy-blocked in this environment) — so the specific
  up/down SEQUENCE assigned to each shape name in this sandbox rests on my
  own standard/commonly-reported understanding of the paper's shapes rather
  than a direct read of the primary source. Flagging that distinction
  rather than overstating verification depth: the CLASSIFIER MECHANISM finding
  (tie-default + lexicon-morphology bugs) is fully verified by the sandbox
  run; the exact shape-to-sequence mapping rests on secondary-source
  agreement alone, short of primary-source confirmation.
- Composed: N/A
- Link: session (Creativity repo, linked full); sandbox
  `/tmp/.../scratchpad/arc_classifier.py`, run twice, byte-identical (3/6);
  WebSearch "Reagan emotional arcs of stories six basic shapes sentiment
  analysis 2016" (arxiv.org/abs/1606.07772,
  link.springer.com/article/10.1140/epjds/s13688-016-0093-1,
  technologyreview.com/2016/07/06/158961); direct WebFetch of all four
  primary/secondary source pages returned HTTP 403.
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E137 · compatible · sandboxes/2026-10-11__arc-classifier-tie-bug-hidden-by-spot-check-and-accuracy.py · observed RESULT: PASS clean=1.000 tie=0.917 lex=0.833 both=0.917 spot3_tie=1.00 fall_recall_tie=0.5 · scheduled brain train session; session_019JKZ53wDZk2PJ4F5v2qxmH
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E276 · compatible · sandboxes/2026-10-14__arc-classifier-tie-default-on-exhaustive-choice-paths-and-clamp-order.py · observed RESULT: PASS 112/729 disagree (15.4%), all with a zero first change; 111 fall-first plus the all-flat path (the negative-only part of the prediction missed); order changes arc in 15/28 sets with clamp and 15/28 without. · brain train auto scheduled run, loop 2 pass 2; session_013UbxUV5wii3FwAXCPW9kkg
