# pappydapimp69/chronicles — lessons

Project: pappydapimp69/chronicles. Newest first.

---

## E1 — chronicles state atomicity
- Date: 2026-07-05
- Project: pappydapimp69/chronicles
- Tags: [coop][state][gamedev]
- What: Share-code import must replace state atomically, not merge piecemeal
- Why built: Cross-device co-op RPG using compressed share codes as the only sync mechanism — no server, no websockets, state travels as a base64 string pasted between devices
- Design: `shareCode.import(code)` decodes → validates schema version → replaces entire game state object in one assignment → re-derives active screen from `meta.phase` + `meta.activeTurn` + device-local `playerIdentity`
- Got right: Identified early that partial merges (e.g. updating only adventure.scenes while keeping stale player profiles) would desync the two devices silently
- Where/why it failed: N/A — constraint established at design time from prior lesson (pappydapimp69__test.md#E8: replacing source-of-truth objects requires rebuilding ALL derived state through one path)
- Fix: Single atomic replacement + full screen re-derivation. Device-local fields (apiKey, playerIdentity) are never in the share code and never overwritten.
- Why this fix: Two sources of truth (local state + imported state) that are "merged" will eventually disagree on which fields are authoritative. One object wins entirely; local-only fields live in a separate namespace.
- Rule of thumb: When two devices share state via a payload, the payload IS the state — import means replace, not merge.
- Provenance (verified/assumed): Assumed from prior E8 lesson; not yet verified in running code (game not yet implemented)
- Link: https://claude.ai/code/session_012KNCvEWeDx6jHCwjAZmoCJ
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E286 · compatible · sandboxes/2026-10-15__sharecode-replace-vs-merge-rng-timer-state.py · observed RESULT: PASS replace import matches reference 1/1, merge with a stale gate timer diverges, merge only works when timer coincides, unencoded alias moves, encoded copy is stable · brain train auto session pass 2; session_0147KUptpmmgHdXXTSmtxr1C
