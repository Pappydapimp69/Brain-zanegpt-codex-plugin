# local/sandbox-edges — lessons

Project: local/sandbox-edges. Newest first.

---

## E54 — overflow check every state needs measured width not avg char estimate
- Date: 2026-10-11
- Project: local/sandbox-edges
- Tags: [browser][rendering][testing]
- What: Composed the every-state overflow check with the average-character-width estimate: over 12 five-message sequences (60 states, 14 true overflows at a 200 px bar), checking only the final state missed 11 of 14, and checking every state with an average-width estimate missed 5 and raised 9 false alarms, while every-state measured width gave 0 and 0.
- Why built: brain train edge paired the transient-overflow lesson with the width-estimation lesson; the question was whether sampling every state is enough or the per-state measurement must also be real.
- Design: Python model with an assumed Arial-like per-glyph width table, one overwritten status slot, four checkers (final-only measured, every-state measured, every-state average estimate, average estimate with 20 percent slack) scored against measured truth.
- Got right: Every-state measured width matched truth exactly (0 missed, 0 false), and final-only was wrong in the way the transient lesson predicts.
- Where/why it failed: The average estimate was two-sided: narrow-heavy text raised false alarms and the wide-heavy 18-character string was missed, and adding 20 percent slack removed none of the 5 misses while raising false alarms from 9 to 13. My first run had no wide-heavy long string and showed 0 misses, which hid the miss side until I added one.
- Fix: Run the overflow check on every intermediate state and compute each width from the real text measurement of that exact string, not from characters times an average.
- Why this fix: Sampling more states fixes which states are checked, measuring fixes how each is judged; the sandbox shows slack on a bad estimator only trades misses for false alarms.
- Rule of thumb: An overflow check on overwritten content needs both every intermediate state and a measured width per state; in this model final-only missed 11 of 14 and an average-width estimate with slack still missed 5.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; glyph widths and message pool are assumed and small, so counts are illustrative while the two-sided error and the slack effect are the finding.
- Composed: sandbox-edges/E37, sandbox-typography-measure/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__overflow-check-every-state-needs-measured-width-not-avg-char-estimate.py
- Prediction: Final-only misses most overflow states; the average estimate misses some wide-heavy strings and flags some narrow-heavy ones; slack does not remove the misses; every-state measured is exact.
- Observed: RESULT: PASS of 14 overflow states final-only missed 11; every-state avg estimate missed 5 + 9 false alarms; with 20% slack 5 missed + 13 false; measured every-state 0/0
- Scenarios: 1) final-only measured; 2) every-state measured; 3) every-state average estimate (built to BREAK with a wide-heavy 18-character string); 4) average estimate with 20 percent slack
- Link: scheduled brain train session, loop 2 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn
- Audited: 2026-10-11 · modeled · Read the entry and reran its stored sandbox, which reproduces the stated counts. The final-only and average-estimate checkers genuinely compute their answers from the message sequences, so the 11 of 14 final-only misses and the two-sided average-estimate error are real model results. But the every-state measured checker is assigned the truth list directly (says = truth), so its 0 missed and 0 false alarms is built in, not computed, and cannot show that a measured width is right. Measured width and truth also share one assumed glyph table, so the claim about real text measurement in a browser was only tested against a hand-written model with a toy 12-sequence pool; the Rule of thumb states a browser rendering fix, hence modeled rather than pass. · scheduled brain train session; session_018Fx6YUUQMABGNn8Depe7Ek loop 1 pass 3

## E53 — canvas label fit expansion headroom and font reset on resize
- Date: 2026-10-11
- Project: local/sandbox-edges
- Tags: [browser][rendering][testing]
- What: Composed German label expansion with canvas sizing: a box sized to the longest English label (84 px) overflowed 3 of 8 German labels, a flat 30 percent headroom still overflowed 1, and the fit check gave 3 false passes when the canvas width was assigned after the font was set.
- Why built: brain train edge paired the two browser-rendering lessons; the question was whether the expansion headroom rule and the canvas-size lesson stack into a new failure.
- Design: Python model with per-character em widths (assumed, Arial-like), eight real English/German UI label pairs, and a canvas object that resets font to 10 px on width assignment as browsers do.
- Got right: English labels all fit the English box (0 overflow), and sizing to the measured widest German label (factor 1.31) cleared all 8; the width-then-font order gave 0 false passes.
- Where/why it failed: Setting the font first and then the canvas width reset the font to 10 px, so the measurement used the small font and 3 overflowing labels passed the fit check silently. A flat 30 percent headroom, the commonly quoted figure, still overflowed Einstellungen-class labels.
- Fix: Assign canvas width and height first, set the font after, and size boxes from the measured widest translated label rather than a flat percentage.
- Why this fix: The sandbox showed the false passes vanish with the order change alone, and the knee of 1.31 only comes from measuring the actual strings.
- Rule of thumb: Measure localized labels after the canvas is sized and the font is set, against the widest real translation; in this model a flat +30 percent and a font-before-resize order each hid overflow.
- Provenance (verified/assumed): Verified first-hand by running the sandbox; glyph widths are an assumed approximation, so absolute pixel numbers are illustrative and only the ordering and false-pass effect are the finding.
- Composed: sandbox-localization-expansion/E1, sandbox-edges/E7
- Polarity: compatible
- Sandbox: sandboxes/2026-10-11__canvas-label-fit-expansion-headroom-and-font-reset-on-resize.py
- Prediction: A box sized to English overflows at least 1 German label, a flat 30 percent still overflows at least 1, and font-before-width gives at least 1 false pass versus 0 the other order.
- Observed: RESULT: PASS EN box 84px overflows 3 DE labels; flat +30% still 1; knee x1.31; font-reset false passes 3 vs 0
- Scenarios: 1) English-sized box; 2) headroom sweep to the knee (built to BREAK the flat 30 percent rule); 3) font-then-width versus width-then-font measurement order
- Link: scheduled brain train session, loop 1 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn

## E52 — allowlist from probe beats deny list
- Date: 2026-10-09
- Project: local/sandbox-edges
- Tags: [process][prompt-engineering][observability]
- What: Composes collective#E5 (enforce load-bearing rules in code, default-deny) with pocketzane#E5/E6/E4 (a TTS engine silently ignores some tags, resets directive state at block boundaries, and failures need lowest-level instrumentation). A modelled engine with 12 working and 8 accept-but-ignore tags was gated three ways.
- Why built: pocketzane#E5 recommends a hand-kept dead-tags deny-list, while collective#E5 says gates must default-deny; the two advices point in opposite directions, so the pair needed a concrete test of which gate leaks silent no-ops.
- Design: Deterministic engine model, 40-use corpus (each of 20 tags twice across 5 blocks). Policies: hand deny-list of 3 dead tags, hand allowlist of 10 working tags, allowlist derived from a one-canary-per-tag probe. Then engine drift, a directive-coverage check, and a once-per-block tag built to break the probe.
- Got right: The default-deny shape of collective#E5 is right but its list must not be hand-typed. The deny-list leaked 10 of 16 dead uses silently; the hand allowlist leaked 0 but blocked 4 working uses; the probe-derived allowlist leaked 0 and blocked 0. After drift (one tag dies, one starts working) the hand allowlist leaked 2, the deny-list leaked 12 and falsely blocked 2, and the re-run probe leaked 0.
- Where/why it failed: The probe is only as strong as its canary. A once-per-block tag passes a single-use canary, so the probe-derived allowlist still leaked 3 of 6 uses. Also a directive declared once in a 4-block document reached only 1 of 4 blocks (pocketzane#E6), and the hand allowlist went stale under drift (6 working uses blocked).
- Fix: Derive the allowlist from observed effect (render a canary, check the output changed), re-run it on every engine change, and make the canary exercise the same repetition and block pattern as real use (a two-use canary in one block caught the once-per-block tag: 0 leaks, at the cost of blocking it entirely). Re-declare directives per block.
- Why this fix: The probe is the lowest-level primitive (pocketzane#E4) and avoids both hand-list failure modes: the deny-list cannot know unseen dead tags, and the allowlist cannot know newly working ones. Default-deny then makes an unprobed tag inert instead of silent.
- Rule of thumb: For a renderer that can silently ignore input, gate by a default-deny allowlist built from a probe of observed effect, not a hand list in either direction, and shape the canary like real use; in this model that gave 0 silent leaks versus 10 for the deny-list, but only for stateless tags.
- Provenance (verified/assumed): Verified first-hand: every number above comes from the saved sandbox run, which models the engine behaviour deterministically. Engine behaviour is modelled: a real TTS engine was untested, and the model takes the silent-ignore and block-reset behaviours from the pocketzane#E5/E6 records.
- Composed: collective/E5, pocketzane/E5, pocketzane/E6, pocketzane/E4
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__allowlist-from-probe-beats-deny-list.py
- Prediction: Deny-list leaks 10 and falsely blocks 0; hand allowlist leaks 0 and blocks 4; probe allowlist 0 and 0; under drift hand allowlist leaks 2, deny-list leaks 12 (blocks 2), re-run probe 0; directive coverage 1/4 then 4/4; single-use canary leaks 3 of 6 on a once-per-block tag, two-use canary 0.
- Observed: RESULT: PASS deny-list leaks 10/16 dead uses, hand allowlist blocks 4 working uses, probe-derived allowlist 0/0; drift leaks allow=2 deny=12 probe=0; directive 1/4->4/4; once-per-block break: single-use probe leaks 3, two-use probe 0. (Unpredicted: hand allowlist falsely blocked 6 uses after drift.)
- Scenarios: 1) hand deny-list; 2) hand allowlist; 3) probe-derived allowlist; 4) engine drift with stale hand policies; 5) directive declared once vs per block; 6) BREAK: once-per-block tag against single-use and two-use canaries.
- Link: brain train auto pass 2 (edge: collective + pocketzane); session_01YFLLRpDsfZpRstb2KT2MQy

