# pappydapimp69/ideas — lessons

Project: pappydapimp69/ideas. Newest first.

---

## E4 — steward batch validation blocks all
- Date: 2026-10-15
- Project: Pappydapimp69/ideas
- Tags: [brain][testing]
- What: The ideas steward promotes every passing proposal, then validates the merged
  repository once; any failure aborts the whole run, so 8 bad Linked lines kept 46
  kernels out of canon for about 30 hours across 30+ failed runs.
- Why built: Validating the merged result after promotion catches cross-file problems
  (a ref to a kernel that only exists in another incoming file) that a per-file check
  would miss.
- Design: steward.yml runs promotion, then scripts/validate.py over canon plus incoming;
  a non-zero exit fails the job and nothing is committed. Linked refs must resolve to
  exactly one kernel by full header path or a segment-boundary prefix.
- Got right: The validator was correct every time: each failure named the file, the
  kernel and the bad ref, so the fix took minutes once someone read the log.
- Where/why it failed: All-or-nothing commit plus no alert: one malformed proposal
  silently blocked every later sync, and brain train kept re-suggesting pairs that had
  already been composed because their kernels never reached canon. Bad refs were prose
  after "none", short refs stopping mid-segment, memory refs, and invented kernels.
- Fix: Corrected the 8 Linked lines (bare none, full header paths, dropped refs to
  nothing or to memory entries); validate.py passed locally and the next steward run
  promoted all 46. Structural fix still owed: validate per proposal and hold only the
  failing file, and surface a failed steward in brain sync output.
- Why this fix: The data fix unblocked canon immediately; isolating failures per file
  keeps one author's typo from freezing every other author's work, and an alert stops
  a silent multi-day stall from being found by accident.
- Rule of thumb: A batch pipeline whose final check aborts everything must hold the
  offending item instead, and must report its own failure; otherwise one bad input
  silently freezes all intake.
- Provenance (verified/assumed): verified first-hand: steward runs 226-231 failed with
  33 Linked-ref problems; after commit df31716 the steward-bot run promoted all 46 and
  ideas/incoming emptied; kernel count rose 1172 to 1218.
- Composed: N/A
- Link: https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx

