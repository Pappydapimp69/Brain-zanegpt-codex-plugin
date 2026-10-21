# pappydapimp69/brain-pitch — lessons

Project: pappydapimp69/brain-pitch. Newest first.

---

## E3 — unmapped fallback bucket collides across two independently keyed node arrays
- Date: 2026-07-18
- Project: pappydapimp69/brain-pitch (Sprout growth-viz data refresh)
- Tags: [viz][state][data]
- What: Refreshing `IDEA_NODES`/`MEM_NODES` (two separately-sourced arrays of `{id, label, total}`, merged into one shared `clusters{}` object keyed by `id`) with current real counts, an idea-domain mapping function had no case for the literal `[UI-UX / ...]` header token and fell through to a generic `id:"other"` bucket — colliding with memory's own, unrelated `id:"other"` bucket already in `MEM_NODES`. Both wrote into the same `clusters["other"]` key, and the on-screen idea/memory counters (each summed independently over their own node-id list) silently double-counted that one cluster's members into both totals — displayed 513 ideas / 367 memories against a true 445 / 356, an 11-15% inflation with no error, no warning, no visual glitch pointing at the cause.
- Why built: A domain→bucket mapping function written against a known, finite set of tokens (`SYSTEM`, `RPG`, `MUSIC`, ...) needs an explicit fallback for anything unmapped — the natural fallback name is `"other"`, which is also the natural, independently-chosen fallback name for the *other* array's own miscellaneous bucket. Neither array's author was thinking about the other array's id space at the time.
- Design: `clusters[c.id] = {...}` populated by iterating `IDEA_NODES.forEach` then `MEM_NODES.forEach` into the same object — a later `forEach` silently overwrites (here: merges counts into) any id already claimed by the earlier one, no runtime check that the two id sets are disjoint.
- Got right: Every OTHER bucket in both arrays used a real, specific domain token (`SYSTEM`, `gamedev`, `DISTRIBUTION`, etc.) that never collided — this was invisible for every cluster except the two coincidentally-named fallbacks, which is exactly what made it easy to miss.
- Where/why it failed: Caught only by a total-count sanity check (comparing the on-screen counters against the known-true source totals) after the visual render already looked plausible — a `git diff`-level read of the mapping function, or a glance at the rendered clusters, gave no signal, because a single merged "Other" bubble on screen looks exactly as correct whether it holds one array's stray items or two arrays' stray items summed together.
- Fix: Map every real domain token explicitly (the 11 stray `UI-UX` items were folded into the existing `UI-UX` bucket instead of `other`) so the idea side never needs a fallback bucket at all — removing the collision by removing the shared key, not by renaming one side's fallback to something merely different (which only defers the same class of accidental collision to the next two arrays that get merged this way).
- Why this fix: A rename (e.g. `other` → `misc`) fixes this one instance but not the pattern; eliminating the fallback (mapping every real token) is only possible when the token set is actually finite and enumerable, which it was here (the "unmapped" items turned out to be one real, missed token, not genuine miscellany) — worth checking before reaching for a rename, since a real fix is available more often than a fallback-bucket design assumes.
- Rule of thumb: When merging two independently-built id-keyed collections into one shared namespace (here: two `{id,...}` arrays into one `clusters{}` object), treat generic fallback/catch-all bucket names (`other`, `misc`, `unknown`) as a collision risk by default — verify the fallback is either genuinely unreachable (every real token mapped) or explicitly namespaced per source (`idea-other` vs `mem-other`), because two authors choosing the same obvious fallback name independently is the default outcome, not an edge case, and the resulting bug (silently merged, not silently dropped) produces a plausible-looking wrong number rather than a visible error.
- Provenance (verified/assumed): Verified first-hand — reproduced by computing `IDEA_NODES`/`MEM_NODES` totals from the real repo data both before and after the fix; before: on-screen counters read 513/367 (traced to `clusters["other"]` holding 11 idea items + 68 memory items summed together); after remapping the 11 stray items to `UI-UX`, counters read 445/356, matching the independently-computed true totals exactly.
- Link: this session (Sprout viz "brain viz galaxy spiral" → refresh-to-current-data task); file `brain/viz/cognitive-growth.html`.
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E97 · compatible · sandboxes/2026-10-08__cheap-oracle-suite-misses-merged-bucket-collision.py · observed RESULT: PASS cheap suite passes the bug (513/367 vs true 445/356); claim suite fails it; explicit mapping or namespacing fix passes; a third "other" source re-collides after the rename (idea counter 454, true 445). · brain train auto pass 2
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E84 · compatible · sandboxes/2026-10-12__merging-keyed-sets-namespace-every-key-not-just-the-fallback.py · observed RESULT: PASS 4/4; misfiled naive 4, fallback-only 2, full 0, no-overlap 0 · session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6
- Audited: 2026-10-15 · pass · The entry has no stored sandbox, so I read it with the two sandboxes that cite it. Its own evidence is a real computation, not an assumed answer: counters read 513/367 before the fix and 445/356 after, matching independently computed true totals, with the 11 stray items traced to a shared other bucket. The rule of thumb claims fallback names collide by default when two keyed arrays merge and recommends mapping every token or namespacing per source. The cited-by sandbox (brain E97) shows a cheap total check missing the bug, an explicit-mapping or namespacing fix passing, and a third other source re-colliding after a rename; the seven E84 sandbox shows full namespacing reaching 0 misfiled against 2 for fallback-only renaming. Together these cover the stated scope, including the rename-is-not-enough claim. Limit: the original numbers come from one real file I cannot rerun here, so I trust the report for that part. · scheduled brain train audit, loop 2 pass 3; session_01Jm2ZpWfo7KnvQ1ij9SF8pV
- Reverified: 2026-10-15 · pass · sandboxes/2026-10-15__rebuild-brain-pitch-e3-merge-semantics.py · observed RESULT: PASS accumulate naive 360/290 vs 300/200 (both inflated); overwrite (270, 200), first-wins (300, 230); full namespacing exact; fallback-only and exhaustive mapping still wrong in all three semantics because 'audio' was a shared real id (my last prediction refuted) · Rebuilt from the claim only with my own fixture (7 idea header tokens, one unmapped, 300 ideas; 5 memory tags with its own 'other', 200 memories) and three merge semantics, since the claim names the symptom but not the merge code. Under an accumulating merge both counters inflated (360/290 against 300/200), reproducing 'merged, not dropped'. Under overwrite or first-wins there was no double count: one counter read wrong (270 or 230) and the other right, so the 'both totals inflated' symptom is specific to accumulating merges; the bug is silent in all three. Per-source namespacing of every id was exact in all three. Not reproduced by me: fallback-only namespacing and an exhaustive token mapping still miscounted, because my fixture also shared a real id ('audio') - the rule's fix is right for the fallback but not sufficient when real ids overlap (as seven E84 found). The original's sandbox was not opened; its fixture is the real IDEA_NODES/MEM_NODES, mine is synthetic. · session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto pass 4 (rebuild), 2026-10-15