## E51 — quarantine skip plus weak check double blind
- Date: 2026-10-08
- Project: local/sandbox-edges
- Tags: [testing][process][ci]
- What: Composed memory/E10 (a quarantine skip leaves held files unmeasured) with sandbox-edges/E48 (a presence-only check passes a stale value). The two blind spots stack: held files are invisible to the validator, and once released a presence-only check still passes placeholder content, so a clean release can still carry defects.
- Why built: brain train edge picked the sandbox-edges and memory pair by shared tags; E10 and E48 both describe a gate that reports green on something it never really measured.
- Design: Deterministic model of 22 held proposals, no RNG. Every file fails schema (the only recorded hold reason); 4 also have a bad filename and 5 carry a placeholder in a required field. A full check, a presence-only check and a structural pre-check run against the same files before and after release.
- Got right: The model reproduced E10's numbers exactly: 4 filename failures surface only after release. Separating the checks showed the hold block records only the first failing gate, one reason (schema) against three real defect kinds.
- Where/why it failed: Fixing the recorded reason and lifting holds left the weak check green on the 5 placeholder files once names were fixed (0 errors), while the full substance check still reported 5. Clearing a hold therefore does not prove the item is clean when the post-release check is presence-only.
- Fix: Run cheap structural checks on held files before release and report them as informational (the pre-release tally found all 4 name defects). Pair the release gate with a minimum-substance check on required fields, not a presence check.
- Why this fix: The structural pre-check cannot jam the pipeline and turns the hold from a single-reason latch into a tally. The substance check removes the second blind spot, so green after release means measured, not merely non-empty.
- Rule of thumb: In this model the skip hid 4 defects (0 seen while held, 4 after release) and the presence-only check hid 5 more even after release (0 weak vs 5 full errors). Count a held item's known problems as a floor, and require a substance check, not a presence check, at the gate that lifts the hold.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script, deterministic, numbers copied from the run. The defect assignment (4 names, 5 placeholders of 22) is modeled on E10's recorded counts for names; the placeholder count is an assumption.
- Composed: sandbox-edges/E48, memory/E10
- Polarity: compatible
- Sandbox: sandboxes/2026-10-08__quarantine-skip-plus-weak-check-double-blind.py
- Prediction: Skip-validator reports 0 errors on held files; 4 name failures after release; structural pre-check finds all 4; presence-only check passes 5 placeholders that the substance check catches.
- Observed: RESULT: PASS skip hides 4 name defects (0 seen, 4 after release); weak check hides 5 placeholders even after release; pre-release structural tally finds 4. Weak 0 vs full 5 errors; hold reasons recorded: schema only.
- Scenarios: 1) skip-validator on 22 held files; 2) release after fixing only the recorded reason; 3) structural pre-check on held files; 4) BREAK: names fixed, presence-only vs substance check; 5) hold block reason diversity
- Link: session 2026-10-08, brain train auto pass 2 (edge)

## E50 — edge opticon lockstep identical refused push symptom different fixes
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [git][process][tooling]
- What: opticon#E7's squash-merge stale-commit conflict and lockstep#E10's harness-level push block present as the IDENTICAL 'push refused' symptom, but lockstep#E10's own recommended remedy (hand the user a local push script) does nothing for opticon#E7's actual cause — a local push carries the same stale pre-squash commits and hits the same real conflict, confirming the two causes need genuinely different fixes despite the shared symptom.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Diagnosing opticon#E7's real cause (stale pre-squash commits) as if it were lockstep#E10's cause (harness blocking all auth) and applying lockstep#E10's fix would not resolve it; only opticon#E7's own recorded fix (rebase onto base, cherry-pick only new commits) does.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A 'push refused' symptom alone doesn't distinguish an environment-level block (lockstep#E10) from a genuine content conflict from stale commits (opticon#E7) — check for actual overlapping diffs (a SHA/content comparison) before reaching for either fix, since applying the wrong one wastes a cycle without touching the real cause.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both causes' identical symptom text and confirmed lockstep#E10's remedy would not resolve opticon#E7's actual cause.
- Composed: opticon/E7, lockstep/E10
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E49 — edge mirage zanegpt doc path bug is presentation not logic
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [tooling][documentation][testing]
- What: zanegpt#E3's install-doc bug (a static fallback path printed instead of the resolved one) is mirage#E6's own diagnostic pattern applied fresh — the underlying install LOGIC is 100% correct (mirage#E6's 'goal' axis), the bug is entirely in what gets DISPLAYED to the user (mirage#E6's 'on-screen' axis), exactly the split that made 'the AI companions scatter' a visibility bug, not a behavior bug.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The actual install logic succeeded using the correctly-resolved path every time; the path a user would read from the docs and might manually retype never matched it, a pure presentation-layer bug with zero logic-layer fault.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Before treating a 'the docs are wrong' report as a logic bug, apply mirage#E6's own method — measure the underlying goal/logic axis separately from the displayed/presentation axis; zanegpt#E3 is a 100%-correct-logic, 100%-wrong-presentation case, and conflating the two wastes a logic-debugging pass on a doc-generation bug.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the install logic's correctness against the doc-displayed path's mismatch with the real resolved path.
- Composed: mirage/E6, zanegpt/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E48 — edge mirage lockstep missing writer passes a weak non empty check
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][state]
- What: lockstep#E3's finding (a tracked stat needs a writer at its event, not just a reader at display) is a concrete instance of mirage#E2's general weak-assertion shape — a display reading a stale, pre-initialized value passes any 'looks non-empty/plausible' check exactly like mirage#E2's stale-text case, because the missing writer means the reader was never wrong, it was just never fed anything new.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: After an event that should have updated a stat, the display still showed the OLD initialized value; a weak 'is this a plausible positive number' check passed on it anyway, indistinguishable from the correct post-event value without knowing what the correct value should be.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: lockstep#E3's fix (add a writer at the real event) is necessary because no assertion on the READER side can ever catch a missing WRITER — mirage#E2's own fix (assert the specific expected value, not mere presence) still requires knowing what value to expect, which is lockstep#E3's actual gap, not a testing gap alone.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the stale displayed value passing the weak check against the correct post-event value it should have shown.
- Composed: mirage/E2, lockstep/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/local__sandbox-edges.md#E51 · compatible · sandboxes/2026-10-08__quarantine-skip-plus-weak-check-double-blind.py · observed RESULT: PASS skip hides 4 name defects (0 seen, 4 after release); weak check hides 5 placeholders even after release; pre-release structural tally finds 4. Weak 0 vs full 5 errors; hold reasons recorded: schema only. · session 2026-10-08, brain train auto pass 2 (edge)

