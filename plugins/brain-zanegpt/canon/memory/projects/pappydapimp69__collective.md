# pappydapimp69/collective — lessons

Project: pappydapimp69/collective. Newest first.

---

## E16 — verified zero prefill usage before claiming impact
- Date: 2026-08-01
- Project: Pappydapimp69/Collective
- Tags: [process][prompt-engineering][verification]
- What: After filing an idea kernel that Claude 4.6+ models (including this
  session's own Sonnet 5) reject response-prefill requests with HTTP 400,
  the user asked what this actually means for the Brain system. Rather than
  assert impact, grepped Brain's own CLI source, Collective's full codebase,
  and every project's promoted memory canon (PITFALLS.md + all
  projects/*.md) for any existing use of assistant-role message prefill.
- Why built: the natural failure mode when reporting a newly-learned
  external-API change is to imply or assume it matters somewhere without
  checking — inflating urgency on a hunch reads as more useful than a flat
  "nothing's affected," but it isn't actually more honest or more useful.
- Design: two greps — `grep -rn "prefill\|role.*assistant"` across
  `~/.brain/Brain/bin/brain` and Collective's source tree, and
  `grep -in prefill` across `~/.brain/memory/PITFALLS.md` and every
  `projects/*.md` file (122 distinct projects) — excluding the newly-filed
  entry's own text.
- Got right: checking both the LIVE code paths (Brain's CLI, Collective)
  and the RECORDED canon (all 122 projects' lessons) before answering,
  instead of just one or the other.
- Where/why it failed: N/A — this is a clean verification pass, not a bug.
- Fix: N/A — nothing needed fixing; the answer was "zero current exposure,"
  reported as such.
- Why this fix: There was nothing to repair, so the value of the pass is the negative result itself: two greps over the live code paths and the recorded canon convert an assumed exposure into a measured zero, which is what makes "nothing is currently affected" reportable rather than merely believed. Recording the scope that was searched is what lets the finding be re-checked cheaply when the next model change lands.
- Rule of thumb: When a newly-learned external API/model behavior change
  (deprecation, breaking change) surfaces, don't assert or imply impact —
  grep the actual live codebase(s) AND the recorded canon for real usage
  before answering "what does this mean for us." A confirmed "nothing is
  currently affected" is exactly as valuable a finding as confirmed
  breakage, and asserting risk without checking erodes trust the moment
  someone verifies it themselves.
- Provenance (verified/assumed): Verified first-hand — direct grep across
  Brain's CLI source, Collective's full repo, and all 122 projects'
  PITFALLS.md/project files this session; zero hits for prefill/assistant-
  role construction anywhere outside the newly-filed PROMPT-ENGINEERING
  idea kernel itself.
- Composed: N/A
- Link: this session; ideas repo entry
  `response-prefill-is-deprecated-on-current-models`

## E15 — brain query substring matching inflates counts
- Date: 2026-08-15
- Project: Pappydapimp69/Collective
- Tags: [tooling][process][observability]
- What: While scanning ~40 candidate topics for coverage gaps with `brain query`,
  the term `raft` reported 23 memory / 44 idea hits, implying the distributed-
  consensus algorithm was already well covered. It is not: `matches()` tests
  substring containment, so `raft` matched "d**raft**" (a project slug appearing
  throughout canon) and "c**raft**" (which appears in almost every craft-domain
  entry). The real coverage for Raft-the-algorithm is approximately zero.
- Why built: the gap-detection workflow (`brain train gap`) explicitly says a
  near-zero query result IS the signal for a real gap. The inverse — a HIGH
  count read as "already covered" — is used just as often to SKIP a topic, and
  nothing warns that the count may be inflated.
- Design: `matches(block, terms)` in `bin/brain` returns true if any term is a
  substring of the lowercased block, or if its punctuation-stripped form is a
  substring of the stripped block. There is no word-boundary check, so any short
  query term is a substring of longer unrelated words.
- Got right: substring matching is the right default for this corpus — it is
  what lets `metallic-roughness` match prose containing `metallic-roughness,`
  and lets partial technical terms find their entries at all. The behaviour is
  not a bug in isolation; the gap is that its failure mode is silent and
  asymmetric.
- Where/why it failed: the false positive is invisible at the summary level. A
  count line reading `23 memory · 44 idea` looks like strong coverage and
  invites skipping the topic; only opening `--verbose` and reading the headers
  reveals that none of them concern the queried subject. Short terms (<= 5
  chars) and terms that are common English substrings are the danger zone, and
  those are exactly the kind of term a terse query uses.
- Fix: for any query whose result will be used to conclude "this is already
  covered", confirm with `--verbose` and read the actual headers before
  skipping. Prefer longer, distinctive, hyphenated terms (`raft-consensus`,
  not `raft`). Treat a high count on a short term as unverified.
- Why this fix: the cost is asymmetric. A false NEGATIVE (0 results on a bad
  phrasing) is now caught automatically by the CLI's retry guard added earlier
  today; a false POSITIVE has no such guard and silently suppresses work that
  should have happened, which is the more expensive direction because nothing
  ever surfaces it.
- Rule of thumb: `brain query` counts are substring matches with no word
  boundary — a short term inflates its own coverage by matching inside longer
  unrelated words (`raft` in `draft`/`craft`). Never conclude "already covered"
  from a count alone; open `--verbose` and read the headers, and prefer
  distinctive multi-part terms when the answer will decide whether to skip work.
- Provenance (verified/assumed): Verified first-hand — reproduced `matches()`
  exactly in a standalone script this session and confirmed `raft` matches "a
  draft entry about level design" -> True, "procedural craft technique" ->
  True, and the control "the raft consensus algorithm" -> True; also confirmed
  the degenerate case `at` matches "cat photos" -> True. The inflated count was
  first observed in a real 40-topic gap scan, not constructed.
- Composed: N/A
- Link: this session; `bin/brain` `matches()` / `_norm()`

## E14 — prose guidance does not stop precondition errors
- Date: 2026-08-15
- Project: Pappydapimp69/Collective
- Tags: [process][tooling][cli]
- What: Three precondition errors recurred repeatedly across one long session
  — running `brain link` from inside the cache (which git-inits a node repo's
  subfolder and plants a `.brain` store in it), running other `brain` commands
  from a cache dir and reading the bare "not linked" as a broken link rather
  than a wrong cwd, and reading a 0-result multi-word `brain query` as "the
  system is empty" when the canon keys its headers on hyphenated kebab slugs.
  All three were already documented in prose in CLAUDE.md, which the same agent
  had read at session start.
- Why built: the standing assumption behind CLAUDE.md's guidance section is
  that documenting a trap prevents it. This session is a counterexample with a
  large sample: the query-phrasing trap was diagnosed OUT LOUD mid-session and
  then repeated twice more by the same agent in the same session.
- Design: the guidance lived only as prose in CLAUDE.md ("Query with 1-2
  KEYWORDS, not sentences... A 0-result query almost always means rephrase, not
  'empty system'"), with nothing in the CLI checking any of it. `require_link`
  emitted an undifferentiated "not linked", `cmd_link` had no location check at
  all, and `cmd_query` reported zero and stopped.
- Got right: the prose was accurate and specific — it named the exact failure,
  the exact cause, and the exact fix. The gap was purely that nothing enforced
  it at the moment of the mistake.
- Where/why it failed: prose guidance is read once, at the start, in a context
  where none of the three situations is live; the error happens later, under
  task focus, when the agent is not re-reading anything. Worse, the failures
  are all SILENT-ish — a 0-result query and a "not linked" line both look like
  ordinary states rather than mistakes, so nothing interrupts the flow to
  trigger recall. Documentation competes with attention; a gate does not.
- Fix: moved all three into `bin/brain` as hard checks (commit 9ad2eed):
  `cmd_link` refuses when the cwd is inside the cache and says why;
  `require_link` distinguishes "no link here" from "you are standing in the
  cache"; `cmd_query` retries a 0-result multi-word query against the
  hyphen-joined slug and the individual tokens, and re-runs automatically on a
  hit. Kept the prose too — the code states the rule, the prose states the
  reason.
- Why this fix: each of the three is mechanically decidable at the moment of
  use from information the CLI already has (cwd vs CACHE; result count vs term
  count). Anything decidable at the point of failure belongs at the point of
  failure, not in a document read hours earlier.
- Rule of thumb: if a documented trap keeps getting hit by readers who have
  read the document, that is evidence about the ENFORCEMENT POINT, not about
  the reader's diligence — move any check the tool can make itself into the
  tool, and leave the prose to explain why the check exists. Documentation
  competes with attention at the moment of the mistake; a refusal does not.
- Provenance (verified/assumed): Verified first-hand — all three failures
  occurred in this session (a nested `.git`, `.brain` store, CLAUDE.md and
  pre-commit hook were created inside `ideas/incoming/` and had to be undone
  with `brain unlink --force`), and all three guards were tested against those
  exact reproductions after implementation. Notably the query guard's FIRST
  implementation tokenised on argv only, so a quoted phrase — the precise way
  the failure occurs — arrived as a single term and the guard silently never
  fired; caught by testing it against the real failing command rather than a
  constructed one, and fixed to split whitespace within terms.
- Composed: N/A
- Link: this session; Brain commit 9ad2eed (`bin/brain`: `_inside_cache`,
  `cmd_link` guard, `require_link` message, `cmd_query` phrasing retry)
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E223 · compatible · sandboxes/2026-10-14__zero-allow-history-needs-a-benign-canary.py · observed RESULT: PASS zero-allow ambiguous in 1/3 histories (all-risky), canary separates 3/3, distinct hold leaks threshold in 7 probes, identical ack leaks none · brain train auto pass 5, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU

## E13 — sync ignores ideas incoming
- Date: 2026-07-31
- Project: Pappydapimp69/Collective
- Tags: [process][tooling]
- What: `brain sync` (full mode) reports "0 pushed to main, 0 held" after a validated, git-committed proposal was written to `~/.brain/ideas/incoming/` — the proposal silently never reaches the ideas repo's steward through `brain sync` at all.
- Why built: filed a new SONGWRITING idea kernel via the documented ideas/README flow (copy TEMPLATE.md into `incoming/`, fill it in, `python3 scripts/validate.py`, commit), then ran `brain sync` expecting it to push and trigger promotion, matching how the `memory` node's incoming/ proposals work.
- Design: reading `cmd_sync()` in `~/.brain/Brain/bin/brain` shows "full" mode calls `_push_local_to_main()`, which ONLY reads `local_root()/memory/incoming/*.md` and copies those into the shared `memory` node's `incoming/`, commits, and `git push`es the memory repo. It never touches the `ideas` node at all — ideas proposals aren't part of sync's data flow in either direction.
- Got right: `python3 scripts/validate.py` inside `~/.brain/ideas` correctly validated the new proposal file's schema before commit, so the format itself was never in question.
- Where/why it failed: `brain sync`'s "0 pushed to main, 0 held" is indistinguishable from "your proposal has a problem" or "there was nothing to sync" — it gave no signal that the ideas node isn't part of what sync operates on, so the natural read is "the promotion failed" rather than "wrong command for this node."
- Fix: for an `ideas` node proposal, after `validate.py` passes, commit it and push directly — `cd ~/.brain/ideas && git add incoming/<file> && git commit -m "..." && git push origin main`. The ideas repo runs its own steward via CI (`.github/workflows/steward.yml`) on push to `main`, independent of `brain sync`. Confirmed first-hand: pushing directly triggered `steward-bot: promote passing proposals / hold exceptions` within seconds, and the entry became retrievable via `brain query`.
- Why this fix: `brain sync` is scoped to the `memory` node only (by reading its source, not by guessing); the `ideas` node's promotion path is push-triggered CI on its own repo, so a manual `git push` on that repo is the correct and only way to get a validated ideas proposal into canon.
- Rule of thumb: `brain sync`'s pushed/held counts describe the `memory` node only — a validated, committed proposal sitting in `~/.brain/ideas/incoming/` (or any other node besides `memory`) needs its own `git push origin main` in that node's repo; don't read "0 pushed" from `brain sync` as evidence an ideas/tension proposal failed or has nothing to promote.
- Provenance (verified/assumed): Verified first-hand — read `cmd_sync`/`_push_local_to_main` source directly, reproduced the "0 pushed" result, then reproduced the working fix (direct push) and confirmed promotion via `git log origin/main` showing the steward-bot commit and `brain query` retrieving the promoted entry.
- Composed: N/A
- Link: this session (SONGWRITING idea `mock-heroic-scale-inflation-without-winking`, promoted at ideas repo commit 8c02605)

## E12 — playwright fullpage screenshot duplicates position fixed elements
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [testing][tooling][browser]
- What: NON-BUG — a Playwright `page.screenshot({fullPage:true})` of a page with a `position:fixed;bottom:0` action bar showed that bar rendered TWICE: once appearing to float mid-content over a results card, and effectively absent/duplicated near the true bottom of the stitched image. This looked exactly like the kind of overlap bug worth filing (fixed content bleeding into scrolled content), so it was investigated rather than dismissed.
- Why built: N/A — this is a test-methodology finding, not a feature. Recorded so a future session doesn't re-spend time diagnosing the same artifact as a real defect.
- Design: Re-tested the identical page state with a normal (non-fullPage) screenshot after programmatically scrolling to a specific `window.scrollTo(0, Y)` offset, capturing only the actual viewport rather than Playwright's full-page stitch.
- Got right: The instinct to verify before dismissing — a genuinely-plausible-looking bug report deserves a real check, not an assumption either way.
- Where/why it failed: Playwright's `fullPage:true` capture works by scrolling the page and stitching multiple viewport-sized screenshots into one tall image. A `position:fixed` element is, by definition, re-rendered at the SAME on-screen location at every scroll position the stitcher captures — so it gets pasted into the final composite once per stitched segment, appearing to "duplicate" or "float" over unrelated content in the merged image. This is an artifact of the stitching process itself, not of the page's actual rendering at any single real scroll position.
- Fix: No code change — confirmed via a targeted (non-fullPage) screenshot at a real scroll offset that the fixed bar renders exactly once, in the correct place, with a clean gradient fade and no overlap with scrolled content.
- Why this fix: There is no "fix" because the artifact is a property of the
  screenshot TOOL, not the page — `fullPage:true` works by capturing a
  sequence of viewport-sized screenshots at successive scroll offsets and
  stitching them into one image, so any `position:fixed`/`sticky` element
  (defined to stay put on-screen regardless of scroll) is, by construction,
  present in EVERY one of those stitched segments and gets pasted into the
  composite once per segment. Verifying with a real scroll offset plus a
  viewport-only capture bypasses the stitching step entirely, so it reflects
  what a real user's screen actually shows at any single moment — the
  correct ground truth this class of bug report needs to be checked against.
- Rule of thumb: Never trust a Playwright `fullPage:true` screenshot to judge how a `position:fixed`/`position:sticky` element actually looks or behaves — it will appear to repeat once per stitched segment regardless of correctness. Verify fixed/sticky elements with viewport-only (non-fullPage) screenshots taken at specific `window.scrollTo()` offsets, or by asserting `getBoundingClientRect()` values directly, not by eyeballing a fullPage capture.
- Provenance (verified/assumed): VERIFIED first-hand — same page, same state, two screenshot methods; `fullPage:true` showed the apparent duplication, a scrolled non-fullPage capture at the same effective scroll position showed correct single rendering. Reproducible and deterministic (static layout, no animation/timing involved in either capture).
- Composed: N/A
- Link: this session; Playwright `chromium.launch` headless screenshots, `fullPage:true` vs `window.scrollTo()` + viewport-only screenshot on the same page state

## E11 — rebuild from the products own live data not third party summaries
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [data][web][process]
- What: A character-recommendation app for a live-service game (Dragon Ball: Gekishin Squadra) shipped with ability/skill data built from third-party build-guide/tier-list SNIPPETS (dbgsbuilds.com, gamerblurb.com, search excerpts). Much of it was wrong or outdated: e.g. Android 17 listed skills ("Barrier Formation", "Explosive Barrier") no longer in the game, and Vegeta had been given a passive ("Solitary Guardian") that actually belongs to a DIFFERENT hero slot (SS4 Vegeta). A user who plays the game caught it immediately.
- Why built: External direct fetches were blocked early in the project (local proxy allowlist), so the only reachable data was WebSearch snippets of community fan sites — themselves lagging the game's live patches. That was accepted as "the best available" and hardened into shipped data.
- Design: The fix was to stop trusting summaries and reconstruct from the product's OWN data. The game is a Next.js site; its full hero database (all 38 heroes, every skill name/description/stat, every locale) ships as a JSON blob embedded inside one of its client JS bundles (`chunk 6765-…`, webpack module id `88260`, key `"PG"`). Fetched the bundle with curl, sliced out the module's function body by brace-counting, executed it against a mock `{exports:{}}` to recover the JSON, then regenerated every character's abilities from it programmatically.
- Got right: Once network access was restored, re-verifying the CURRENT build before trusting the extract — fetched a live hero page and confirmed it still references the same bundle hash, so the cached chunk wasn't stale. Also kept the interpretive layer (my own playstyle-axis scores) separate from the factual layer (official abilities/roles), so only the factual layer needed the resync.
- Where/why it failed: Third-party summaries of a LIVE product are a lossy, lagging mirror — they drift silently as the product patches, and a snippet can attribute one entity's data to another (the Vegeta/SS4-Vegeta passive mix-up). Nothing about the snippet flags that it's stale; it reads as authoritative. Building shipped data on that foundation guarantees eventual, invisible wrongness that only a domain expert notices.
- Fix: When a live product exposes its own data feed — even an undocumented one embedded in a JS bundle, a GraphQL response, an internal JSON API — reconstruct from THAT and treat third-party write-ups as context/color only, never as the system of record. Verify the extract is from the current build (check the live page still references the same asset hash) before trusting a cached copy.
- Why this fix: The product's own shipped data is the single source of truth by construction — it's literally what the live client renders. A community summary is someone's hand-transcription of a past version of that truth. For any factual field that a user of the product can directly check, the gap between "authoritative feed" and "third-party summary" is the gap between correct and embarrassingly-wrong.
- Rule of thumb: For factual data ABOUT a live product, mine the product's own data surface (embedded bundle JSON, internal API, page data island) rather than third-party summaries — summaries of a live system rot silently and misattribute. If only summaries are reachable, mark the data explicitly low-confidence and re-sync from the authoritative source the moment it's reachable; and always confirm you pulled the CURRENT build (asset-hash check) before trusting an extracted blob.
- Provenance (verified/assumed): VERIFIED first-hand — extracted the official 38-hero JSON from the live bundle, diffed it against the shipped app data (found role-correct but ability-names stale across ~24 characters, plus the Vegeta passive misattribution), regenerated all ability arrays from it, and confirmed via headless browser that the corrected kits render. The staleness itself was user-reported and reproduced against the official data.
- Composed: N/A
- Link: this session; official hero bundle `dbg-squadra.bn-ent.net/_next/static/chunks/6765-…js` module 88260; user-reported stale Android 17 skills

## E10 — narrate the computed vector in second person to make personalization feel warm
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [ui][ux][design]
- What: A recommender app modelled the user as a 7-axis playstyle vector and surfaced it as labelled bar-charts (aggression, range, mobility, …). A user's feedback: it "comes across as cold and distant." The underlying math was fine; the PRESENTATION of the personalization read like a diagnostic readout, not like the app understood them.
- Why built: The vector drives every recommendation, so showing it is honest and useful. But the first cut showed it the way it's stored — as axes and dots — which is how a developer thinks about the user, not how the user experiences being understood.
- Design: Added a dedicated "You, as the Scouter sees you" profile screen whose LEAD element is a second-person sentence generated from the same vector: it picks the 2–3 dominant axes and renders them as prose — "Based on what you've told us so far, you like to dive in first, you love landing one big finisher, and you never stop repositioning." The raw axis bars stay, but BELOW the sentence, as supporting detail for anyone who wants the numbers.
- Got right: The narrative is generated from the exact same `playerVector()` that ranks the roster — it's not a separate hand-wavy blurb that could drift from the real model. Each axis carries a pre-written hi/lo phrase ("you like to dive in first" / "you play patient and reactive"), and only axes past a magnitude threshold are spoken, so a flat/undeveloped profile honestly says "nothing dominates yet" instead of inventing a personality.
- Where/why it failed: A computed profile shown as chart primitives (bars, dots, axis labels) is information WITHOUT recognition. Users don't feel "seen" by a bar at 80%; they feel catalogued. The same data spoken back in second person crosses from "here is a measurement of you" to "here is what I've noticed about you" — which is the entire emotional point of personalization. The failure was treating a warmth problem as if it were a data-completeness problem.
- Fix: For any user-model that's meaningful enough to show, render its dominant dimensions as second-person natural-language BEFORE (or instead of) the raw numeric view. Drive the prose from the same values the system acts on. Gate each statement on a confidence/magnitude threshold so a thin model stays honest ("not much to go on yet") rather than fabricating traits.
- Why this fix: The recognition is carried by voice and framing, not by more data or prettier charts. Second-person prose sourced from the live model is cheap to build, cannot drift from the real recommendations (same source), and converts a cold readout into something that feels like attention — which is what makes a personalized tool feel personal rather than clinical.
- Rule of thumb: When a computed user-model (preference vector, taste profile, cluster) reads as "cold/clinical," the fix is usually framing, not more data: narrate its dominant dimensions back in second person ("you tend to…"), generated from the SAME values the system acts on, gated on a magnitude threshold so a thin profile admits it's thin. Keep the raw chart as optional supporting detail underneath, not as the headline.
- Provenance (verified/assumed): VERIFIED first-hand that the narrative is generated from the live vector and renders correctly across empty/partial/populated states (headless checks: empty state shows the "still a stranger" copy, a rated profile shows the dominant-axis sentence). The claim that it reads "warmer" is the USER'S qualitative judgement that prompted the change and my design rationale — a UX judgement, not a measured A/B result.
- Composed: N/A
- Link: this session; `buildProfileScreen` / `AXIS_PHRASE` narrative generation in squadra_app artifact; user feedback "cold and distant"

## E9 — localstorage in sandboxed artifacts throws guard at load and validate on restore
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [browser][state][ui]
- What: A single-file HTML app (a Claude Artifact) needed to remember the user's picks/ratings across visits via localStorage, so a returning user isn't forced through the whole onboarding pick-flow again.
- Why built: The app's value compounds as the user rates more characters; losing all of it on refresh made every visit start cold. Persistence turns it from a one-shot toy into something worth returning to.
- Design: One JSON blob under a versioned key (`squadra_scouter_v1`) holding the owned-set, favorites, ratings, and attack-ranks. Sets serialized as arrays. `saveState()` fires on every mutation (chip toggles, star taps, attack-rank taps); `loadState()` runs ONCE before first paint, ahead of the initial render.
- Got right: Two defensive properties that are easy to skip and expensive to omit: (1) EVERY storage access is wrapped in try/catch, and (2) restore VALIDATES every field rather than trusting the blob — only known character ids are re-admitted, star values are range-checked (1–5), arrays are length-clamped. A partial or hand-corrupted blob degrades to "ignore it and start fresh," never a thrown exception.
- Where/why it failed: The naive version — `JSON.parse(localStorage.getItem(k))` at startup, unguarded — has two separate failure modes that both kill the app before it renders. (a) In a sandboxed embed context (artifact iframe, some in-app webviews, private-mode variants), touching `localStorage` at all can THROW a SecurityError rather than returning null — so the access itself, not just the parse, must be guarded. (b) Once the persisted schema is real, it WILL drift as the app evolves (a field renamed, an id removed); an old or truncated blob then parses into shapes the current code doesn't expect. Either one, unguarded at load, is a white-screen-on-open with no obvious cause.
- Fix: Guard the storage CALL itself (not just the JSON.parse) in try/catch, at both save and load. On load, treat the blob as untrusted input: validate/whitelist every field back in, clamp ranges, drop unknown ids, and let any failure fall through to default in-memory state. Never let persistence be able to prevent first paint.
- Why this fix: Persistence is a nice-to-have; rendering is not. The correct failure mode for "storage is unavailable or corrupt" is "run exactly as a first-time visitor," which requires that no storage path can throw uncaught and no restored value can be malformed enough to crash a render. Wrapping only the parse (a common half-measure) still dies on the throwing getItem in a sandbox.
- Rule of thumb: Treat localStorage as a fallible, untrusted side channel, especially inside sandboxed/embedded contexts (artifacts, iframes, in-app webviews) where the ACCESS itself can throw, not just the parse. Wrap every get/set in try/catch, run the load before first paint, and validate every restored field (known keys only, clamp ranges, length-limit arrays) so a corrupt or schema-drifted blob degrades to a clean first-run instead of a blank screen.
- Provenance (verified/assumed): VERIFIED first-hand — headless-browser round-trip test: seeded state → saveState → cleared in-memory → loadState restored it; reloaded a persistent browser context and confirmed a real returning-visitor restore; and fed the key deliberately-corrupt JSON, confirming the app still loaded to a clean first-run state with zero console errors. ASSUMED (documented, not re-tested here): the specific claim that some artifact sandboxes throw on `localStorage` access is why the guard wraps the access and not only the parse — the try/catch makes the app correct whether or not a given host throws.
- Composed: N/A
- Link: this session; `saveState`/`loadState` in squadra_app single-file artifact; Playwright persistence + corrupt-blob resilience test

## E8 — fixed viewport height cuts off primary cta when only width tested
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [browser][mobile][ui][testing]
- What: A single-page artifact ("Squadra Scouter," a DBZ character-recommender built and published as a Claude Artifact this session — not committed to this repo, so provenance is the session transcript, not a diff) had its primary CTA button ("Start the scouter →") sit entirely below the fold in a real mobile in-app artifact viewer, confirmed by the user's own screenshot. The page was natively scrollable (no `overflow:hidden`), but nothing signaled that scrolling was necessary, so the button read as missing/cut off.
- Why built: Every prior mobile-responsiveness check this session — for this artifact and an earlier, unrelated one (Brain's own cognitive-growth viz, see the sibling `[browser][ui]` control-bar-overflow lesson) — varied viewport WIDTH (1200/412/390px) but always kept a generous, near-full-device HEIGHT (844px+). A real artifact viewer's own chrome (title bar + OS nav bar) eats into the vertical space an app actually gets, which no test this session had ever modeled.
- Design: Diagnosed with a Playwright check at a deliberately realistic constrained-height viewport (412×660 — simulating in-app-viewer chrome eating ~180px off a typical ~844px device height) reading the CTA's `getBoundingClientRect()` against `window.innerHeight`. Confirmed: `viewportH: 660, bodyScrollH: 831, btnBottom: 770.9, btnVisible: false, isScrollable: true` — the exact shape of the user's screenshot.
- Got right: The page's document-flow/scroll model itself was already correct (no `overflow:hidden` trap, `min-height:100vh` document layout) — the defect was purely that the primary action lived in normal scroll flow with no affordance signaling more content was below, not a structural layout bug.
- Where/why it failed: `position:fixed` bottom action bar wasn't the first fix tried in isolation — see the companion `[browser][animation][ui]` lesson (same session) for a second-order bug this fix itself introduced and how it was resolved. The root cause here specifically: test coverage only ever varied the dimension (width) that was already known to be a risk from a prior bug, never the dimension (height) that was the actual gap.
- Fix: Replaced five separate per-screen button rows (normal document flow) with ONE persistent `#actionBar` living outside the animated screens, `position:fixed;bottom:0`, sized `width:100%;max-width:<content-max-width>` (not content-width — avoids the exact overflow class from the sibling control-bar lesson), with a `linear-gradient` fade backdrop so it reads over scrolled content. Verified via Playwright at 320×480, 412×660, 375×812, 1280×900 — primary CTA `getBoundingClientRect()` fully within the viewport on EVERY screen at EVERY size, both before any scroll and after scrolling to `document.documentElement.scrollHeight` (confirming trailing content never ends up hidden behind the bar either).
- Why this fix: A `position:sticky` bottom element was considered and rejected — sticky only activates once the browser would otherwise have scrolled it into view, so on a LAST-child button (the common case here), it provides zero benefit on initial page load, which is exactly the failure state being fixed. Fixed positioning is unconditional regardless of scroll offset, which is what "reachable the instant the screen loads" actually requires.
- Rule of thumb: When testing "does this artifact/page work on mobile," a WIDTH sweep alone is an incomplete test — real host chrome (in-app artifact viewers, browser toolbars, OS nav bars) constrains HEIGHT independently of width, and a normal-flow primary CTA below a tall intro/content block can be fully invisible on load with no failure signal other than a human screenshot. Test viewport HEIGHT as deliberately as width (e.g. 480-660px, not just 812-900px), and prefer making any primary action `position:fixed` to the viewport rather than trusting scroll-discoverability, if the action must be reachable on first paint.
- Provenance (verified/assumed): VERIFIED first-hand — Playwright `getBoundingClientRect()` measurements before the fix (reproducing the user-reported cutoff exactly) and after (0 failures across a 4-viewport-size sweep, both on-load and at max-scroll), plus visual screenshots matching the numeric assertions. Deterministic static layout measurement, no timing/animation dependency in the final assertions.
- Composed: N/A
- Link: this session; user-reported via screenshot; fix verified via headless Playwright viewport sweep (320×480, 412×660, 375×812, 1280×900)

## E7 — animated ancestor transform hijacks position fixed containing block
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [browser][animation][ui][testing]
- What: Fixing a mobile-viewport CTA-cutoff bug (sibling `[browser][mobile][ui]` lesson, same session) by giving each screen its own `position:fixed;bottom:0` button row produced wildly wrong button coordinates on some screens (`getBoundingClientRect().top` in the thousands of pixels on a 660px-tall viewport) — but only on screens with tall content, and only when measured shortly after a screen transition.
- Why built: Each `.screen` element had `animation:fadein .3s ease` (`from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none}`) for a soft entrance. The Playwright test measured `getBoundingClientRect()` after an 80ms `waitForTimeout` — well inside that 300ms animation window.
- Design: Per the CSS spec, ANY non-`none` `transform` on an element makes that element the containing block for its `position:fixed` descendants (not just the viewport) — this applies for the full duration a transform value is active, including mid-keyframe-animation, not only for `transform` set as a static style. A `.screen` with `animation:fadein` has a live, non-`none` `transform` for the first ~300ms after becoming active; any `position:fixed` element nested inside it during that window is positioned relative to the `.screen`'s own box, not the viewport.
- Got right: The fixed-positioning fix itself (see sibling lesson) was structurally correct in isolation — verified separately, with adequate `waitForTimeout` after the animation settled, the coordinates were exactly right. The bug was specifically about the TRANSIENT animated window, not the steady-state fixed-position math.
- Where/why it failed: Initial per-screen fixed action bars were nested INSIDE the animated `.screen` container (matching the existing DOM structure of the buttons they replaced). During the ~300ms fade-in, that ancestor's live `transform` silently re-anchored the "fixed" bar to the screen's own (potentially very tall, off-screen-extending) box instead of the viewport — producing coordinates that looked like a completely broken feature, not a timing artifact, unless you already suspected animation timing as the cause.
- Fix: Moved the action bar OUT of `.screen`/`#app` entirely — a single persistent `#actionBar` as a sibling at the top level of `<body>`, whose content (label/handler) is swapped via JS per screen instead of duplicating a fixed bar inside every animated container. This structurally cannot be affected by any screen's transform, at any point in its animation lifecycle, because it shares no ancestor with the animated element.
- Why this fix: Simply lengthening the test's `waitForTimeout` past 300ms would have hidden the symptom without fixing anything — real users still perceive a ~300ms window where the "fixed" bar is in the wrong place (a visible jump/flash as the animation completes and containing-block reverts to the viewport). Relocating the fixed element outside any transform-animated ancestor removes the hazard at its source rather than timing around it.
- Rule of thumb: `position:fixed` is NOT guaranteed to be viewport-relative — it's relative to the nearest ancestor with a non-`none` `transform` (also `filter`, `perspective`, `will-change:transform`, and a few others), and this includes an ancestor whose transform only exists transiently via a CSS `animation`/`transition`, not just a static inline style. Before trusting `position:fixed` math in tests, either verify no animated ancestor is mid-transition, or — more robustly — keep any `position:fixed` element as a sibling of (not nested inside) anything that animates `transform`. A test that only measures well after animations settle can silently miss this class of bug entirely.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced by measuring `getBoundingClientRect()` at 80ms post-transition (mid-animation, buggy) vs 250-400ms post-transition (post-animation, appeared correct) on the SAME per-screen-fixed-bar implementation, isolating the animation window as the cause; confirmed fixed by moving the bar outside `.screen` and re-measuring at 80ms — coordinates now correct immediately, no timing dependency. The CSS containing-block-via-transform mechanism itself is documented browser behavior (CSS Transforms spec), not an assumption.
- Composed: N/A
- Link: this session; discovered via Playwright `getBoundingClientRect()` measurements taken at varying delays post-screen-transition on 412×660/320×480/375×812/1280×900 viewports (found while fixing the sibling `fixed-viewport-height-cuts-off-primary-cta` lesson from the same session)

## E6 — aggregated preference vector as raw sum pins a clamped display and reads as frozen
- Date: 2026-07-15
- Project: pappydapimp69/collective
- Tags: [algorithm][ui][stats]
- What: A recommender app builds a 7-axis player "playstyle" vector by accumulating weighted character trait-vectors (from star ratings, picks, ranked skills), then shows it as axis bars and uses it to rank characters by distance. The user reported the profile "doesn't even update" — rating more characters seemed to do nothing to the displayed profile.
- Why built: The vector is the whole product — it drives both the profile screen and the ranked guide. Each new rating is supposed to visibly reshape it.
- Design: The bug was the aggregation: `P[axis] = Σ (weight_i · trait_i)` — a RAW weighted SUM. Every rated character adds its (weight × trait) with no normalization, so the magnitude grows without bound as you rate more. The axis-bar renderer, meanwhile, clamped to the trait space's own range: `px = 50 + clamp(P[axis], -2, 2)/2 * 50`.
- Got right: The value WAS updating — it was just growing past the display's clamp ceiling. The distance-based match% also technically responded, but with a maxD that scaled with total weight, so it too drifted oddly. The instinct to distrust "it doesn't update" and actually log the raw vector (rather than assume a missing re-render/save) is what surfaced the real cause.
- Where/why it failed: A raw sum of same-signed contributions crosses the ±2 clamp after the FIRST strong rating (a single 5-star on a trait-2 character already gives 1.2·2 = 2.4 > 2). From then on the bar pins to the edge and never moves again no matter what you add — so the display looks frozen even though the underlying number keeps climbing. The clamp didn't cause the bug; it HID it, converting "value out of display range" into the visual signature of "value not changing at all." Two different failure modes with the same on-screen appearance.
- Fix: Normalize to a weighted AVERAGE — `P[axis] = Σ(weight_i · trait_i) / Σ|weight_i|`. This keeps P in the exact same bounded space (−2..2) as each individual character's trait vector, so: (a) every new input measurably shifts the average and the bar moves; (b) the value never leaves the display range, so the clamp is a no-op safety net, not a wall; (c) match% gets a FIXED, honest denominator — `maxD = sqrt(nAxes · (range)²)` — the max possible distance between two points in that bounded space, giving a stable, comparable 0–100% instead of one that rescaled with how much you'd rated.
- Why this fix: An aggregate meant to represent a CENTRAL TENDENCY ("what kind of player are you, on average") should be an average, not a sum — a sum encodes "how much total signal" and is unbounded by construction, which is exactly wrong for something you plot in a fixed-range widget and compare by distance. The average lives in the same space as the things it's compared against, which is what makes both the visualization and the distance metric well-defined.
- Rule of thumb: When an aggregated preference/profile vector feeds BOTH a fixed-range display and a distance/similarity match, aggregate it as a normalized weighted AVERAGE (÷ total absolute weight), not a raw weighted sum — a sum grows unbounded, pins any clamped bar to the edge after one strong input (looking "frozen"), and gives distance a moving denominator. Separately: a "the display doesn't update" report on any CLAMPED visualization should first make you suspect the underlying value has left the display's range (still changing, just off the top), not that it's static — log the raw number before hunting for a missing re-render or save.
- Provenance (verified/assumed): VERIFIED first-hand — reproduced the raw-sum vector pinning axes past ±2 after one 5-star rating; after switching to the weighted average, headless-measured that rating a second, opposite-type character shifted P (e.g. aggression 2.0 → 1.5, durability −1.0 → +0.5), that every P value stayed within [−2, 2], and that match% spread across a realistic range (29–100%, 25 distinct values) instead of collapsing. Deterministic numeric computation, no timing involved.
- Composed: N/A
- Link: this session; `playerVector()` raw-sum → weighted-average change in the Squadra Scouter artifact; user report "the profile doesn't even update"
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E8 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — prompt is not a trust boundary
- Date: 2026-07-11
- Project: pappydapimp69/collective
- Tags: [security][prompt-engineering][process]
- What: A public system is driven by a prompt users paste into their own LLM. Every actual restriction — which modes are allowed, that auto may only touch objective-signal gaps, that a session can never close a gap, that writes land only under `gaps/` — is enforced by a server-side steward that runs on the GitHub side, not by the prompt's wording.
- Why built: To let the public help improve a private knowledge base without granting write access, and without trusting a pasteable prompt to hold any line.
- Design: Two layers. The pasted prompt is convenience/UX and is fully attacker-editable. A steward (`gap_steward.py`) plus an independent workflow check (`gap-diff-shape-check.yml`) validate every submission server-side and default-deny. The prompt's rules are MIRRORED in the steward, not trusted from the prompt.
- Got right: Treating the prompt as untrusted from the start. The steward default-denies — e.g. auto may append only to a gap whose declared type is provably in the allow-set; an unknown/blank type is rejected — so editing or ignoring the prompt cannot widen what actually lands.
- Where/why it failed: The recurring failure mode was mine, not the system's: repeatedly catching myself about to encode a real guarantee in prompt text ("the prompt says never close a gap") and believing it would hold. A pasted prompt is one edit or one ignored line away from gone.
- Fix: For every rule, ask "does this matter for safety/integrity?" If yes, it lives in steward code with a test, and the prompt only describes it. Accept the real cost: load-bearing rules now exist in BOTH the prompt (UX) and the steward (enforcement) and can drift — that duplication is the price of not trusting the prompt.
- Why this fix: A prompt the user pastes is a UI, not a control surface. Anyone can change a word or skip a line, so any constraint that only lives there is advisory.
- Rule of thumb: A prompt is not a trust boundary. Put every load-bearing constraint in server-side code that runs regardless of what the prompt says, default-deny there, and use the prompt only to make the well-behaved path easy — never to prevent the misbehaved one.
- Provenance (verified/assumed): Verified first-hand — the steward's allow-lists and default-deny rules are enforced in code with an adversarial suite (117 tests) this session, independent of any prompt text.
- Link: this session; collective `gap_steward.py` + `.github/workflows/gap-diff-shape-check.yml`
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E1 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-07-17 · projects/pappydapimp69__garden.md#E1 · compatible · no sandbox · this session (Garden audit + fix); `SCHEMA.sql` (global_action_log, sanitize_global_action_log trigger), `src/data/actionsLog.js`
- Cited-by: 2026-07-17 · projects/pappydapimp69__garden.md#E2 · compatible · no sandbox · this session (Garden audit); `supabase/functions/vision-proxy/index.ts`, `src/vision/client.js` (`_callProxy`, `payload`)
- Cited-by: 2026-07-17 · projects/pappydapimp69__garden.md#E3 · compatible · no sandbox · this session (Garden audit); `supabase/functions/vision-proxy/index.ts`, `SCHEMA.sql` (vision_api_calls)
- Cited-by: 2026-10-09 · projects/local__sandbox-edges.md#E52 · compatible · sandboxes/2026-10-09__allowlist-from-probe-beats-deny-list.py · observed RESULT: PASS deny-list leaks 10/16 dead uses, hand allowlist blocks 4 working uses, probe-derived allowlist 0/0; drift leaks allow=2 deny=12 probe=0; directive 1/4->4/4; once-per-block break: single-use probe leaks 3, two-use probe 0. (Unp… · brain train auto pass 2 (edge: collective + pocketzane); session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-14 · modeled · The entry has no stored sandbox, so there was nothing to rerun; its only evidence is the author's statement that the steward's allow-lists and default-deny rules are exercised by an adversarial suite of 117 tests, in a repository not available to this audit. The Rule of thumb (a prompt is not a trust boundary, enforce in server-side code and default-deny) is a design principle that the described architecture does follow, and nothing in the entry assumes its own answer. But it covers a real system (a GitHub-side steward and workflow check) whose enforcement I could not exercise, and the claimed cost, drift between the prompt copy and the steward copy of each rule, is asserted rather than measured. I therefore judge it modeled: the design argument holds, the test results are unverified here, and no adversarial submission was replayed against the real steward. · scheduled brain train auto loop 2 pass 3, audit session 2026-10-14; session_015r1XigkmG22M1a2ZeANy7S

## E4 — never round up a persistence state
- Date: 2026-07-11
- Project: pappydapimp69/collective
- Tags: [process][github][agent]
- What: A completed training loop was reported as "saved in Collective" when only a chat draft (and at most an open issue / PR) existed — the file had not landed on `main`. "Filed," "saved," and "recorded" were being used interchangeably.
- Why built: The pipeline turns a session's finding into a GitHub issue → mechanically validated PR → human-merged gap file on `main`.
- Design: The original flow closed the source issue as soon as a PR opened, and the agent narrated success at that point.
- Got right: The pipeline stages themselves were fine; the defect was purely in what "done" was claimed to mean.
- Where/why it failed: Opening an issue or a PR is a REQUEST to persist, not persistence. Claiming "saved" there is a false success — the merge can still be declined, and nothing is on `main`. There was no machine check tying the success claim to the actual landed file, so the claim could outrun reality.
- Fix: Define four explicit states — drafted / submitted / pending-review / recorded — and forbid rounding up. Keep the source issue OPEN until a post-merge workflow re-checks out `main`, confirms the exact file plus a per-session sha256 source-fingerprint marker are present, and only THEN marks it recorded and closes the issue. The agent reports the state it is actually in.
- Why this fix: Success should be VERIFIED against ground truth (the file on `main`), not asserted from an intermediate step. A fingerprint the verifier re-checks makes "recorded" unfakeable by any upstream stage.
- Rule of thumb: Never round up a persistence/commit state. "Submitted" ≠ "merged" ≠ "recorded." When an agent (or a human) reports something as saved, tie the claim to a check against the real destination, and keep the request open until that check passes.
- Provenance (verified/assumed): Verified first-hand — built the four-state model + the post-merge verify workflow this session; the verifier greps the fingerprint marker on `main` before closing the issue.
- Link: this session; collective `.github/workflows/gap-persistence-verify.yml` + `TRAINING_MODE.md`

## E3 — github actions heredoc injection untrusted body
- Date: 2026-07-11
- Project: pappydapimp69/collective
- Tags: [security][github][ci]
- What: A GitHub Actions workflow parsed an issue body by interpolating `${{ github.event.issue.body }}` directly into a `run:` shell heredoc — a shell-injection vector, since the issue body is attacker-controlled public input.
- Why built: The intake workflow reads the submitter's issue body to validate it and file the gap.
- Design: The original step embedded the body inline in the shell script (heredoc / command-substitution context).
- Got right: The downstream validation logic was sound; the hole was entirely in HOW the untrusted text reached it.
- Where/why it failed: `${{ ... }}` expressions are substituted into the script TEXT before the shell runs, so a body containing backticks, `$(...)`, or the heredoc sentinel is executed, not treated as data. It is a well-known Actions footgun that is easy to reintroduce because the happy path looks fine.
- Fix: Pass untrusted event data through the environment and write it with `printf %s` — `env: ISSUE_BODY: ${{ github.event.issue.body }}`, then `printf '%s' "$ISSUE_BODY" > body.txt`. An env value is data, never expanded as script.
- Why this fix: The only robust boundary is keeping attacker text out of the script text entirely; env var + `printf %s` guarantees it is inert bytes regardless of contents.
- Rule of thumb: Never interpolate `${{ github.event.* }}` (issue/PR body, title, comment) into a `run:` block. Route every webhook-supplied field through `env:` and consume it with `printf %s` / `"$VAR"` — treat any such field as executable if inlined.
- Provenance (verified/assumed): Verified first-hand — fixed both the gap and entry intake workflows this session; the env + `printf %s` pattern is in `gap-intake.yml`'s "Write issue body to file" step.
- Link: this session; collective `.github/workflows/gap-intake.yml`
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E9 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-10 · projects/pappydapimp69__brain.md#E123 · incompatible · sandboxes/2026-10-10__boundary-by-construction-vs-classification-evasion-and-capability-cost.py · observed RESULT: FAIL evasion D1 96 D2 84 D3len 26 D3str 18 of 108; leaks fence 2 fixed-nonce 1 quote 5 nonce 0 json 0; rules effective placement 0/20 typed G0 10 G1 14 G2 17; misses 2/16. The two misses are the strict-detector rule delivery (1/20… · session_01YFLLRpDsfZpRstb2KT2MQy

## E2 — gate agent autonomy on signal type not proxy
- Date: 2026-07-11
- Project: pappydapimp69/collective
- Tags: [process][agent][design]
- What: An "auto" (self-driven, human-supervised) training mode was first restricted to fact-lookup gaps only, and banned from building artifacts. That both under-powered it and drew the safety line in the wrong place.
- Why built: Auto lets the system mine a knowledge gap end-to-end with a human watching but not steering each round — the highest-throughput mode.
- Design: v1 rule — auto may only work `fact-lookup` gaps, no artifacts; rationale was "a machine shouldn't judge its own work."
- Got right: The instinct that auto shouldn't settle EVERYTHING was correct — some gaps genuinely need a human.
- Where/why it failed: "fact-lookup only" is a proxy, and a proxy both over- and under-restricts. The real seam is the SIGNAL that settles a gap: objective (an external source, or a built artifact that demonstrably works or doesn't) vs subjective (how something lands on a person). Auto can settle objective gaps under supervision — including `fit` gaps, where the artifact IS the evidence. It cannot settle a `reaction` gap, whose only signal is a real person's in-the-moment reaction. Banning `fit` lost real capability (a fact is often best shown with a built thing); the actual risk was confined to `reaction`.
- Fix: Gate auto on signal type — allow `fact-lookup` and `fit` (build the artifact, judge it objectively), forbid `reaction`. Enforced with `AUTO_ALLOWED_GAP_TYPES = {fact-lookup, fit}` and default-deny on anything else.
- Why this fix: The limit now matches the true invariant (is the settling signal objective and machine-checkable?) rather than a category that merely correlates with it.
- Rule of thumb: When limiting an autonomous agent's scope, gate on the underlying property that actually makes a task safe/decidable (here: objective vs human-only signal), not a proxy category — a proxy both blocks safe work and can let unsafe work slip through where the correlation breaks.
- Provenance (verified/assumed): Verified first-hand — shipped the objective/subjective gating in `gap_steward.py` with tests this session; both the wrong v1 (fact-lookup-only) and the corrected rule are in the branch history.
- Link: this session; collective `gap_steward.py` (`AUTO_ALLOWED_GAP_TYPES`)
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E42 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E1 — anonymous github fetch build to weakest primitive
- Date: 2026-07-11
- Project: pappydapimp69/collective
- Tags: [process][github][llm]
- What: A public training prompt kept "failing to read the repo" in different ways across several sessions — truncated fetches, wrong owner casing, unfollowable templated URLs, and finally "can't list the gaps directory." Each was patched as its own surface bug, over hours, before the shared root cause was found.
- Why built: The prompt hands an LLM URLs to fetch Collective's data (canon snapshots, the gaps folder, the submission form) so a training session can see prior coverage and continue an existing gap.
- Design: It pointed the model at the GitHub contents API (`.../contents/gaps`) to LIST the gaps directory, and at `github.com/tree` / templated `.../main/<path>` URLs elsewhere.
- Got right: Once the actual capability was probed, the fix was small and durable — a generated flat index file fetched by one raw URL.
- Where/why it failed: Nobody had tested what an ANONYMOUS client — which is exactly what a public LLM's fetch tool is — can actually retrieve. One `curl` of each URL type settles it: the contents API returns **403** to anonymous/rate-limited callers, `github.com/tree` HTML is robots-blocked for crawlers, and only `raw.githubusercontent.com/<complete-file-path>` returns **200**. A directory has no raw URL, so "list the folder" had no working primitive at all. The separate surface bugs (casing, templated URLs, truncation, listing) were one root cause wearing four masks: building on a fetch capability that was never verified against the real caller.
- Fix: Probe the three URL types once with `curl`; confirm only raw file URLs work. Maintain a generated `gaps/INDEX.md` (built from the gap files, kept current by a workflow) and hand the model its single raw URL; degrade to "create a new gap" if even that misses.
- Why this fix: An LLM integration can only rely on the WEAKEST reliable fetch primitive. For anonymous GitHub that is a complete raw file URL — not the API, not HTML tree pages, not constructed or relative URLs.
- Rule of thumb: Before building an interface on top of an external capability, spend one probe confirming the exact capability exists for the REAL caller (here: an unauthenticated fetch). When several surface failures share a medium, suspect one unverified primitive underneath and test it before patching each symptom — reactive symptom-fixing multiplies the cost. Build to the weakest reliable primitive. (An extension of "instrument the lowest-level primitive first" to third-party/external capabilities.)
- Provenance (verified/assumed): Verified first-hand — ran the curls this session (contents API 403, tree 200 but robots-blocked for crawlers, raw 200), then shipped the index generator + workflow and confirmed the raw `INDEX.md` returns 200 on main.
- Link: this session; collective PRs adding the gap index + `.github/workflows/gap-index.yml`
- Cited-by: 2026-09-29 · projects/local__sandbox-edges.md#E10 · compatible · no sandbox · session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-14 · projects/pappydapimp69__brain.md#E40 · compatible · no sandbox · Brain install.sh; session 2026-09-14