## E3 — multi entry proposal silently drops extras
- Date: 2026-08-05
- Project: Pappydapimp69/ideas
- Tags: [process][tooling]
- What: A single `incoming/` proposal file carrying FOUR idea kernels promoted only the first one and then deleted the file, silently destroying the other three. Nothing in the pipeline reported a problem: `validate.py` passed, the steward printed `promoted 1 · held 0`, and CI went green.
- Why built: Four reusable kernels came out of one build session (the Suno song & style builder). They were filed as four `## [DOMAIN / ...]` blocks in one dated proposal file, on the reasonable-looking assumption that a proposal file is a batch.
- Design: `scripts/steward.py` runs per FILE, not per entry: `parse_proposal()` calls `parse_entries()` and returns `entries[0]` — its docstring says "A proposal file should contain exactly one entry" — and on success `promote()` ends with `os.remove(os.path.join(ROOT, "incoming", fname))`, deleting the whole file including the entries it never looked at. `ideas/README.md` does say "Fill in **one** `## [DOMAIN / sub / kw / kw]` header", so the one-per-file rule is documented; it is simply not enforced anywhere.
- Got right: the surviving kernel promoted correctly into the right domain block, and the append-only guard on `idea-repository.md` was never at risk — this destroys the SUBMISSION, not canon.
- Where/why it failed: the two gates disagree about the schema and neither one closes the gap. `validate.py`'s `check_incoming()` iterates `parse_entries(text)` and validates EVERY entry in a file, so a four-entry file is not merely accepted, it is affirmatively checked and passed. The steward then reads only entry 0 and unlinks the file. The discrepancy is invisible because the steward's own summary counts FILES (`promoted 1 · held 0`), so "1" looks like a complete success rather than "1 of 4". The loss is silent, immediate, and — since the file is deleted in the same commit — recoverable only from the git history of the branch that introduced it.
- Fix: re-filed the three lost kernels as three separate one-entry files (`2026-08-05__declared-emotional-target.md`, `2026-08-05__budget-meter-beats-a-length-rule.md`, `2026-08-05__exact-versus-word-boundary-matchers.md`) and confirmed with `python3 scripts/steward.py --dry-run` that all three promote. One kernel per file, always.
- Why this fix: it restores the lost content immediately without touching the steward, which is the conservative move for shared automation that other projects depend on. The deeper repair belongs to the steward itself and is proposed, not applied here: `parse_proposal()` should hold — not silently discard — any file where `len(parse_entries(text)) > 1`, since a hold is visible and reversible while `os.remove` is neither. Alternatively the steward could promote every entry in the file, which is what `validate.py`'s behaviour already implies; either resolution is fine, but the two gates must agree.
- Rule of thumb: when an automated promoter DELETES its input on success, any input it partially parses is silently destroyed — so verify the promoter and the validator agree on the unit of submission before batching anything into one file, and read the promoter's summary counts carefully (a count of FILES processed will report a complete success while discarding most of the content). Run the promoter's `--dry-run` against your own proposal before pushing; it takes seconds and it is the only thing that would have caught this.
- Provenance (verified/assumed): verified first-hand. Reproduced the exact failure by cloning the repo at the pre-steward merge commit and running `python3 scripts/steward.py`, which printed `promoted 1 · held 0` for the four-entry file; confirmed by reading `parse_proposal()` (returns `entries[0]`) and `promote()` (`os.remove`), and by grepping the post-steward `idea-repository.md` for the three missing kernels (0 hits, and the proposal file gone from `incoming/`). The claim that `validate.py` passes a multi-entry file is verified — it ran green on the same file before the merge.
- Composed: N/A
- Link: session 2026-08-05; ideas commits f1f22b6 (merge) → 8c44a3a (steward-bot promotion of 1 of 4).

## E2 — ideas domain tag casing made entries invisible
- Date: 2026-07-11
- Project: pappydapimp69/ideas
- Tags: [process][documentation][taxonomy]
- What: Two entries in `idea-repository.md` used `narrative-design` (lowercase)
  as their top-level DOMAIN tag — `[narrative-design / comedy / ...]` and
  `[narrative-design / AI-fiction / ...]`. The established domain, per
  `README.md`'s own `ESTABLISHED DOMAINS` list, is `NARRATIVE-DESIGN`
  (uppercase) — every other entry in the file's 78 entries consistently
  uses uppercase domain tags (`RPG`, `SYSTEM`, `DATA-TOY`, etc.). A
  case-sensitive scan for `NARRATIVE-DESIGN` found zero matches even
  though it's a listed, established domain — the only two entries that
  should live under it were effectively invisible to that domain.