## E47 — edge gardenviz dog integer accumulator scheduler survives dogs own 04x headless rate
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [determinism][viz][testing]
- What: garden-viz#E9's fixed integer-accumulator reveal scheduler, tested against dog#E2's specific measured headless rAF rate (0.4x wall-clock), holds frame-rate-independent exactly as both source lessons separately claim — the naive overshoot-discarding scheduler diverges sharply (60 vs 24 sprouts) at that exact multiplier, while the fixed scheduler converges (62 vs 62) at native and headless(0.4x) alike.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: At native 60fps vs dog#E2's own measured 0.4x headless rate, the bad scheduler's reveal count dropped from 60 to 24 sprouts over the identical wall-clock window; the fixed scheduler held at 62 for both.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: garden-viz#E9's own fix (drain an integer accumulator on the game's virtual time, per dog#E2's exact prescription 'assert on the game's own clock, never real elapsed seconds') is confirmed to survive dog#E2's specific measured headless slowdown factor, not just a generic frame-rate difference — a useful concrete number for anyone re-verifying either lesson in a headless CI context.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both schedulers' reveal counts at native 60fps and at dog#E2's measured 0.4x headless rate.
- Composed: local/sandbox-combined-garden-viz/E9, dog/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E46 — edge dog answeringdeep safe contains the crash not the partial overwrite
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedev][state][testing]
- What: dog#E4's safe() try/catch correctly stops one subsystem's exception from blanking the whole frame, but doesn't undo whatever that subsystem already wrote to a shared UI slot before throwing — if a second subsystem's call partially overwrites answering-deep#E1's shared slot then fails, safe() leaves the WRONG partial content rendered, not the frame blanked and not the first subsystem's correct content restored.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Without safe(), the frame throws and renders nothing at all; with safe(), the frame renders, but shows the failing subsystem's partial, wrong overwrite of the working subsystem's correct output — a third, worse-to-debug state neither source lesson names on its own.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: safe()'s containment (dog#E4) needs to be paired with answering-deep#E1's compose-not-overwrite discipline for any subsystem that writes to a slot ANOTHER subsystem already wrote this frame — catching the exception prevents a blank frame, it does not restore or protect an earlier, correct write from being clobbered first.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the blank-frame result without safe() and the wrong-but-rendered result with it, same two subsystems.
- Composed: dog/E4, the-game-the-answering-deep/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E45 — edge darkgoblin test ratchet bot passes rung3 smoke test fragile content
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][gamedesign][ai-agents]
- What: test#E1's rung-3 validation-ladder step (a headless smoke playthrough) reports content completable while using dark-goblin#E1's exact argmax-ratchet bot policy — the bot finds the one greedy-optimal path and passes, but a realistic, slightly-suboptimal playstyle gets stuck on the SAME content, meaning the smoke test's PASS only proves the content is completable by one narrow strategy, not robustly completable.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The ratchet-bot's greedy-optimal strategy completed the content (smoke test PASS); an only-slightly-different, entirely plausible strategy failed to complete the identical content — the ladder's rung 3 never distinguished these.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: test#E1's own validation ladder needs dark-goblin#E1's warning applied specifically to its rung-3 bot choice — an argmax/greedy playthrough bot proves ONE path exists, not that the content tolerates ordinary variation in real play; run the smoke test with more than one strategy profile, or the ladder's strongest rung inherits its weakest agent's blind spot.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the ratchet bot's PASS against the realistic strategy's failure on the identical content.
- Composed: dark-goblin/E1, test/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E44 — edge darkgoblin seven own recommended fix is an undisposed context source
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [browser][rendering][testing]
- What: dark-goblin#E6's own recommended fix (rasterise via Image+canvas, bypassing Phaser's SVG loader) creates a new canvas/context resource on every call — called repeatedly with no disposal, it becomes exactly the leak source seven#E2 describes, silently evicting an unrelated, legitimate, earlier-mounted canvas once the browser's context cap is reached.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: 4 undisposed SVG rasterizations (dark-goblin#E6's fix) past a cap of 3 evicted an unrelated game canvas mounted before any of them — that canvas goes black with no error, a delayed symptom from a fix applied to a completely different subsystem.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A workaround that creates a new browser resource per call (dark-goblin#E6's canvas rasterization) inherits seven#E2's disposal discipline automatically — dispose in the function that acquires, as its first statement, the same as any other context-creating code path, or the fix itself becomes the leak.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the live-canvas list after 4 undisposed calls, confirming the unrelated earlier canvas was evicted.
- Composed: dark-goblin/E6, seven/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E43 — edge darkgoblin draft pkill selfkill and wrong dir both report 0 pushed
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [tooling][process][ci]
- What: dark-goblin#E2's pkill -f self-kill (exits 128+n, every && step after it silently never runs) and draft#E5's ambiguous incoming/ directory are a THIRD confirmed root cause for the exact '0 pushed, 0 held' signature already known to be ambiguous — here the sync step never ran AT ALL, producing output indistinguishable from a sync that ran correctly against an empty, wrong directory.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A pkill -f pattern matching its own invoking shell line caused the following brain-sync step to never execute; the observed signature ('0 pushed 0 held') was identical to draft#E5's own already-recorded wrong-directory case, where sync DOES run, just against nothing.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: The '0 pushed, 0 held' signature now has (at least) three independently-confirmed causes — genuine emptiness, a wrong-but-identically-named target directory (draft#E5), and a silently-skipped step from an unrelated && chain failure (dark-goblin#E2) — treat it as uninformative on its own and check which of the three actually happened before trusting any of them.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both failure paths' observed output, textually identical despite completely different mechanisms.
- Composed: dark-goblin/E2, draft/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E95 · compatible · sandboxes/2026-10-08__zero-count-groundtruth-check.py · observed RESULT: PASS of 3 failing worlds, naive trust flagged 0, source-count check flagged 3, directory comparison pinpointed 1 (prediction refuted for the directory comparison). · brain train pass 4

## E42 — edge collective seven proxy category gate mismatches real decidability both directions
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [process][agent][testing]
- What: collective#E2's proxy-category gating mistake ('fact-lookup-only' standing in for 'objectively decidable') fails in BOTH directions, verified concretely: a task that looks like a lookup but hinges on human taste gets wrongly admitted, and a task that IS objectively decidable but doesn't surface-match the lookup shape gets wrongly blocked.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A human-taste-dependent task matched the 'looks like lookup' proxy and was wrongly admitted; a genuinely decidable but oddly-phrased task failed the same proxy and was wrongly blocked — both mismatches on the same gate.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A proxy category for a real property (collective#E2) isn't just under- or over-powered in one direction — verify BOTH false-admit and false-block cases explicitly before trusting a surface-shape gate, since a gate tuned to fix one direction's failures can leave the other completely open.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both example tasks' proxy-admit result against their real decidability, mismatching in both directions.
- Composed: collective/E2, seven/E6
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E41 — edge brain zanegpt unchecked edge recommender is the least checked claim
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [tooling][process]
- What: brain#E6's own recorded finding (brain train edge ranks purely by shared-tag count, no accessibility filter, top pick inaccessible most of the time) is a direct instance of zanegpt#E5's warning — a confident, unqualified recommendation from the tool's own reasoning is exactly the 'agent's account of its own runtime' zanegpt#E5 says is the least-checked claim in the room.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The naive recommender confidently picked the highest-scored candidate (repoA, inaccessible); adding the accessibility check zanegpt#E5's own discipline demands correctly skipped to the next viable candidate (repoB).
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any ranking/recommendation tool's TOP pick deserves the same skepticism zanegpt#E5 applies to an agent's runtime self-report — a confident single-criterion ranking (shared-tag score) says nothing about a second, unchecked precondition (accessibility) the ranking never modeled.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the naive top pick (inaccessible) against the accessibility-checked pick (accessible).
- Composed: brain/E6, zanegpt/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E40 — edge dbzcombat seven set e truncates a monotonic axis sweep before the top
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][balance][tooling]
- What: dbz-combat#E2's monotonic-power-axis sweep (checking no single obviously-dominant pick exists) run under seven#E3's set -e pattern aborts at a deliberately-included worst-case fixture and never reaches the top of the axis — the sweep can report 'no dominance found' while never actually testing the one point (the top) where dominance would show.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The sweep intended to cover power levels 1-5; a known-worst fixture at level 3 aborted it under set -e, leaving levels 4-5 (including the true top of the axis) never tested.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: seven#E3's known-red-kills-set-e failure is especially dangerous composed with a MONOTONIC sweep (dbz-combat#E2) specifically, because the sweep's most informative point is always at one end of the range — a truncation anywhere before that end silently removes the exact evidence the sweep exists to gather, not just a random sample of it.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the intended vs actually-covered power levels and confirmed the true top was never reached.
- Composed: local/sandbox-dbz-combat/E2, seven/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E39 — edge dbzcombat opticon same frame off by one shape two subsystems
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedev][state][determinism]
- What: dbz-combat#E1's cancel-flag ordering bug (set inside a branch that runs AFTER the frame's input is sampled) and opticon#E5's passable-tile update (not everywhere at once) are the identical off-by-one-frame shape verified together in one frame loop — a write happening later in the SAME frame than its reader is stale for that frame and only correct starting next frame, regardless of which subsystem (a UI cancel window, a pathfinder) the flag belongs to.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Both the cancel flag and the passability flag read as their stale default on the frame they're written, and both read correctly starting the following frame — same shape, same fix, different subsystems.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any per-frame-mutated flag needs its readers ordered explicitly AFTER its writers within the same frame, or every reader sees last-frame's value for one full frame regardless of domain — dbz-combat#E1 and opticon#E5 are the same bug in different subsystems, and the fix (write-before-read ordering) is identical.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both flags' read results in frame 1 (before same-frame writes) and frame 2 (after), identical stale-then-correct pattern for both.
- Composed: local/sandbox-dbz-combat/E1, opticon/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E38 — edge dbzcombat mirage null sentinel in a set leaks clearability
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [security][testing][state]
- What: dbz-combat#E3's unguarded null sentinel polluting an 'ever-optimal skills' Set does more than corrupt the aggregate — its mere presence in the set is an observation, mirage#E5's exact mechanism: any code iterating or checking membership against the naive set can detect that SOME scenario was unclearable, a leak the sentinel-guarded version never exposes.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The naive set contained None alongside real skill ids, so checking 'is None a member' correctly (if accidentally) reveals an unclearable scenario existed; the guarded set, built by filtering the sentinel before insertion, never contains it and reveals nothing.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Guarding a sentinel before aggregation (dbz-combat#E3's own fix) is also a privacy/leak fix, not just a correctness one, whenever the aggregate is exposed to anything an observer can query — apply mirage#E5's framing (a refusal/absence is itself information) to any sentinel-pollution bug, not only to deliberately-gated affordances.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both sets and whether membership-checking None reveals the unclearable-scenario fact for each.
- Composed: local/sandbox-dbz-combat/E3, mirage/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E37 — edge brain answeringdeep transient overflow invisible at final state
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [ui][testing][gamedev]
- What: brain#E7's fixed-width control bar clipping bug only manifests as a TRANSIENT state when content is assembled by answering-deep#E1's sequential same-slot-overwriting events — checking only the bar's FINAL content (after all events resolve) misses the clip entirely if a later, shorter event happens to overwrite the overflowing one before anyone looks.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A mid-sequence status message overflowed the simulated viewport width while the first and last messages in the same sequence did not — a test checking only final state would report no overflow ever happened.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A layout-overflow check (brain#E7) on content driven by sequential overwriting events (answering-deep#E1) must sample EVERY intermediate state the content passes through, not just the final one — the two bugs compose specifically because the overwrite pattern is exactly what makes a transient-only symptom possible in the first place.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the bar width at each of 3 sequential events, confirming transient overflow at step 2 invisible at the final step 3.
- Composed: brain/E7, the-game-the-answering-deep/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/local__sandbox-edges.md#E54 · compatible · sandboxes/2026-10-11__overflow-check-every-state-needs-measured-width-not-avg-char-estimate.py · observed RESULT: PASS of 14 overflow states final-only missed 11; every-state avg estimate missed 5 + 9 false alarms; with 20% slack 5 missed + 13 false; measured every-state 0/0 · scheduled brain train session, loop 2 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn

