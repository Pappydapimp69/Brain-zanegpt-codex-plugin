# local/sandbox-combined-hold-dismiss — lessons

Project: local/sandbox-combined-hold-dismiss. Newest first.

---

## E1 — hold dismiss must ship on every input surface
- Date: 2026-07-13
- Project: local/sandbox-combined-hold-dismiss
- Tags: [input][ui][gamedev][mobile][testing]
- What: Changing a story prompt from tap-to-dismiss to timed hold fixes combat-mashing accidental dismissal only on input surfaces that actually receive the new hold action. A missing touch hold binding leaves touch users unable to dismiss the prompt at all.
- Why built: `brain train` selected the high-value seam `dog + the-game-wrong-sky`. The interaction claim was that wrong-sky#E11's hold-to-dismiss design must be audited through dog#E27's all-input-surfaces rule: adding a new player action is incomplete if keyboard/gamepad get it and touch does not.
- Design: Built `sandbox-hold-dismiss-input-surfaces.js`, a deterministic input model with: - A prompt that dismisses after 3 `holdDismiss` ticks. - Keyboard, gamepad, and touch input surfaces. - Keyboard/gamepad bindings for `holdDismiss`. - Touch with attack taps but no `holdDismiss` binding. - A touch attack-tap control to verify mashing no longer dismisses the prompt accidentally.
- Got right: The sandbox checks both requirements independently: high-frequency attack taps must not dismiss the prompt, and every supported input surface still needs a deliberate dismissal path.
- Where/why it failed: Keyboard and gamepad closed the prompt after 3 hold ticks. Touch had no hold binding, so three attempted hold-dismiss inputs left the prompt open with 0 hold ticks. Touch attack taps also left it open, which is correct for preventing accidental dismissal but exposes the missing intentional action.
- Fix: When introducing hold-to-dismiss, add and test the hold action on every supported input surface, including touch. Keep attack/tap separate from prompt dismissal, but provide a reachable touch-specific hold target.
- Why this fix: The model shows the design fix and the input-coverage requirement are different. Removing tap dismissal protects story prompts from combat mashing, but only adding the hold binding to touch makes the prompt dismissible for touch-only users.
- Rule of thumb: For a new player action, "works on keyboard" is not a shipped interaction. Audit keyboard, touch, and gamepad separately, especially when the action is meant to replace a dangerous shared control.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-hold-dismiss-input-surfaces.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: keyboard hold-dismiss = hold binding true, prompt open false, hold ticks 3; gamepad hold-dismiss = hold binding true, prompt open false, hold ticks 3; touch hold-dismiss = hold binding false, prompt open true, hold ticks 0; touch attack taps = prompt open true, hold ticks 0.
- Composed: dog/E27, the-game-wrong-sky/E11
- Link: Sandbox: `sandbox-hold-dismiss-input-surfaces.js`

