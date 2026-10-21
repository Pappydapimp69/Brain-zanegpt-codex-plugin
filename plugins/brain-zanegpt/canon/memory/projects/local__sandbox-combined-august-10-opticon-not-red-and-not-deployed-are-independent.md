# local/sandbox-combined-august-10-opticon-not-red-and-not-deployed-are-independent — lessons

Project: local/sandbox-combined-august-10-opticon-not-red-and-not-deployed-are-independent. Newest first.

---

## E1 — sandbox combined august 10 opticon not red and not deployed are independent
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-opticon-not-red-and-not-deployed-are-independent
- Tags: [process][ci][deployment][verification]
- What: A deterministic sandbox (four fixed run outcomes, no RNG) scoring CI deploy runs by a naive run-state check and by a served-bytes-versus-intent check, across a cancelled feature-branch run, a clean default-branch run, a silently downgraded run, and an outright failure.
- Why built: august-10#E1 records that the dangerous deploy end-states are wrong-but-plausible rather than red — a fallback that silently downgrades the artifact, or a "cancelled" run from a cross-branch shared concurrency group. opticon#E3 records that GitHub Pages via Actions deploys only from the default branch, blocking at deploy setup rather than failing. This tests what those two facts jointly do to any check keyed on run state.
- Design: Four scenarios carrying both a run state and a served/intended byte pair. The naive predicate treats any success-shaped state as green; the strict predicate additionally requires served bytes to equal intended bytes.
- Got right: Separating run state from served bytes as independent fields rather than deriving one from the other, which is what allows the three distinct outcomes (deployed fine, deployed wrong, never deployed) to be distinguished at all.
- Where/why it failed: The silently downgraded run reports green to the naive check while serving 60 of 100 intended bytes. Independently, the feature-branch push reports "cancelled" — never entering the failure state — so it is neither green nor red, and nothing was served. Together these make "not red" and "not deployed" fully independent properties: a branch-scoped deploy can be both, and no predicate over run state alone, however strict, separates the three outcomes.
- Fix: Verify deploys by comparing the SERVED artifact against intended bytes rather than by reading run state at any strictness, and treat a cancelled or skipped run as an explicit non-deploy requiring its own alarm rather than as an absence of failure.
- Why this fix: Each lesson alone suggests a run-state remedy — refuse downgrade fallbacks, scope concurrency by ref, merge to the default branch. Composed, they show run state is the wrong observable entirely: the state machine has a success value that does not imply delivery and a non-failure value that implies no attempt, so the only field that distinguishes all three outcomes is the artifact itself.
- Rule of thumb: august-10#E1's silent downgrade and opticon#E3's default-branch-only constraint make "not red" and "not deployed" independent — sandbox-confirmed a green-reporting run serving 60 of 100 intended bytes alongside a cancelled run that is neither green nor red and served nothing; verify served bytes against intent, and alarm on cancelled/skipped as a non-deploy.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b4/l12.py) and confirmed the downgraded run scores naive-green True with artifact-matches-intent False, and the feature-branch run scores False on both while never entering a failure state. august-10#E1 and opticon#E3 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E1, pappydapimp69__opticon/E3
- Link: session_014mRpopK9xnhvk35tT8ozkX