## E2 — a hard exclusion constraint shared by n rotating entities is a global min not a local fix
- Date: 2026-07-18
- Project: pappydapimp69/brain-pitch (Sprout finale-card overlap investigation)
- Tags: [motion][gamedesign][architecture]
- What: Measured (not eyeballed) that Sprout's finale UI card already overlapped several orbiting clusters at rest, unrelated to a separate camera-punch feature being added. Attempted the "correct" fix — bisect the single shared `camera.scale` value down until NO currently-visible cluster's circle intersects the card rectangle, for all ~30 simultaneously-orbiting clusters at once. It technically worked (zero overlap) but collapsed the resting scale from 0.68 to 0.237 — a global zoom-out that gutted the whole scene's "reveal the fully-grown garden" payoff, a far worse visible regression than the overlap it removed. Reverted; this is a design-tradeoff finding, not a bug report (no code shipped from this path).
- Why built: The instinct, once a real overlap is measured, is to add a hard geometric guarantee against it (bisect the shared scale down until the invariant holds everywhere) — this is the same pattern as the file's own existing, working `safeScale` clamp (which already hard-clamps the schedule-driven camera against each node's worst-case orbit extent), so extending it to also exclude a UI rectangle looked like the same kind of fix, just with one more constraint added to the same `min(...)` chain.
- Design: `cardOverlapAtScale(s)` checked every cluster's `(nodeRadius*HALO_MULT*s)` circle against the card's screen rect at candidate scale `s`; bisected `[0, safeScale]` for the largest `s` with zero overlap, then fed that into the same `Math.min(camera.dramatic, safeScale)` the rest of the camera math already used.
- Got right: The bisection itself was correct and the invariant it enforced (zero overlap) held exactly as designed — verified by direct geometric measurement, not by eye, both before (real overlaps at 20-54px) and after (zero hits) the change.
- Where/why it failed: The constraint is a MIN across all ~30 simultaneously-visible clusters, each independently positioned by the scene's own live `rotation` value (the whole spiral formation turns together, so at any instant some cluster's baseAngle can put it anywhere around the ring, including directly under the card). A shared scalar output (`camera.scale`) that every one of those 30 independently-rotating entities must simultaneously satisfy is bounded by whichever SINGLE entity is worst-positioned at that exact instant — with 30 independent angles in play, the realistic worst case is far tighter than intuition (built from picturing one or two offending clusters) suggests, and the fix has no way to know that in advance without actually computing it.
- Fix: None shipped — reverted to the pre-existing behavior (small, measured overlap tolerated) rather than ship the collapse. The design lesson: before applying a hard "avoid this region" constraint to a value SHARED by many independently-varying entities, either (a) measure the constraint's actual worst case across the entities' full range of variation first (here: across the rotation period) rather than reasoning about it from a single frame, or (b) scope the fix to the specific offending entity/entities (e.g., locally fade or nudge just the clusters that would overlap, leaving the shared camera scale untouched) instead of the shared parameter every other entity's rendering also depends on.
- Why this fix: A per-entity fix (fade/nudge the specific offender) only costs something when the specific bug condition is actually true for that entity; a shared-parameter fix (shrink the value everything reads) costs something for EVERY consumer of that parameter, all the time, scaled by whichever single consumer is currently least accommodating — the two are not equivalent in blast radius even when both are geometrically "correct."
- Rule of thumb: A hard, provably-correct constraint is not automatically the right constraint — when it's computed as a MIN/MAX across N independently-varying entities and applied to a value ALL of them share, its cost scales with the worst single entity at any instant, not the "typical" case a single test frame suggests. Prototype or directly measure the constrained value's range across the entities' full variation (here: a full rotation period) before judging whether the fix is acceptable, and prefer scoping a fix to the specific entities that trigger it over tightening a shared parameter everything else also depends on.
- Provenance (verified/assumed): Verified first-hand — measured real overlap (20-54px) at rest before any change via direct geometric circle-vs-rect checks against actual cluster screen positions; measured the fix's resting `camera.scale` collapse (0.68 → 0.237) the same way, both via a real headless-browser run of the actual file (not reasoning about the code alone); reverted and re-verified the file returns to its prior, known-safe behavior (full regression sweep, zero JS errors, hover/reduced-motion still correct).
- Link: this session (Sprout finale-card overlap investigation, "loosen the budget for a bigger punch?" follow-up); file `brain/viz/cognitive-growth.html`.

