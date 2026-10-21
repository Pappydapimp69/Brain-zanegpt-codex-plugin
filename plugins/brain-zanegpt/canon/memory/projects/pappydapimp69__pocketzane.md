# pappydapimp69/pocketzane — lessons

Project: ElevenLabs Studio Label Voice Assigner — a Tampermonkey userscript
(`elevenlabs-voice-assign.user.js`) that pastes labeled, header-mapped text into
ElevenLabs Studio, strips labels, inserts clean text, and bulk-assigns voices per
role via synthetic multi-select + the voice picker. Newest first.

---

## E6 — Accent styling silently stopped applying after the first paragraph
- Tags: [tts][voice][prompt-engineering]
- Date: 2026-06-14
- What: The bracket-tag protocol that drives Zane's exaggerated Japanese-accent "bits" in the TTS scripts.
- Why built: To make the text-to-speech engine reliably switch into the accent for a bit and reliably
  return to the normal host voice, across a multi-paragraph script.
- Design: An accent bit is opened with `[thick exaggerated Japanese accent] … [normal voice]`, one tag
  per bracket, and the accent tag is re-declared at the start of every paragraph that needs it.
- Got right: One-tag-per-bracket plus an explicit `[normal voice]` exit kept the accent from bleeding
  into surrounding host dialogue; the convention generalized cleanly across all eight scripts.
- Where/why it failed: A single accent tag placed once at the top stopped applying after the first
  paragraph — the engine resets voice/style state at paragraph boundaries, so later paragraphs silently
  reverted to the default voice with no visible error in the script.
- Fix: Re-declare the accent tag in every paragraph that should carry it, and close each bit explicitly
  with `[normal voice]`; documented this in `ACCENT_RULES.md`.
- Why this fix: It adapts to the engine's actual per-paragraph state reset rather than assuming styling
  is sticky; an explicit exit tag is more robust than relying on the next tag to override a lingering state.
- Rule of thumb: If a styling directive silently stops applying partway through, assume the renderer
  resets state at block boundaries and re-declare it per block.
- Link: session commit 4e55662 (branch claude/notorious-peepop-transcripts-evf2bj).
- Cited-by: 2026-10-09 · projects/local__sandbox-edges.md#E52 · compatible · sandboxes/2026-10-09__allowlist-from-probe-beats-deny-list.py · observed RESULT: PASS deny-list leaks 10/16 dead uses, hand allowlist blocks 4 working uses, probe-derived allowlist 0/0; drift leaks allow=2 deny=12 probe=0; directive 1/4->4/4; once-per-block break: single-use probe leaks 3, two-use probe 0. (Unp… · brain train auto pass 2 (edge: collective + pocketzane); session_01YFLLRpDsfZpRstb2KT2MQy

## E5 — TTS engine accepts-but-ignores certain bracket tags (silent no-op)
- Tags: [tts][voice][prompt-engineering]
- Date: 2026-06-14
- What: A maintained "dead-tags" list of bracket emotion/style tags the TTS engine accepts but does
  not act on (e.g. `[building]`).
- Why built: To stop authors from spending tags that produce no audible change and to constrain scripts
  to directives that actually work.
- Design: Scripts draw only from a known-good set of emotional-state tags; tags found to have no effect
  are catalogued as "dead" in `ACCENT_RULES.md` and avoided everywhere.
- Got right: Centralizing the deadlist in the shared ruleset meant every script reused the same guard
  instead of each rediscovering the same dud tags.
- Where/why it failed: Certain plausible-looking tags (e.g. `[building]`) are parsed without error but
  produce no change in the audio — a silent no-op that looks correct on the page and only reveals itself
  on listen-back.
- Fix: Catalogue the ineffective tags as "dead" and exclude them, preferring the validated set; while
  drafting Segment 2 this caught a would-be `[building]` cue before it shipped.
- Why this fix: A silent no-op cannot be caught by reading the script, so an explicit deny-list is the
  only durable safeguard.
- Rule of thumb: When a system silently accepts-but-ignores some inputs, keep an explicit allow/deny
  list — silent no-ops never surface themselves.
- Link: session commit faa473a (`personas/ACCENT_RULES.md`).
- Cited-by: 2026-10-09 · projects/local__sandbox-edges.md#E52 · compatible · sandboxes/2026-10-09__allowlist-from-probe-beats-deny-list.py · observed RESULT: PASS deny-list leaks 10/16 dead uses, hand allowlist blocks 4 working uses, probe-derived allowlist 0/0; drift leaks allow=2 deny=12 probe=0; directive 1/4->4/4; once-per-block break: single-use probe leaks 3, two-use probe 0. (Unp… · brain train auto pass 2 (edge: collective + pocketzane); session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E54 · compatible · sandboxes/2026-10-10__per-utterance-rows-stable-ids-vs-flat-manuscript.py · observed RESULT: PASS edit one row: rows 1 vs flat 7/8 chunks; insert: index-named 21 vs stable-id 1; inline-label parser wrong 3; alias voices 2 vs 1; overlap lost. Miss: my first absolute guess of 10 chunks was impossible with 8 chunks. · brain train auto session 2026-10-10; session_012uwXvPE6LveBmBN1pFKYfK
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E256 · compatible · sandboxes/2026-10-14__wpm-estimate-filters-but-duration-cannot-see-a-dropped-emphasis-tag.py · observed RESULT: PASS missed_plain=2 missed_padded=0 err_range=(-0.21,0.20) break_drop_caught=6/6 emph_drop_caught_by_duration_5pct=0/3 at_2pct=3/3 by_tag_check=3/3 · brain train auto loop 2 pass 5; session_015vYTjNJNEjDvnZgWaJaTSv
- Audited: 2026-10-14 · modeled · Read the entry and found no stored sandbox: the claim (a real TTS engine parses certain bracket tags without error but changes nothing audible) rests on listen-back by the author, not on a computed result, so question 1 has no model to judge and question 2 cannot be confirmed. The claim is about a real external system, and the only thing tested was the author's ear on specific tags such as the building tag; the general rule (keep an explicit allow or deny list for silent no-ops) is sound and is supported by a later cited sandbox that compared deny-list, hand allowlist and probe-derived allowlist leaks, but that sandbox models the list mechanics and never touches the engine. So the entry is credible but unverified against the engine itself, which fits modeled rather than pass; a reproducible check would need an audio-diff probe of each tag against the real engine. · brain train auto scheduled run, loop 1 pass 3; session_013UbxUV5wii3FwAXCPW9kkg