## E36 — edge august10 answeringdeep hysteresis margin on a discrete pulse eats it
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedesign][determinism][testing]
- What: august-10#E3's hysteresis margin, correctly stabilizing a genuinely continuous, oscillation-prone field, silently eats a discrete transient pulse entirely when applied to answering-deep#E5's 'detection = a transient ping' case — the same margin appropriate for one property class fails completely for the other, because a hysteresis dwell time assumes the value stays elevated long enough to confirm, which a genuine one-frame pulse never does.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The hysteresis margin correctly stabilized a real oscillating field (True/True/True mid-sequence); the identical margin applied to a single-frame detection spike never registered it at all — zero detections across the whole sequence.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Before applying a hysteresis/dwell-time margin (august-10#E3's own fix for oscillation), classify the property per answering-deep#E5's discrete-vs-continuous split first — a margin appropriate for a continuous field is not a safe default for a discrete event signal, it can suppress the event entirely rather than merely delaying it.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the hysteresis output for both the continuous field (stabilizes) and the discrete pulse (never detected).
- Composed: august-10/E3, the-game-the-answering-deep/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E35 — edge skilltree brain nan delta is worse than silent drift
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][testing][process]
- What: brain#E2's delta-sum drift (a rename-style event inflates a running total with no compensating negative) and skilltree-formula#E5's NaN propagation (one malformed upstream value poisons everything downstream, no error) compose in the same accumulator: the delta-sum drifts silently by a plausible amount even with clean data, and a single NaN delta anywhere poisons the ENTIRE total to NaN forever — different failure shapes, same accumulator, same fix.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG (except a seeded deterministic PRNG standing in for the sim's own RNG, where the claim is specifically about shared-RNG-stream coupling).
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Delta-summing a clean-looking stream still drifted from the independently-recomputed true total by 5 (brain#E2's own finding); adding one NaN delta to the identical stream poisoned the whole running total to NaN, a much louder but equally silent-at-the-source failure.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: An accumulator vulnerable to brain#E2's delta-sum drift is ALSO exposed to skilltree-formula#E5's NaN-poisoning the moment any upstream source can produce a malformed value — recompute ground truth independently (brain#E2's own recorded fix) to catch both, since neither failure throws on its own.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the delta-sum total vs true total (drift=5) and the same stream's total once one NaN delta was added (poisoned to NaN).
- Composed: local/sandbox-combined-skilltree-formula/E5, brain/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E34 — edge seven recursion existence checker misses caller supplied bypass
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [security][testing][state]
- What: recursion#E2's bypassable gate (threshold read from the gated command's own payload) is checked by a seven#E4-style static/existence checker as PASS (the reference exists in source), while a caller supplying threshold=0 directly bypasses the gate at runtime — the static check never actually exercises the vulnerable call path.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG (except a seeded deterministic PRNG standing in for the sim's own RNG, where the claim is specifically about shared-RNG-stream coupling).
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The existence check passed because the source literally references cmd.get('threshold'); a dynamic call supplying threshold=0 bypassed the gate completely, something the static check has no way to see.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A static check for 'does this code reference the gating field' (seven#E4's failure shape) tells you nothing about whether the field is caller-controllable in a way that defeats the gate (recursion#E2's own finding) — verify by actually calling the gated function with adversarial payload values, not by grepping for the field name.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the static check's pass and the dynamic bypass with a caller-supplied threshold=0.
- Composed: seven/E4, the-game-the-recursion/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E33 — edge opticon answeringdeep terminal state sim shares the coupled rng
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [determinism][testing][gamedev]
- What: opticon#E1's fix (simulate whole runs to terminal state for a reachability/outcome test) does not by itself isolate the sim from answering-deep#E3's shared-RNG-stream coupling — an unrelated entity consuming one extra draw before the reachability sim runs flips its terminal outcome for the same seed, because 'simulate to terminal state' says nothing about which RNG stream the simulation draws from.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG (except a seeded deterministic PRNG standing in for the sim's own RNG, where the claim is specifically about shared-RNG-stream coupling).
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The same seed produced terminal state -1 in isolation and -3 once one unrelated draw was consumed first by another entity — the reachability sim's own logic never changed.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: opticon#E1's terminal-state simulation and answering-deep#E3's stream-isolation fix are independent requirements — simulating to a terminal state makes the test outcome-based instead of step-based, but only isolating the RNG stream (answering-deep#E3) keeps that outcome stable against unrelated content changes elsewhere in the world.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the terminal state with and without one unrelated draw consumed first, same seed, different result.
- Composed: opticon/E1, the-game-the-answering-deep/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E32 — edge mirage answeringdeep partial bust masks a graceful fallback fix
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [deploy][tooling][content]
- What: answering-deep#E4's silent-placeholder fallback for a missing sprite-map entry has no build-time signal by design; shipping the fix (adding the entry) still shows the placeholder to users stuck on mirage#E4's exact failure — a stale, unstamped nested import serving the OLD sprite map, so 'shipped fix had no effect' is not a red herring, it's the predictable composition of both bugs.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG (except a seeded deterministic PRNG standing in for the sim's own RNG, where the claim is specifically about shared-RNG-stream coupling).
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The placeholder rendered before the fix (expected) and rendered identically AFTER the fix shipped, because the entry-point was stamped but the nested sprite-map import was not, so affected users' browsers kept serving the pre-fix file from cache.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: When a 'shipped fix had no effect' report follows a fix for a silently-graceful fallback (answering-deep#E4), check mirage#E4's own diagnostic FIRST (stamp every specifier in source, not just the entry point) before re-diagnosing the original bug — the fallback's silence and the cache's staleness compound into an identical-looking failure from two different, already-recorded causes.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the placeholder result both before and after the fix, identical, tracing to the nested-import staleness.
- Composed: mirage/E4, the-game-the-answering-deep/E4
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E31 — edge dbzcombat august10 bucket saturation flags a trustworthy looking report
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][process]
- What: dbz-combat#E5's warning (a coverage report can look trustworthy while being wrong in an unrelated way) has a cheap, general early-warning check in august-10#E2's own finding — a bucket saturated with an exact-match parser's '' miss value is the SAME tell august-10#E2 already names for a different metric, and checking for ANY suspiciously large bucket catches this class of report-level bug without the full independent-oracle recomputation dbz-combat#E5's fix requires.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG (except a seeded deterministic PRNG standing in for the sim's own RNG, where the claim is specifically about shared-RNG-stream coupling).
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Case/whitespace label variants (CAT_A, 'cat_a ') and two genuinely unmatched labels all silently landed in the '' bucket via exact-match parsing, saturating it to 57% of all entries — a report reader trusting per-category percentages would never see this without checking bucket-level saturation.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Before running dbz-combat#E5's full independent-oracle check on a coverage/aggregation report, first check for august-10#E2's cheap saturation tell (any one bucket, especially a miss/empty/unknown bucket, holding a suspiciously large share) — it doesn't replace the full check, but it's a fast first signal that something in the underlying parser is silently eating real data.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the actual bucket counts and the saturated '' bucket's fraction (0.57) from case/whitespace-variant labels.
- Composed: local/sandbox-dbz-combat/E5, august-10/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E30 — edge draft wrongsky escape hatch inside per tile loop reintroduces scaling bug
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [performance][rendering][gamedesign]
- What: draft#E3's bespoke-procedural escape hatch, if implemented as a per-tile filter call inside the same per-tile draw loop, reintroduces wrong-sky#E3's exact performance bug (filter cost scales with draw count) even though it correctly fixes the visual-quality problem the escape hatch exists for.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A naive per-tile override applies one filter call per override-tile (cost scales 10/100/1000 with tile count); compositing all override-tiles into one offscreen buffer and filtering once holds constant at 1 filter call regardless of tile count.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any content-quality escape hatch (draft#E3) that needs a per-item visual transform must be checked against wrong-sky#E3's own recorded fix (composite unfiltered, filter once) before shipping inside a per-item draw loop — fixing visual quality and reintroducing a cost-scales-with-draw-count regression are independent risks from the same code location.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed filter-call counts for both implementations across 10/100/1000 override tiles, linear vs constant.
- Composed: draft/E3, the-game-wrong-sky/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E29 — edge darkgoblin prologue sub frame press is a snapshot vs moving system case
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [input][testing][harness]
- What: prologue#E2's finding (a press shorter than one frame is invisible to per-frame sampling) is a fourth confirmed instance of dark-goblin#E5's generalized diagnosis (a harness encodes a snapshot while the system keeps moving) — swept across increasing frame durations, the sampling harness's miss rate on a fixed-duration press only gets worse, the hallmark of a snapshot-lag failure, not a one-off.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A 5ms press was missed by the sampling harness at every tested frame duration (8/16/33/66ms), while event-time capture saw it every time — the miss doesn't improve at any tested frame rate, confirming it's structural, not incidental.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: prologue#E2's own fix (capture at event time, never sample held state once per frame) generalizes exactly the way dark-goblin#E5 predicts for any harness snapshotting a continuously-moving system — sweep the relevant timing parameter (here, frame duration) to confirm a suspected snapshot-lag bug is structural before treating it as a one-off flake.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the sampling harness's miss/hit result across 4 frame durations against event-time capture's consistent hit.
- Composed: dark-goblin/E5, the-game-prologue/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E45 · compatible · sandboxes/2026-10-11__render-pass-snapshot-of-animated-page-needs-frozen-clock.py · observed RESULT: PASS 4/4; unfrozen flaky@120 0.80 max 7.68px; frozen 0; static 0 · session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E28 — edge brainbuilder draft coupled feedback needs drafts own override field
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedesign][state]
- What: brain-builder#E6's loud-on-every-event feedback channel, when derived directly from draft#E2's combat-balance flag with no override, cannot represent a move that wants the presentation (beam) without the loud feedback — draft#E2's own recorded fix (an explicit override field) is exactly what decouples them.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A move wanting beam presentation with quiet feedback got forced into LOUD_FLASH under direct coupling; adding draft#E2's override field let the same move correctly render quiet.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any presentation-loudness channel derived directly from an unrelated balance/mechanic flag (draft#E2's coupling risk) will eventually need to disagree with that flag for SOME content — budget the override field before the first move that needs it, not after, since brain-builder#E6's 'gate the loudest channels' has no lever to pull without one.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the coupled result (forced loud) vs the override-field result (correctly quiet) for the identical move.
- Composed: brain-builder/E6, draft/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E27 — edge brainbuilder darkgoblin ratchet bot flattens smoothness assertion
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][balance][ai]
- What: brain-builder#E5's smoothness assertion (no single-step drop across party size) can PASS on a measurement produced by an argmax-ratchet balance bot (dark-goblin#E1), while the true difficulty curve for a real player still has a genuine step — the bot's narrow, locked-in strategy never samples the harder cases where the real drop lives.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The true curve (0.79->0.40->0.16 across sizes 3-5) fails the smoothness check; the ratchet bot's measured curve (flattened to 1.00/1.00/0.95/0.95) passes it, on the exact same underlying boss.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A smoothness/monotonicity assertion (brain-builder#E5) is only as trustworthy as the agent measuring it — dark-goblin#E1's warning (distrust an instrument that returns exactly the success it was built to detect) applies directly: verify the measuring bot itself isn't ratchet-narrow before trusting a passing smoothness check.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both curves and the smoothness check's verdict on each, same boss, different measuring agent.
- Composed: brain-builder/E5, dark-goblin/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E26 — edge brainbuilder answeringdeep grouped beat is compose not overwrite
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedev][rendering][state]
- What: brain-builder#E7's fix (group simultaneous same-source hits into one beat) is a specific instance of answering-deep#E1's general rule (a later handler must compose with, not overwrite, an earlier one writing the same UI slot) — a naive per-event replay renderer that sets the display slot per event loses all but the last of 3 simultaneous hits, exactly answering-deep#E1's failure shape, now on a combat-trace replay instead of a modal/toast slot.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A naive renderer setting the display slot once per trace event showed only the last of 3 simultaneous hits; accumulating (composing) all 3 into the slot showed the full grouped beat.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Rendering a deterministic combat trace as a pure replay (brain-builder#E7) still needs answering-deep#E1's compose-not-overwrite discipline at the actual render step — grouping events into a beat upstream doesn't help if the renderer itself sets a shared display slot per event rather than accumulating.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the naive renderer's single surviving hit vs the composed renderer's full 3-hit group.
- Composed: brain-builder/E7, the-game-the-answering-deep/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E25 — edge test lockstep withheld command still shares the triggering edge
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [input][gamedev][state]
- What: test#E4's correct i-frame implementation (withhold the damage command on the dodge edge, not a state flag) does not protect against lockstep#E4's separate failure — if another system (block) reads the SAME raw input edge unconditionally, that system still fires from the identical press, because withholding one consumer's command does nothing to a second consumer reading the same edge.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A single dodge-press edge correctly withheld the damage command (test#E4) while the SAME edge, read unconditionally by a second system, also fired an unintended block action (lockstep#E4) — both from one input, until the edge read was context-gated.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: test#E4's command-withholding technique is correct but SCOPED to one consumer — any other system reading the same raw input edge needs its own context gate (lockstep#E4's fix) independently; fixing one consumer's response to an edge says nothing about another consumer sharing that same edge.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both systems firing from one shared edge, then both correctly separated once context-gated.
- Composed: test/E4, lockstep/E4
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E24 — edge seven wrongsky per call requery misses cumulative invariant
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][state]
- What: wrong-sky#E4's own noted blind spot (a test suite that always re-queries between picks never catches an exclusive-offer violation) is seven#E4's general vacuous-checker shape — a check scoped per-call (is anything still pending right now) can never see a violation of an invariant scoped across the WHOLE sequence (exactly one accepted, ever).
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A per-call re-query check passed after both an allowed first accept AND a should-be-impossible second accept, because each call only asks 'is something still pending,' never 'how many were ever accepted' — the cumulative count (2) violates the real invariant the per-call check can't see.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A checker's scope must match the invariant's scope — a per-call re-query is the right tool for a per-call property, and the WRONG tool for a property (exactly one accepted, ever) that only exists across the whole sequence; verify sequence-scoped invariants with sequence-scoped checks, never a re-query.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both per-call check results (both pass) against the real cumulative accepted count (2, violating exactly-one).
- Composed: seven/E4, the-game-wrong-sky/E4
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E23 — edge seven waitingcity unnamespaced shared state same fix two domains
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][architecture]
- What: seven#E5 (two games sharing one origin's storage, unnamespaced key collides) and waiting-city#E3 (two NPC roles sharing one view-state slot, unnamespaced key collides) are the same generalized bug and the same generalized fix — verified together, the identical namespacing technique resolves both, though the domains (deploy storage vs. UI event handling) share nothing else.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Unnamespaced writes to a shared store from two independent writers silently lost the first writer's value in both cases; adding a scope prefix to the key preserved both values in both cases, with no other change.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: 'Two independent things share one flat key space' is a domain-agnostic bug shape (storage, view-state, any dict-like shared store) — the fix is always the same: namespace the key by the writer's identity before it ever touches shared storage, regardless of what domain the two writers happen to be in.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed collision results for both domains unnamespaced, then both domains namespaced, confirming both fixed identically.
- Composed: seven/E5, the-game-the-waiting-city/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-12 · projects/pappydapimp69__seven.md#E84 · compatible · sandboxes/2026-10-12__merging-keyed-sets-namespace-every-key-not-just-the-fallback.py · observed RESULT: PASS 4/4; misfiled naive 4, fallback-only 2, full 0, no-overlap 0 · session; brain train auto pass 2 (edge); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E22 — edge august10 zanegpt isolated conjunction test hides real arithmetic shortfall
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][gamedesign][balance]
- What: august-10#E7's arithmetic-unreachability finding is exactly what zanegpt#E4's mutation-testing discipline is built to catch and an isolated conjunction test is built to miss — a 'can build' test with only the stone term varied (wood/labor pinned generously true) passes at the tuned value while the REAL total demand across the whole tech tree already exceeds supply.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The isolated conjunction test passed (stone_ok pinned True); the real summed arithmetic (201 total stone demand vs 48 supply) shows it's actually unreachable; a mutation test on the stone term specifically would have caught the gap the isolated test's co-pinned terms hid.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A conjunction test ('can build X') varying only ONE term with the others pinned generously-true can pass indefinitely while the real, game-wide arithmetic (august-10#E7's own fix: sum total demand vs total supply) is already broken — apply zanegpt#E4's mutation check to the specific term under suspicion, and separately re-derive the real total from the whole content set, not a single test fixture's convenient values.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the isolated test's pass, the real arithmetic shortfall (201 vs 48), and the mutation test's catch.
- Composed: august-10/E7, zanegpt/E4
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E21 — edge august10 darkgoblin per item green and deploy green both insufficient
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][deploy][content]
- What: dark-goblin#E7's per-item well-formed check and august-10#E1's build-step-success signal are two INDEPENDENT insufficient proxies for 'the served result is right' — all assets can pass per-item validation while an aggregate defect (missing face) exists, AND the deploy step can report success while silently serving a stale fallback bundle; neither check implicates or substitutes for the other.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Per-item validation passed 6/6 assets while a contact-sheet-level check found a real missing-face defect on one; separately, a 'success'-reporting deploy step served a stale fallback bundle — both false-positive signals present simultaneously, independently caused.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Verify BOTH the aggregate content (dark-goblin#E7's contact sheet, not just per-item checks) AND the actually-served bytes (august-10#E1's fix, not just the build step's own exit code) — passing one says nothing about the other, and a pipeline needs both checks, not either.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed per-item pass=True, the aggregate defect list, and the deploy-success-vs-stale-served mismatch, all in one run.
- Composed: august-10/E1, dark-goblin/E7
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E20 — edge seven test hidden callback draws break saved seed count resume
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [determinism][state][testing]
- What: test#E2's save-{seed,count}-for-determinism discipline is defeated by seven#E1's callback-hidden variable roll count if the saved count only reflects the sim's 'obvious' top-level draws — resuming from an under-counted save produces a genuinely different subsequent random stream, silently, with no error.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: 3 enemies produced 4 real RNG draws (1 obvious + 3 hidden crit-checks); resuming from the correctly-counted save reproduced the exact next value, resuming from a save that only counted the 1 obvious draw produced a completely different next value.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Every RNG draw a sim's own code path causes — including ones buried inside a data-dependent callback (seven#E1) — must be reflected in the saved count test#E2 relies on; audit for callback parameters specifically, since they're the easiest place for a draw to happen without looking like 'the sim drew' at the call site being saved.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the true draw count and both resumed streams' next values, diverging as predicted.
- Composed: seven/E1, test/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/pappydapimp69__seven.md#E48 · compatible · sandboxes/2026-10-11__save-rng-state-words-survives-a-miscounted-draw.py · observed RESULT: PASS 4/4; true 6000 counted 3000; words cost 0 match; counted diverges; true-count cost 6000; sorted hash stable · session; brain train auto run 2 pass 1 (kernel, declare); session_01NHKVhTvCnvtvZ2NGLSPYj6