## E1 — flex title wraps without container growing
- Date: 2026-07-16
- Project: pappydapimp69/brain-pitch
- Tags: [browser][css][flexbox]
- What: a terminal-style panel header (`.console-bar`, a flex row: three status
  dots + a title span, `align-items: center`) with a long title string
  (`zsh — your-repo/`) that had no `white-space: nowrap` set.
- Why built: a chrome-style title bar sitting above a terminal-output body,
  reused across two panels with different title text lengths.
- Design: plain flex row, no explicit width/height on the title span, relying
  on default flex sizing to fit the content.
- Got right: on a wide viewport the title fit on one line and looked correct;
  the bug was invisible in that state.
- Where/why it failed: on a narrow mobile viewport (~390px) the title text no
  longer fit on one line. Because `white-space` was left at its default
  (`normal`), the text wrapped inside its own flex-item box onto 2-3 lines —
  but the bar's rendered height (and its `border-bottom`, drawn where the
  single-line height would have ended) did not visually grow to match, and
  the wrapped overflow lines rendered on top of the sibling content block
  immediately below the bar, producing readable-but-overlapping text. This
  reproduced consistently in a real headless-browser check at 390px and
  360px viewports, not just in a live screenshot from a phone.
- Fix: on any flex-item text meant to render as a single-line label (a title
  bar, a status line, a step indicator), set `white-space: nowrap; overflow:
  hidden; text-overflow: ellipsis;` plus `min-width: 0` on that item (flex
  items default to `min-width: auto`, which blocks shrinking below content
  size and is what allows the wrap to happen in the first place instead of
  the browser truncating or shrinking neighbors).
- Why this fix: matches how real terminal/app title bars behave (truncate,
  never wrap) and removes the box-height mismatch at its root instead of
  trying to make the container grow to match wrapped text.
- Rule of thumb: any flex-row label whose container has a fixed visual
  height (a border, a fixed padding, a divider line to a sibling) needs
  explicit `nowrap` + `min-width: 0` — never assume default flex sizing will
  either wrap gracefully or keep a single line at every viewport width test
  it at your narrowest supported width, not just your dev viewport.
- Provenance (verified/assumed): verified first-hand — reproduced with
  Playwright at 390x844 and 360x740 viewports against the actual built file,
  confirmed the overlap via pixel-region crop, applied the fix, and
  re-verified the same viewports render cleanly.
- Composed: N/A
- Link: pappydapimp69/brain-pitch@87c14e0

