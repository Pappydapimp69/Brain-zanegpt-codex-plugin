# local/sandbox-combined-save-lifecycle — lessons

Project: local/sandbox-combined-save-lifecycle. Newest first.

---

## E1 — save import and restart need distinct lifecycle guards
- Date: 2026-07-13
- Project: local/sandbox-combined-save-lifecycle
- Tags: [save][state][gamedev][process][testing]
- What: An import/continue path and a restart-on-death path can corrupt different parts of the same run lifecycle: import can rerun once-only setup and reset in-session progress, while restart can reconstruct from seed/options and lose the session's actual starting snapshot. Fixing one path does not protect the other.
- Why built: `brain train` selected the high-value seam `dog + the-game-wrong-sky`. The interaction claim was that dog#E26's once-only side-effect hazard and wrong-sky#E2's snapshot-over-reconstruct restart rule compose inside save flows: a continued save needs idempotent setup guards, and a death restart needs the captured run-start snapshot.
- Design: Built `sandbox-save-restart-once-only.js`, a deterministic model with: - A `makeWorld(seed, options)` constructor defaulting to archetype `default` and level 1. - A level-2 setup function that spawns a boss and resets `bossWon`. - A saved level-2 `scout` run where `bossWon` is already true. - A naive import path that reruns setup and a naive restart path that calls `makeWorld(seed, {})`. - A fixed import path with an idempotency guard and a fixed restart path that restores a JSON run-start snapshot.
- Got right: The sandbox tests import/continue and restart separately in one flow, so it catches two lifecycle assumptions that can be hidden if each path is verified alone.
- Where/why it failed: The naive import preserved the archetype but reran level-2 setup, resetting `continuedBossWon` to `false`. The naive restart reconstructed from seed with empty options, producing archetype `default` and level 1 instead of the actual run-start archetype `scout` and level 2.
- Fix: Gate once-only setup on idempotent state such as `!bossSpawned` when a function can be reached from import/refresh paths. For restart-on-death, restore the captured run-start snapshot instead of reconstructing from seed/options.
- Why this fix: The fixed path preserved `continuedBossWon: true` after import and restored restart archetype `scout` at level 2. Those are independent guarantees: idempotency protects continued state, while snapshot restart protects run-start identity.
- Rule of thumb: Save/import and restart are different lifecycle surfaces. Audit both whenever a function gains a new caller: imports must not replay once-only side effects, and restarts must restore the exact run-start snapshot.
- Provenance (verified/assumed): Verified first-hand on 2026-07-13 by running `node sandbox-save-restart-once-only.js` in `C:\Users\Kompooter\Documents\Brain`. Observed: naive import setup + reconstruct restart = continued archetype `scout`, continued boss won `false`, restarted archetype `default`, restarted level 1; idempotent setup + snapshot restart = continued archetype `scout`, continued boss won `true`, restarted archetype `scout`, restarted level 2.
- Composed: dog/E26, the-game-wrong-sky/E2
- Link: Sandbox: `sandbox-save-restart-once-only.js`