## E19 — edge seven prologue sentinel state words load as valid zero seed
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [determinism][state][testing]
- What: prologue#E1's fix (save the PRNG's raw state words, not a replay count) is itself exposed to seven#E6's sentinel-handoff risk if the saved state-words field can also legitimately mean 'never seeded' (a reserved 0/sentinel value) — a naive loader passes it straight through as a valid seed with no error, silently starting a deterministic-but-meaningless stream.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A naive loader accepted the sentinel state-words value (0) and returned it unchanged, no error; a loader that explicitly checks for the sentinel raised instead of silently seeding from it.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any 'save the raw state, not a derived count' fix (prologue#E1) still needs an explicit reserved-value check at load time if the state's own value space overlaps with a legitimate sentinel — seven#E6's fix (branch on the sentinel before handing it to the reconstructor) applies to PRNG state loading exactly as much as to any other reconstructed subject.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the naive loader's silent pass-through vs the correct loader's raised error on the identical sentinel input.
- Composed: seven/E6, the-game-prologue/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E18 — edge opticon seven vacuous name checker on renamed group
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][state][gamedev]
- What: A grouped-focus system (real leak in one named group) checked by a name-literal validator: renaming the leaking group makes the checker's hardcoded lookup miss it entirely and report PASS, though the leak is unchanged.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Renaming the leaking group from 'B' to 'B2' left the checker still searching for 'B'; it found nothing and reported PASS (vacuous), identical to seven#E4's generalized failure, now reproduced on a grouped-focus target instead of a document.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A checker binding its target by a NAME LITERAL rather than by structural identity silently stops checking after any rename in the system it watches — derive the target at check time, and treat an empty match set as a failure, not a pass.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed FAIL before rename, PASS (vacuous) after — same leak, same threshold, only the lookup key changed.
- Composed: opticon/E4, seven/E4
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E17 — edge opticon darkgoblin best ever gate blind to ratchet inflated score
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [ai][testing][gamedev]
- What: opticon#E6's best-ever stall-gate, applied to a score produced by an argmax-ratchet instrument (dark-goblin#E1), never fires: the ratchet's own metric climbs monotonically by construction even while the TRUE underlying behavior it's supposed to represent is collapsing, so the necessary best-ever fix is not sufficient when the input score is itself a ratchet artifact.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The best-ever gate correctly never stalls on the ratchet's self-reported score (0.60->0.64, monotonic) while the SAME gate correctly DOES stall on the true behavior series (0.10 down to 0.01) — the gate works exactly as designed on both, which is precisely the problem: it only ever sees the number it's handed.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A best-ever progress gate is only as trustworthy as the metric feeding it — if that metric can itself come from an argmax/ratchet-style instrument (dark-goblin#E1's own warning: distrust an instrument that returns exactly the success it was built to detect), verify the gate against the TASK's real outcome periodically, not only against its own input stream.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed stalled=False on the ratchet-reported series and stalled=True on the true-behavior series, same detector, same gate logic.
- Composed: opticon/E6, dark-goblin/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E16 — edge mirage test clear at tick start fragile to any write order
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][gamedev][architecture]
- What: mirage#E3's tick-clears-queue-at-start bug (destroys an earlier same-frame writer) recurs for ANY writer, not just the legitimate input-handler mirage#E3 found — including a boundary-violating 'read-only' renderer that writes per test#E5's own warning; whether a write survives depends entirely on its ORDER relative to the tick's clear, not on whether the writer was supposed to write at all.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A renderer write landing before the tick's clear is captured normally; the identical write landing after the clear silently vanishes from THIS tick and reappears in the queue for the NEXT one — a one-frame-delayed, unexplained effect.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A shared-queue 'clear at consumer's own start' pattern is fragile to write ORDER from every producer touching that queue, including ones that shouldn't be writing at all (test#E5's boundary violation) — mechanically enforce the read-only boundary AND fix the clear-timing, since either bug alone can produce this exact one-frame-delay symptom.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed captured-vs-not for a renderer write placed before vs after the tick's own clear call.
- Composed: mirage/E3, test/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E15 — edge mirage recursion zero sensitivity oracle is a classification question
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][gamedesign][ai-agents]
- What: mirage#E7's zero-sensitivity ground-truth oracle (flat across deception strength) is only wrong for information-gap mechanics — applying recursion#E3's own diagnostic (check whether two seemingly-conflicting precedents were each correct for a DIFFERENT object class) shows the SAME oracle is properly monotonic-sensitive on a non-information-gap mechanic, confirming both findings are correct for their respective class, not in tension.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The ground-truth oracle scored flat (1.0/1.0/1.0) across increasing deception on an info-gap mechanic, and monotonically decreasing (1.0/0.7/0.4) on a non-info-gap mechanic using the exact same scoring function — the oracle itself didn't change, only which class of mechanic it was measuring.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Before generalizing 'this oracle/instrument is broken' from one mechanic to a whole testing strategy, apply recursion#E3's classification check — sweep the SAME instrument across a mechanic class it should legitimately be sensitive to, and confirm the zero-sensitivity finding is specific to the information-gap class, not a blanket indictment of ground-truth-reading oracles.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the identical oracle function's scores across both mechanic classes, flat for one, monotonic for the other.
- Composed: mirage/E7, the-game-the-recursion/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E14 — edge draft waitingcity full session revert reverts story unlocks too
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [gamedesign][state]
- What: draft#E4's storyIdx-gated boss availability, composed with waiting-city#E1's full-session-revert respawn on a boss-fight loss, silently reverts a story unlock earned EARLIER in the SAME session, not just the fight's own progress — the respawn restores the session-start snapshot, which predates the mid-session advance.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A mid-session event advanced storyIdx from 2 to 3, unlocking something new; losing the boss fight triggered the recorded full-session-revert respawn, which restored storyIdx to its session-start value of 2 — the unlock vanished along with the expected combat retry.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A full-session-revert respawn (waiting-city#E1) composed with ANY session-scoped progress gate (draft#E4's storyIdx) needs the snapshot to be refreshed at every gate-advancing event, not just at session start, or a loss silently costs the player state they earned this session and never lost the fight over.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed storyIdx before the fight (3, unlock earned) and after the full-session-revert respawn (2, unlock gone).
- Composed: draft/E4, the-game-the-waiting-city/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E13 — edge draft seven reconstruct first still needs sentinel filtering
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [process][data-integrity]
- What: draft#E6's fix (reconstruct real data before any creative/structural decision locks in) is not sufficient on its own if the reconstruction accepts an unhandled sentinel (seven#E6) as real data — a naive reconstruction over raw records with a -1 'not recorded' sentinel produces a plausible but wrong total, with no error either way.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Naive reconstruction (no sentinel filter) totaled 7.5 over 5 nominal days; filtering the -1 sentinels first gave the true 9.5 over 3 real days — same input, silently different answers, neither throwing.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: 'Reconstruct the real data first' (draft#E6) must be read as 'reconstruct the real data, filtered for sentinels, first' — an unfiltered reconstruction is not more truthful than the assumption it replaces, just wrong in a way that looks authoritative.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both reconstructions' totals and day counts on the identical raw input.
- Composed: draft/E6, seven/E6
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E12 — edge draft mirage object literal last key wins two recorded shapes one mechanism
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][testing]
- What: draft#E1 (a derived key placed AFTER a spread silently overwrites the spread's same-named field) and mirage#E1 (opts spread AFTER reserved fields silently overwrites them) are the identical JS mechanism — last-key-wins in an object literal — verified together with the same fix (reorder so the value meant to win is listed last) resolving both.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: draft#E1's shape with the derived key moved BEFORE the spread preserves the original field, exactly matching mirage#E1's own recorded fix of moving opts before reserved fields — one mechanism, two independently-discovered instances.
- Fix: Apply both source lessons' fixes together; reorder so the intended winner is listed last, in every object literal of this shape.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes (reorder each literal) are applied.
- Rule of thumb: Any object-literal bug report of the shape "my field got silently overwritten" is the SAME last-key-wins mechanism regardless of whether the winner is a spread or an explicit key — the fix is always reordering so the intended winner is listed last, never a type-specific patch.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed both draft#E1's derived-key ordering (after: overwritten; before: preserved) and mirage#E1's opts ordering (wrong: opts wins; fixed: reserved wins).
- Composed: draft/E1, mirage/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E11 — edge darkgoblin mirage clamped timer plus weak assertion hides lateness
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][gamedev][determinism]
- What: dark-goblin#E4's clamped-delta headless timer (3x slower than real time) delays new timed content past a test's check window, and mirage#E2's bare length>0 assertion passes anyway on stale prior text still sitting in the element — a green test where the specific content under test never actually arrived.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: New narration arrives at 300ms under the clamp; a 100ms test window checks before it lands. length>0 on the stale text still passes; checking for the specific expected text correctly fails.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A weak presence assertion on a persistent UI element composes badly with any timing bug that only delays (not drops) content — assert the SPECIFIC expected value, and account for headless/clamped timing when sizing a test's wait window, not just when the content is dropped entirely.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed arrival time vs window, and both assertions' pass/fail on the same stale-text state.
- Composed: dark-goblin/E4, mirage/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E10 — edge collective opticon raw fetch by ref vs pages default only
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [deploy][process][tooling]
- What: collective#E1's ref-sensitive raw fetch (a complete raw URL returns 200 for whatever ref is named) composed with opticon#E3's Pages-serves-default-branch-only constraint means a raw fetch built against a non-default ref can return a 200 with content that was NEVER actually deployed and live users never see — the 200 status certifies the ref exists, not that it matches what's served.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: A raw fetch to a feature-branch ref returned 200 with draft content different from what Pages actually serves from the default branch — the mismatch is invisible from the fetch's own status code.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Any tool that both fetches its own reference content via a ref-sensitive raw URL (collective#E1) AND treats that content as representative of what's actually deployed (opticon#E3's default-branch-only Pages constraint) must pin the fetch ref to the SAME branch Pages serves, and verify a served-URL round-trip (opticon#E3's own recorded fix) rather than trusting a raw-URL 200 as proof of live content.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the fetched (wrong-ref) content, the actually-live (default-branch) content, and confirmed they differ despite a 200 status.
- Composed: collective/E1, opticon/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E9 — edge collective mirage differential response leaks injection denylist
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [security][testing][ci]
- What: collective#E3's injection fix (pass untrusted data via env:, never interpolate) still leaves a probing oracle if the DEFENSE's own response visibly differs when it detects a match — mirage#E5's 'a refusal is an observation' applies directly: a visibly-different response across 3 probe strings distinguishes the denylist boundary, a byte-identical acknowledgement does not.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The visibly-different responder produced 2 distinct outputs across 3 probes, letting an attacker binary-search the denylist; the uniform responder produced 1 output regardless, leaking nothing about which probe matched.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Fixing an injection vector (collective#E3) is necessary but not sufficient if the detection check's OWN behavior is externally visible — apply mirage#E5's fix (emit a byte-identical acknowledgement regardless of the internal verdict) to any injection-detection layer, not just to the mechanics it originally targeted.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed the distinct-output counts for both responder styles across the same 3 probe strings.
- Composed: collective/E3, mirage/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-10 · projects/local__sandbox-refusal-rule-not-bucket.md#E1 · compatible · sandboxes/2026-10-10__refusal-names-the-rule-not-the-bucket-but-never-the-secret-operand.py · observed RESULT: PASS rule-level refusal cuts guard calls to 0.57x of category-only (S1) and gives 20/20 named receipts on false positives, but naming matched VALUES drops secret-threshold recovery from 8 to 1 probe and listing ALL matched rules le… · session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-10 · projects/pappydapimp69__brain.md#E123 · incompatible · sandboxes/2026-10-10__boundary-by-construction-vs-classification-evasion-and-capability-cost.py · observed RESULT: FAIL evasion D1 96 D2 84 D3len 26 D3str 18 of 108; leaks fence 2 fixed-nonce 1 quote 5 nonce 0 json 0; rules effective placement 0/20 typed G0 10 G1 14 G2 17; misses 2/16. The two misses are the strict-detector rule delivery (1/20… · session_01YFLLRpDsfZpRstb2KT2MQy

