# local/sandbox-kernel-play-the-legible-game — lessons

Project: local/sandbox-kernel-play-the-legible-game. Newest first.

---

## E1 — legible bots vs tag reader chain completion
- Date: 2026-10-09
- Project: local/sandbox-kernel-play-the-legible-game
- Tags: [gamedesign][simulation][narrative][testing]
- What: Applied the kernel that playtest bots must see only what the interface shows. A toy relationship game (5 NPCs, 6 days, 4 actions a day, a chain beat needing 3 fresh-beat trust steps with one NPC) was played by a tag-reading bot and by legible bots with attachment, a bedtime and late self-interest keyed to a visible mood meter.
- Why built: brain train kernel listed play-the-legible-game as unapplied; no memory entry had built against it.
- Design: Seeded LCG, 300 seeds per cell. Beat selection is the staged selector from sandbox-kernel-system-narrative/E1 (specificity, best tension fit, not-recently-shown, tie-break) with the recently-shown stage placed between specificity and fit, or after fit. Trust rises only when the shown beat is not among the NPC's last 3. A text check of the sibling verb-guard kernel ran on a hint line and a help panel that ends in a key-summary line.
- Got right: The tag-reader bot completed the chain in 300 of 300 seeds, the legible bots in 47 percent, so the "looks fine" verdict came entirely from the omniscient policy. Stripping the key-summary line made the verb guard find all 4 undocumented verbs where the unstripped check found 0.
- Where/why it failed: My first version of the game was too easy: legible bots finished 99 percent, hiding the effect, because the fit stage left several beats alive and the recently-shown placement made no difference. Attachment, which the kernel offers as realism, did not raise completion here: 47 percent at 0.5 and 36 percent at 0.8, since returning to the same NPC repeats the same beat once the fit stage has narrowed to one.
- Fix: Make the toy game's scarcity real (budget below the chain's cost) and give the selector a continuous fit stage before judging bots. Report completion per policy, and treat attachment as a parameter to sweep, not a free realism gain.
- Why this fix: The verdict gap only appears when the content is scarce enough that blind knowledge matters; the selector placement only matters when exact fit narrows to one candidate (same finding as E1: 36 percent with the stage after fit against 47 percent between, at attachment 0.8 vs 0.5 respectively and 0.357 vs 0.470 at 0).
- Rule of thumb: Judge reachability with bots limited to interface-visible state: the tag reader scored 100 percent against 47 percent for legible bots here; and sweep attachment, because it lowered completion (47 to 36 percent from 0.5 to 0.8) when the selector rotates beats poorly.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox, deterministic, 300 seeds per cell. The game and beat pool are synthetic, not a real shipped game, and the real MIRAGE prototype's 92 to 12 percent figure was not reproduced.
- Composed: ideas:gamedesign/simulation/play-the-legible-game, ideas:gamedesign/discoverability/assert-every-bound-verb-is-explained, sandbox-kernel-system-narrative/E1
- Sandbox: sandboxes/2026-10-09__legible-bots-vs-tag-reader-chain-completion.py
- Prediction: Before the first run: tag bot near 100 percent, legible bots well below half, attachment raising completion, and the verb guard failing only after stripping the key line.
- Observed: RESULT: PASS tag-bot 1.00 vs legible 0.467 (attach0.5,lru between); lru-after attach.8 0.327; naive verb guard misses 0, stripped 4. Attachment prediction was wrong (completion fell). First, easier game version gave 0.993 and was discarded.
- Scenarios: S1 tag bot; S2 tag bot with other selector order; S3 legible bots at attachment 0, 0.5, 0.8 under two selector orders (built to break the attachment-helps assumption); S4 no bedtime limit; S5 verb guard with and without the key-line strip.
- Link: https://claude.ai/code/session_01GfAHwy3Bruhswzp52FBWqr