- Why built: `narrative-design` is ALSO a valid lowercase SUB-tag elsewhere
  in the same file (`[RPG / narrative-design / legendary-transformation /
  survivorship-bias]` — domain=RPG, subtag=narrative-design, correctly
  lowercase per the file's own sub-tag convention). Whoever filed the two
  miscased entries was very plausibly pattern-matching the FAMILIAR string
  "narrative-design" from its correct, lowercase, sub-tag usage elsewhere,
  without registering that the SAME string needs different casing when it
  moves from sub-tag position to domain position.
- Design: The file's convention (domain uppercase, sub-tags lowercase) is
  established by consistent usage across 78 entries and stated implicitly
  by the `ESTABLISHED DOMAINS` list — but it's enforced by NOTHING
  mechanical. `validate.py`-style schema checking exists in the separate
  `memory` repo for ITS OWN incoming proposals; `idea-repository.md` has
  no equivalent linter, so a casing slip has no way to get caught before
  landing.
- Got right: The two entries' CONTENT was fine — well-formed 2-4 sentence
  self-contained fragments, correctly passing the artifact/portability
  tests the filing spec describes. The failure was purely in the tag,
  not the substance.
- Where/why it failed: A string that's correct in one grammatical position
  (sub-tag, lowercase) and incorrect in another (domain, uppercase) is
  exactly the kind of thing a person (or a model) skims past — it reads as
  "the right word" at a glance, and nothing about eyeballing a bracket
  line surfaces that the SAME word needs different capitalization
  depending on which slot it's in. The file's own rule — "New entries are
  slotted into the matching DOMAIN block, not blindly appended at the end"
  — was also violated as a direct consequence: since no NARRATIVE-DESIGN
  block existed under the correct casing, the two entries had nowhere
  matching to slot into, and landed appended after the DATA-TOY block
  instead, which is itself a symptom of the same root cause, not a
  separate mistake.
- Fix: Corrected both headings to `NARRATIVE-DESIGN` (uppercase), matching
  every other domain tag in the file and the established list.
- Why this fix: Restores the mechanical property the whole system depends
  on for its two operating modes: MINING MODE says "match domain and
  keywords first" — a case-sensitive or convention-aware search for
  `NARRATIVE-DESIGN` now actually finds these two entries; FILING MODE says
  "match an existing domain before coining a new one" — a future narrative-
  design fragment now has a real, discoverable block to slot into instead
  of risking a THIRD miscased variant.
- Rule of thumb: When the same string is legitimately used in two different
  grammatical roles within one taxonomy (a domain vs. a sub-tag, a top-
  level key vs. a nested value), expect exactly this class of slip: correct
  usage in the familiar role gets pattern-matched into the other role with
  the wrong casing/formatting for that role. This is invisible to a normal
  read-through (the word itself is right) and needs either (a) a mechanical
  lint pass over just the structural markers (grep the domain position
  specifically, not the whole line) or (b) picking taxonomy conventions
  that DON'T reuse the same string in two roles with different formatting
  rules, when practical. Periodically grep a free-text taxonomy's
  structural positions (here: `^## \[DOMAIN` against the established list)
  rather than trusting a visual skim to catch a casing-only mismatch.
- Provenance (verified/assumed): VERIFIED first-hand this session — grepped
  `idea-repository.md` for `^## \[` domain headings restricted to the
  uppercase established-domain pattern and found the two lowercase
  `narrative-design` entries excluded from the match (0 hits for
  `NARRATIVE-DESIGN` before the fix, despite it being an established
  domain per `README.md`); confirmed the correct lowercase sub-tag usage
  of the same string elsewhere in the file (`[RPG / narrative-design /
  ...]`) as the likely source of the miscasing; fixed and re-verified the
  domain-position grep now cleanly matches all 78 entries against the 7
  established domains with zero anomalies.
- Link: session (dog-game-continue-oc3xqh); Pappydapimp69/ideas
  `idea-repository.md` (the two corrected `NARRATIVE-DESIGN` headings),
  `README.md` (`ESTABLISHED DOMAINS`).

## E1 — ideas blueprint marked implemented went stale after a pivot
- Date: 2026-07-11
- Project: pappydapimp69/ideas
- Tags: [process][documentation][gamedev]
- What: `reference/dog-park-3d/LEVEL-3-BLUEPRINT.md` (a design doc in the
  `ideas` repo, written to spec Dog Park 3D's Level 3 before it was built)
  described Rex as a passive "charm meter" the player out-scores via a
  `presentation() >= rexCharm` check, and was marked "✅ IMPLEMENTED."
  Five days later, Dog Park 3D's own commit `4b38a2a` ("Rex becomes a real
  contest instead of a hidden passive meter") replaced that design
  entirely with an interactive fetch-off + Simon-Says trick showcase —
  `rexCharm` no longer exists anywhere in the shipped code. The blueprint
  in `ideas` was never updated to reflect the pivot; it still read as
  current, accurate, "IMPLEMENTED" documentation of a mechanic that hadn't
  existed in the real game for days.
- Why built: The blueprint was written once, at design time, specifically
  to be handed off for implementation — a natural, reasonable artifact.
  Marking it "✅ IMPLEMENTED" after the first build pass was also
  reasonable at the time it was written; nothing about that marker
  distinguishes "implemented and still accurate" from "implemented once,
  then the implementation moved on without telling this file."
- Design: `ideas` and `Pappydapimp69/Dog` are two independent repositories
  with no automated link between them — a blueprint in `ideas` is a
  one-way export at authoring time (design → spec → build), with no
  mechanism (CI check, cross-repo hook, even a manual habit) that revisits
  the spec when the actual implementation is later revised.
- Got right: The blueprint's OTHER claims (the map, the two volunteer
  NPCs, the level-renumbering, the brain lessons applied to the scatter/
  reachability design) all remained accurate — only the Rex mechanic
  itself was later revised, and only that section went stale. The
  blueprint wasn't uniformly wrong, which is part of why it read as
  trustworthy: most of it still checked out.
- Where/why it failed: A cross-repo "spec → implemented" pointer has a
  built-in one-way bias: the IMPLEMENTATION repo (`Dog`) has every
  incentive and immediate feedback loop to stay internally consistent with
  itself (tests, deploys, the running game) — a revision there is felt
  immediately. The SPEC repo (`ideas`) has none of that; nothing breaks,
  deploys, or fails a test when its record of "what got built" drifts from
  what actually got built. The gap is invisible from the `ideas` side
  entirely — it only surfaces if someone deliberately re-reads the spec
  against the current implementation, which nothing prompts anyone to do
  once a feature reads as "done."
- Fix: Added a dated correction directly in the blueprint (not a silent
  rewrite) — kept the original design section as the historical record,
  and appended what actually shipped, when, and why (citing the
  superseding commit), plus a pointer flagging that later same-session
  work (cutscenes, judge-cam, trick animations) isn't reflected in this
  blueprint OR the reference `.js` mirror files under the same folder
  either.
- Why this fix: A design doc that's meant to double as a historical record
  should never be silently overwritten to match new reality — that
  destroys the "why we built it this way, then why we changed it" trail,
  which is often more valuable than either snapshot alone. A dated,
  additive correction preserves both: what was designed, and what's
  actually true now, with an explicit pointer so a future reader (or
  mining pass) can't mistake the superseded section for current fact.
- Rule of thumb: A design/blueprint doc exported to a SEPARATE repo from
  its implementation (spec repo vs. build repo, `ideas` vs. a game repo,
  a wiki vs. a codebase) has no natural mechanism to notice when the real
  implementation is later revised — the spec repo gets no signal, no
  failing test, no broken deploy. Treat any "✅ IMPLEMENTED" marker in a
  cross-repo spec as accurate only as of its own last-touched date, not as
  an ongoing guarantee — and when a shipped feature undergoes a
  significant pivot (not just a bugfix), make updating any cross-repo
  spec/blueprint that described the original design part of the pivot
  itself, with a dated correction rather than a silent rewrite. Periodic
  re-audits (does this spec still match the live code?) are the only thing
  that catches drift that already happened, since nothing else will.
- Provenance (verified/assumed): VERIFIED first-hand this session — read
  the blueprint's Rex section, grepped the live `Dog` repo's `game.js` for
  `rexCharm` (zero occurrences), found the superseding commit `4b38a2a`
  by its own commit message ("Rex becomes a real contest instead of a
  hidden passive meter") explicitly describing what the blueprint's design
  used to be and what replaced it, and confirmed the blueprint's own
  git history shows no commit since touching Rex's description.
- Link: session (dog-game-continue-oc3xqh); Pappydapimp69/ideas
  `reference/dog-park-3d/LEVEL-3-BLUEPRINT.md`; Pappydapimp69/Dog commit
  `4b38a2a`.
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E90 · compatible · sandboxes/2026-10-10__why-comment-stale-sandbox.py · observed RESULT: PASS value-only: what-comments stale 6/6 (checker caught 6), why-comments 0/6; premise-only: why-comments stale 6/6 but checker caught 0 · brain train auto loop 1 pass 1; session_01LphKr4r2NDaVJxz3d1yx7B