## E8 — edge collective dog normalize fix reintroduces nan poisoning
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][testing]
- What: collective#E6's own recommended fix (normalize a weighted sum by total weight, instead of an unbounded raw sum) reintroduces dog#E3's exact NaN-poisoning failure if any single input's weight is corrupted — the division silently propagates NaN into the displayed value, which a naive clamp then hides as a plausible-looking pinned number.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: One corrupted (NaN) weight among three inputs made the normalized average NaN; a clamp-to-display function then silently returned the floor value (0.0) for the NaN case, reproducing collective#E6's original 'looks pinned/stuck' symptom via a completely different cause (dog#E3's NaN fan-out) than the one collective#E6 was originally filed to fix.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: Guard the normalization step itself (isFinite/isNaN check on the total weight AND the result) before it reaches any downstream clamp, not just at the final consumer boundary — a clamp silently converts NaN into a plausible in-range number, hiding the exact failure dog#E3 says needs a loud guard.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed clean-weights average (2.0) vs corrupted-weight average (nan), and both values after passing through the same display clamp (2.0 vs 0.0, no error either time).
- Composed: collective/E6, dog/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E7 — edge brainbuilder seven two silent canvas failures opposite symptoms
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [browser][rendering][testing]
- What: brain-builder#E3's undersized-canvas bug (300x150 default) and seven#E2's oldest-context-eviction bug produce OPPOSITE visual symptoms — a small-but-rendering canvas vs a black one — and can co-occur on the same page across different canvases, so debugging 'a canvas is broken' by symptom alone can't tell which bug is live without checking BOTH used-size and context liveness.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: After 4 mounts with no cleanup (context cap 3): the earliest, CORRECTLY-sized canvas went black (evicted); a later, mis-styled canvas stayed alive but rendered at 300x150 — both silent, zero errors, opposite symptoms.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A broken canvas needs two independent checks, not one: used element size (brain-builder#E3) and context liveness/eviction order (seven#E2) — a black canvas and a tiny-but-visible canvas are different bugs even on the same page in the same session.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed alive/size state for both the evicted canvas and the mis-sized one after 4 mounts.
- Composed: brain-builder/E3, seven/E2
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-11 · projects/pappydapimp69__brain.md#E136 · compatible · sandboxes/2026-10-11__weather-layers-one-canvas-per-layer-hits-context-cap.py · observed RESULT: PASS L=5 cap=3: per-layer 3/5 live (0.69ms, cheapest because 2 layers never draw); one canvas 5/5 1.15ms; DOM fallback 5/5 6.73ms; L=3 all layouts 3/3. (The "about the same total" part of the prediction missed: 0.69 vs 1.15 ms.) · brain train auto loop 2 pass 2 (edge); session_01ScEdAr4bK7Pp21fx27MXao
- Cited-by: 2026-10-11 · projects/local__sandbox-edges.md#E53 · compatible · sandboxes/2026-10-11__canvas-label-fit-expansion-headroom-and-font-reset-on-resize.py · observed RESULT: PASS EN box 84px overflows 3 DE labels; flat +30% still 1; knee x1.31; font-reset false passes 3 vs 0 · scheduled brain train session, loop 1 pass 2; session_01CNA5AiMj7DcwaL9AXKp2Jn

