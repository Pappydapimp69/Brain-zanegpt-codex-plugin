# local/sandbox-kernel-system-cutscene — lessons

Project: local/sandbox-kernel-system-cutscene. Newest first.

---

## E3 — skip parity breaks on time compared skips wallclock payloads and cosmetic dispatch
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-cutscene
- Tags: [cutscene][determinism][testing][state]
- What: Applied the ideas kernel that a cutscene built as command markers dispatched through the gameplay reducer makes watch and skip end on byte-identical state, provable by hashing both. Parity held for the design the kernel describes, and the sandbox measured three small deviations that each break it.
- Why built: brain train gap listed the kernel as unapplied. It came from The Recursion; no memory entry exercised the parity test.
- Design: 500 seeded scenes of 8 markers on a 10 ms grid within 3 s, played with frame deltas of 10 to 40 ms, watched to the end or skipped at a seeded time on the same grid, final states hashed. Four designs: a fired-pointer skip that dispatches markers[ptr:], a skip that re-selects markers with at >= skip time, commands that carry the wall-clock time they fired, and a camera track that dispatches one command when it reaches a point at 1.5 s.
- Got right: Keeping skip times on the same grid as marker times, so a skip can land exactly on a marker.
- Where/why it failed: The pointer design differed in 0 of 500 scenes. Selecting by at >= skip time differed in 14, each a skip landing exactly on a marker that had already fired and fired again. Wall-clock payloads differed in 431. The camera-dispatched command differed in 226, whenever the skip came before the camera reached its point.
- Fix: Skip by the fired pointer, never by re-comparing times; keep command payloads free of playback time; and let cosmetic tracks dispatch nothing. Run the watch-versus-skip hash test with skip times that land exactly on marker times.
- Why this fix: Parity holds only while the sim sees the same commands in the same order on both paths. Each deviation adds a command, a payload or an extra dispatch that exists on only one path.
- Rule of thumb: Watch-versus-skip cutscene parity held in 500 of 500 scenes only for a pointer-based skip; re-selecting markers by at >= skip time double-fired a marker in 14 scenes, wall-clock payloads broke 431, and one command dispatched by a camera track broke 226, so skip by pointer, keep playback time out of payloads, and never dispatch from cosmetic tracks.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b07.py loop 33 in Pappydapimp69/Brain, deterministic seeded scenes. Observed hash mismatches: 0, 14, 431 and 226 of 500 for the four designs.
- Composed: ideas:SYSTEM/cutscene/cmd-marker-timeline/watch-skip-provable-parity
- Link: session 2026-09-28, brain train gap batch 7 loop 33
- Sandbox: sandboxes/2026-09-28__train-gap-b07.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E2 — relative cutscene beats need start values baked at load
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-cutscene
- Tags: [cutscene][timeline][animation][state]
- What: Applied the ideas kernel that cosmetic cutscene tracks should be pure functions of elapsed time, so any timestamp evaluates directly without replay, while a naive seek that stomps elapsed time on a sequential runner returns the wrong state. Both reproduced with costs, and purity breaks for beats authored relative to where the previous beat ended unless their start values are baked.
- Why built: brain train gap listed the kernel as unapplied. draft/E7 established pure functions of elapsed time for scrubbing; nobody had checked beats whose start depends on the previous beat.
- Design: Cutscenes of 3, 30 and 300 eased beats with seeded durations and targets, 200 random seeks each. Compared a naive stomp (keep the live runner's beat, overwrite elapsed), reset-and-replay (counting beats crossed), and direct evaluation by a counted binary search over beat start times. Then 30 beats of which 13 move relative to where the previous beat left off, evaluated directly either using the previous beat's authored target as the start, or using start values accumulated once at load.
- Got right: Adding relative beats. With absolute targets only, direct evaluation is trivially exact and the purity claim looks unconditional.
- Where/why it failed: The naive stomp was wrong on 118, 191 and 200 of 200 seeks at 3, 30 and 300 beats. Reset-and-replay was correct but crossed 1.0, 13.3 and 154.1 beats per seek; binary search took 2.0, 5.0 and 8.3 probes and was wrong on 0. With 13 relative beats, direct evaluation that took the previous beat's authored target as its start was wrong on 89 of 200 seeks; with start values accumulated at load it was wrong on 0.
- Fix: When a track has relative beats, resolve every beat's absolute start value once at load and store it beside the beat, so state(t) stays a lookup plus an ease.
- Why this fix: A relative beat's start is the sum of everything before it, which is history. Baking that sum at load moves the history dependence out of the per-seek path.
- Rule of thumb: A pure state(t) cutscene track seeks correctly in O(log N) (8.3 probes for 300 beats vs 154.1 beats replayed; a naive stomp was wrong 200/200) only if every beat's start is absolute: with 13 of 30 beats relative to the previous beat's end, direct evaluation was wrong on 89/200 seeks until start values were baked at load (0/200).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b07.py loop 32 in Pappydapimp69/Brain, deterministic. Observed: stomp 118/191/200 wrong; replay 1.0/13.3/154.1 beats; binary search 2.0/5.0/8.3 probes, 0 wrong; relative beats 89/200 unbaked and 0/200 baked.
- Composed: ideas:SYSTEM/cutscene/cosmetic-tracks-as-pure-functions-of-elapsed-time/direct-eval-at-any-timestamp-not-replay-dependent, draft/E7
- Link: session 2026-09-28, brain train gap batch 7 loop 32
- Sandbox: sandboxes/2026-09-28__train-gap-b07.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

## E1 — seek must fold marker state and pick a landing convention
- Date: 2026-09-28
- Project: local/sandbox-kernel-system-cutscene
- Tags: [cutscene][timeline][state][animation]
- What: Applied the ideas kernel that a timeline seek must resolve position without firing the markers it passes. The rule held, and a seek that only relocates the pointer leaves any state set by a marker wrong; a seek landing exactly on a marker also needs an explicit convention.
- Why built: brain train gap listed the kernel as unapplied. animation/E1 covered pausing on seek, not what a seek does to marker-set state.
- Design: A 30 s timeline with 14 seeded markers, each either a fire-only effect or a state setter (say, lighting). Playback advance fires markers it crosses. Three seeks over 60 seeded scrub targets: fast-forward by repeated advance, pointer lookup only, and lookup plus a fold that rebuilds state from state markers at or before the target without firing anything. Then a chapter-select jump to each effect marker's exact time, resolved with bisect_right and with bisect_left, followed by 0.5 s of playback.
- Got right: Checking state after each seek, not only the fire log. Lookup-only passes the kernel's own test (0 fires) and is still wrong.
- Where/why it failed: Fast-forward fired 383 markers during 60 scrubs. Lookup-only fired 0, but state was wrong after 54 of 60 seeks, because nothing re-applied the state markers it jumped over. Lookup plus fold fired 0 and had 0 wrong states. On chapter jumps to a marker's exact time, bisect_right counted the marker as passed and its cue played on resume 0 of 7 times; bisect_left left it pending and it played 7 of 7.
- Fix: Make seek do two things: relocate the pointer by lookup, and rebuild persistent state from state markers without firing effects. Decide explicitly whether a seek landing on a marker's exact time plays its cue on resume; chapter select usually wants bisect_left so the chapter opens with its cue.
- Why this fix: A marker can both fire an effect and set state. Seek must drop the first and keep the second. Chapter select lands exactly on marker times every time, so the landing convention is always exercised.
- Rule of thumb: A seek that only relocates the pointer fires nothing (vs 383 fires for fast-forward over 60 scrubs) but leaves marker-set state wrong (54 of 60 seeks), so rebuild state from state markers without firing effects; and pick the exact-landing rule on purpose, since chapter select always lands on a marker time (bisect_right: its cue plays 0 of 7, bisect_left: 7 of 7).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b03.py loop 15 in Pappydapimp69/Brain, deterministic. Observed: fires 383/0/0 and wrong states 0/54/0 for fast-forward, lookup and lookup plus fold; chapter-jump cues 0/7 with bisect_right and 7/7 with bisect_left. The timeline is a model, not the Lamplighter player.
- Composed: ideas:SYSTEM/cutscene/seek-resolves-position-never-executes-transit/a-scrub-target-is-a-lookup-not-a-fast-forward, animation/E1
- Link: session 2026-09-28, brain train gap batch 3 loop 15
- Sandbox: sandboxes/2026-09-28__train-gap-b03.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)

