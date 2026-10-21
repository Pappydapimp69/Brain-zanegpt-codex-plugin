# local/sandbox-combined-recursion-wrong-sky-withheld-command-is-an-unpinnable-gate — lessons

Project: local/sandbox-combined-recursion-wrong-sky-withheld-command-is-an-unpinnable-gate. Newest first.

---

## E1 — sandbox combined recursion wrong sky withheld command is an unpinnable gate
- Date: 2026-08-29
- Project: local/sandbox-combined-recursion-wrong-sky-withheld-command-is-an-unpinnable-gate
- Tags: [security][architecture][state][determinism]
- What: A deterministic sandbox (scripted command streams, no RNG) running a reducer under two gate mechanisms — an armour threshold sourced either from the command payload or pinned in state, and an i-frame implemented as the driver withholding commands — against honest and forged command streams.
- Why built: recursion#E2 records that a reducer gate reading its threshold from the gated command's payload is bypassable, and prescribes pinning the value in state before the dependent command can influence it. wrong-sky#E9 records the opposite-direction idiom for i-frames: keep the reducer pure and model invulnerability as the DRIVER withholding the strike command, with no invuln flag in state. This tests whether recursion#E2's discipline covers a gate built the way wrong-sky#E9 prescribes.
- Design: Two gate sites exercised separately. The armour gate is tested at armour 15 against a threshold of 10, so honest strikes are correctly blocked and a forged `threshold: 999` reveals the bypass. The i-frame gate is tested at armour 5, where the armour gate is open by design and invulnerability exists only as the driver's choice to withhold, comparing an honest driver that withholds three ticks against a forged stream that withholds nothing.
- Got right: Separating the two gate sites and giving each the armour value that makes it the active gate; an earlier single-armour construction had the armour gate masking the i-frame gate entirely and produced no usable comparison.
- Where/why it failed: recursion#E2's fix works exactly as recorded on the armour gate — the payload-sourced threshold drops HP from 100 to 70 under a forged command, and pinning the threshold in state restores it to 100. But the i-frame gate has no value to pin: wrong-sky#E9 deliberately removed it from state. A forged stream that simply never withholds lands every strike (HP 40 versus 70 for the honest driver) against a reducer that is entirely correct and fully compliant with recursion#E2.
- Fix: Treat wrong-sky#E9's withholding idiom as trusting the command source, and state that trust explicitly — either authenticate or authoritatively generate the command stream, or keep a minimal state-side i-frame deadline that the reducer itself enforces, accepting the impurity E9 was avoiding.
- Why this fix: recursion#E2 secures gate VALUES against a hostile payload; wrong-sky#E9 replaces a gate value with a trust assumption about the command SOURCE. Adopting E9 therefore moves that gate outside the scope of E2's audit without removing the gate, so a codebase can pass a complete E2 review while its most timing-sensitive protection is unenforced.
- Rule of thumb: wrong-sky#E9's withheld-command i-frame is a gate with no value to pin, so recursion#E2's "fix the threshold in state" discipline cannot cover it — sandbox-confirmed a forged stream that never withholds lands every strike (HP 40 vs 70) against a fully E2-compliant reducer; adopting E9 converts a state gate into a trust assumption about the command source, and that trust must be stated and enforced.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b3/l11.py), including an earlier construction that did not reproduce because a single armour value masked one of the two gates; confirmed the payload-threshold bypass (100 to 70, restored to 100 when pinned) and the i-frame failure (40 vs 70) against a state-pinned reducer. recursion#E2 and the-game-wrong-sky#E9 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__the-game-the-recursion/E2, pappydapimp69__the-game-wrong-sky/E9
- Link: session_014mRpopK9xnhvk35tT8ozkX