## E6 — edge brain recursion unhandled branch and uninitialized field same silent shape
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [state][testing]
- What: brain#E3 (an unhandled block-end condition silently drops) and the-game-the-recursion#E1 (a new reducer field with no constructor initializer silently NaN-poisons) are the same shape: an addition to an existing system not wired into every place the OLD system already touches fails with no exception, only a downstream wrong number.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The buggy accumulator (only routes ONE end-condition to its counter, and never initializes its new score field) undercounted (2 of 3 events) AND poisoned its score to None/NaN — both silently, zero exceptions; fixing both (route every condition, initialize every field at construction) cleared both.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: When adding a new field OR a new code path to an existing accumulator/reducer, grep for every existing entry/exit point the OLD fields already pass through and confirm the new one is wired into all of them — an exception-free wrong answer is the default failure mode for both omissions, not a coincidence.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed buggy (count=2, score=None) vs fixed (count=3, score=3) on the identical 3-event input.
- Composed: brain/E3, the-game-the-recursion/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E5 — edge brain draft wrong incoming dir mimics parser drop
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [tooling][process]
- What: Two independent root causes produce the identical '0 items found, reported as success' signature: brain#E3's unhandled-end-condition parser drop, and draft#E5's ambiguous incoming/ directory (project-local vs shared-cache, same relative path) — scanning the wrong one returns a correct-but-empty result indistinguishable from a genuine parser bug.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Scanning the real incoming/ directory found 3 proposals; scanning the other, empty one (same relative path, per draft#E5) returned 0 — structurally identical output to brain#E3's silent-drop bug, though nothing was actually dropped here.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A '0 found' result from ANY block-scanning tool needs an independent ground-truth check on the confirmed-correct target before being trusted as 'nothing to do' — the same zero can mean empty, wrong target, or a parser drop, and only an out-of-band count distinguishes them.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed 3-vs-0 scan results against the two differently-populated directories.
- Composed: brain/E3, draft/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E95 · compatible · sandboxes/2026-10-08__zero-count-groundtruth-check.py · observed RESULT: PASS of 3 failing worlds, naive trust flagged 0, source-count check flagged 3, directory comparison pinpointed 1 (prediction refuted for the directory comparison). · brain train pass 4