## E4 — Silent failure hid the root cause
- Tags: [process][observability]
- What: First versions of the assignment flow.
- Why built: Drive the editor/picker via synthetic events.
- Design: v0.1 ran the click/picker pipeline with no error handling.
- Got right: Pipeline structure (parse → insert → resolve → assign → verify); parser/planner.
- Where/why it failed: A throw in the first synthetic click (E1) vanished silently, so
  symptoms ("picker didn't open") pointed at the wrong layers for two iterations.
- Fix: Added try/catch/finally + a structured debug report/log (v0.2), surfacing the real stack.
- Why this fix: Observability turns an invisible failure into a precise diagnosis (and doubles
  as the self-grading mechanism).
- Rule of thumb: Instrument first; verify the lowest-level primitive before theorizing upward.
- Cited-by: 2026-10-09 · projects/local__sandbox-edges.md#E52 · compatible · sandboxes/2026-10-09__allowlist-from-probe-beats-deny-list.py · observed RESULT: PASS deny-list leaks 10/16 dead uses, hand allowlist blocks 4 working uses, probe-derived allowlist 0/0; drift leaks allow=2 deny=12 probe=0; directive 1/4->4/4; once-per-block break: single-use probe leaks 3, two-use probe 0. (Unp… · brain train auto pass 2 (edge: collective + pocketzane); session_01YFLLRpDsfZpRstb2KT2MQy

## E3 — Editor "clear" left stale nodes → plan/node misalignment
- Tags: [editor][prosemirror]
- What: Inserting clean text before assigning voices.
- Why built: One TTS node per paragraph, aligned to a per-paragraph voice plan.
- Design: focus → `execCommand('selectAll'+'delete')` → synthetic paste → map plan[i]→nodes[i].
- Got right: Synthetic paste reused Studio's own paragraph splitting; pasted counts matched plan.
- Where/why it failed: The clear left N default nodes at the front, so pasted nodes started at
  index N and every plan[i]→nodes[i] mapping shifted by N.
- Fix: Align assignment + verification to the TRAILING planLength nodes; retry the clear.
- Why this fix: Freshly pasted nodes are always last; trailing-alignment is robust to leftover
  leading nodes without needing a perfect clear.
- Rule of thumb: Never assume a rich-text "clear" emptied the editor; align by position and verify counts.

## E2 — Picker detected by existence, not visibility
- Tags: [browser][radix][popover]
- What: Opening the voice picker to scrape/click voice rows.
- Why built: Assign a voice to a multi-selected group of nodes.
- Design: Record all matching containers before clicking the indicator, then accept any "new" one.
- Got right: Indicator selector and click target were correct.
- Where/why it failed: The picker (Radix popover) is pre-rendered hidden and merely toggled
  visible, so it was already in the "known" set and filtered out as not-new → looked unopened.
- Fix: Snapshot the set of *visible* containers before the click; accept any that become visible after.
- Why this fix: For popover frameworks the meaningful event is a visibility transition, not insertion.
- Rule of thumb: Detect popovers/menus by visibility change, not by node creation.
- Cited-by: 2026-10-15 · projects/pappydapimp69__brain-creative-training.md#E34 · compatible · sandboxes/2026-10-15__stream-tap-survives-redesign-until-schema-or-pause-breaks-it.py · observed RESULT: PASS redesign: scraper 0% vs stream tap 100%; schema rename: tap 0% reported 'stream-ended' (strict: error:unknown-type:audio_chunk); silence 400 ms on a 600 ms pause keeps 50%, safe from 700 ms; sleep 1000 fails 3/6; hidden pre-re… · https://claude.ai/code/session_01E8b6CeJT8Lb9myTqhRx1qr creative-arts round 2 loop 5 pass 1

## E1 — Synthetic events crash under a Tampermonkey @grant sandbox
- Tags: [browser][tampermonkey][events]
- What: `realClick`, the synthetic pointer/mouse click for node selection + picker interaction.
- Why built: Drive ProseMirror multi-select + the voice control like a real user.
- Design: One options object with `view: window`, dispatch pointerdown/mousedown/pointerup/mouseup/click.
- Got right: The event sequence and ctrl/meta modifiers were the right approach.
- Where/why it failed: With `@grant` (GM_setClipboard) the script is sandboxed and `window` is
  Tampermonkey's wrapper. Chrome's PointerEvent constructor rejects it: "Failed to read the
  'view' property from 'UIEventInit': Failed to convert value to 'Window'." The first event threw,
  so no click ever landed — every downstream symptom traced here.
- Fix: `@grant unsafeWindow`; `REAL_WINDOW = unsafeWindow || document.defaultView || window` used
  as `view`; a `mkEvent` helper retries construction without `view` if it still throws.
- Why this fix: The real Window is what the constructor requires; the fallback makes the click
  sequence crash-proof against this class of error.
- Rule of thumb: In a sandboxed userscript, never pass the sandbox `window` as an event `view`;
  use the real Window — and verify a click dispatches before blaming selectors.