## E4 — edge brain darkgoblin camera core passes shell off frame
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][architecture][gamedev]
- What: brain#E4's camera-scale-schedule 'core' (a pure progress-to-scale function) passes its own unit tests completely while the content is off-frame on day one — exactly the core-to-shell seam dark-goblin#E3 warns a pure core relocates bugs to, reproduced concretely in a camera/viewport domain instead of a UI/data domain.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Core unit tests (exact schedule values at three progress points) all passed; the same schedule left a node at its final layout radius (1100) outside the day-1 visible extent (1000) — the seam (schedule output vs real content extent) is exactly what the core tests never touch.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A pure schedule/policy core passing 100% of its own tests says nothing about whether the SHELL (real content extent, real viewport) it drives stays on-frame — dark-goblin#E3's fix (a screenshot-level or extent-level smoke check) is required in addition to, not instead of, core unit tests.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed core-test pass=True alongside a concrete off-frame=True result from the same schedule.
- Composed: brain/E4, dark-goblin/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

## E3 — edge brain brainbuilder scale only fix validated at one regime
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][performance][process]
- What: brain#E5's sqrt(n) batch-budget fix, validated only at large n, looks correct exactly the way brain-builder#E1 warns a balance constant can — the flat-budget bug it replaces is 10x worse than sqrt(n) at small n but only 100x vs 10x, a difference invisible unless swept across scale, not checked at one n.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: Small/large per-event-time ratio: sqrt-budget 10x, flat-budget 100x — the flat bug's true severity (10x worse than the fix) only shows up sweeping n; a single large-n check would show both looking 'fine' in absolute terms.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A fix framed as 'scales correctly' (sqrt(n), not linear or flat) needs verification swept across the SAME small/medium/large regimes brain-builder#E1 demands for a balance constant — one regime's numbers looking reasonable doesn't confirm the SHAPE of the fix is right.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed per-event-time arrays and the small/large ratio for both budget functions across n=2/20/200.
- Composed: brain/E5, brain-builder/E1
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E226 · compatible · sandboxes/2026-10-14__gc-young-size-sweep-weak-generational-and-ram-cliff.py · observed RESULT: PASS best-throughput Y=16384 (RAM headroom 16384); A thr 0.105->0.882 in RAM, collapses to 0.001 at Y=131072; B thr 4096->16384 gain 0.0097; pause 55->218 us. First run was FAIL (paging counted as work; B claim too strong). · brain train auto loop 1 pass 5; session_01AMmNLeLopueLdsbKx7q1Lv

## E2 — edge august10 seven set e truncates decorrelated order sweep
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [testing][determinism][tooling]
- What: A decorrelated-order agreement sweep (run several traversal orders, measure agreement rate) implemented as a set -e shell script silently truncates the moment it hits a deliberately-included divergent witness order, understating the measured agreement rate without any error.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: 5 intended order-runs; a known-divergent witness at index 2 (nonzero exit) aborted the script under set -e; only 3 of 5 ran. True agreement 0.80, measured (truncated) 0.67 — a real, silent understatement.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A set -e runner and a 'measure agreement across several expected-to-sometimes-disagree runs' sweep are incompatible defaults — capture each run's status explicitly and continue, never let set -e treat an EXPECTED nonzero result as a fatal error.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed exact run counts (5 intended, 3 ran) and both agreement rates (0.80 true vs 0.67 measured).
- Composed: august-10/E4, seven/E3
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU
- Cited-by: 2026-09-30 · projects/local__sandbox-sentinel-and-failfast-coverage-sweep.md#E1 · compatible · sandboxes/2026-09-30__sentinel-and-failfast-coverage-sweep.py · observed RESULT: PASS naive tally counts phantom 'None' (distinct 5 vs true 4) and fail-fast covers 5 of 12 cases; guarded covers 11 with no_winner=3 errors=1 · scheduled train pass 5

## E1 — edge august10 collective extras outside gate defeats server side veto
- Date: 2026-09-29
- Project: local/sandbox-edges
- Tags: [security][gamedesign][state]
- What: collective#E5's server-side default-deny gate (a prompt can't grant the gated action) is defeated in NET EFFECT by august-10#E6's own recorded anti-pattern if side-effect 'extras' are applied outside the gate — the primary action stays correctly denied, but the total effect still lands above idle baseline.
- Why built: brain train edge picked this pair by shared-tag count; composed the two recorded lessons and verified with a sandbox.
- Design: Small deterministic Python model of both mechanisms together, no RNG.
- Got right: Each source lesson's own fix, applied alone, behaves as recorded.
- Where/why it failed: The gate correctly denied the primary action in both cases; extras applied outside it still pushed the net effect (40) above the idle baseline (34), exactly august-10#E6's own numeric shape, now in a security-gate context.
- Fix: Apply both source lessons' fixes together; neither alone is sufficient, per the sandbox.
- Why this fix: The sandbox reproduces the composed failure only when both mechanisms are present unfixed, and clears when both fixes are applied.
- Rule of thumb: A server-side default-deny gate (collective#E5) must wrap EVERY side effect of the gated action, not just the action's headline output — write `gated ? (everything) : 0`, never `(gated ? action : deny) + always-applied extras`, because a veto that leaves any additive side-channel unconditional is defeated in effect even when it correctly blocks the primary action.
- Provenance (verified/assumed): Verified first-hand — sandbox built and run this session; printed net effect with extras outside vs inside the gate, against the idle baseline.
- Composed: august-10/E6, collective/E5
- Link: session https://claude.ai/code/session_012zuXA5N7JHxucNBdEWhyAU

