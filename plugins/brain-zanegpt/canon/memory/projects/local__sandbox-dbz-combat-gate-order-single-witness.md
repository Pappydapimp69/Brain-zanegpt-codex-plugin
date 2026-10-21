# local/sandbox-dbz-combat-gate-order-single-witness — lessons

Project: local/sandbox-dbz-combat-gate-order-single-witness. Newest first.

---

## E1 — sandbox dbz combat gate order single witness
- Date: 2026-09-29
- Project: local/sandbox-dbz-combat-gate-order-single-witness
- Tags: [testing][determinism][input][gamedev]
- What: Sandbox of a tick loop where the cancel-window gate is updated after the input read, tested under two input policies, to check whether a single test policy can witness the bug.
- Why built: sandbox-dbz-combat#E1 says the late gate hides behind a cancel-ASAP policy; august-10#E4 says one deterministic run of an order-dependent process is one witness. This seam tests them together.
- Design: Deterministic, no RNG: a move with 4 startup ticks then a 3-tick true cancel window; two step orders (read then advance = gate late, advance then read = gate correct); two policies (single press at a chosen tick, and a held press re-sampled every tick); press swept across every tick of the true window.
- Got right: With the correct order both policies accept 3/3 presses in the window with 0 latency. With the late gate the held-press policy also accepts 3/3, so a suite using only that policy passes both orderings.
- Where/why it failed: With the late gate the single-press policy drops the press on the first window tick (2/3 accepted, dropped at tick 4), and the held-press policy hides this only by accepting one tick late (latency 1 versus 0) — an unasserted delay, not a fix.
- Fix: Run the same ordering scenario under several input policies and step orders and assert both acceptance and accept latency; include a frame-perfect single-press case on the first window tick.
- Why this fix: The bug lives on exactly one tick of the window, so only a policy that presses there and does not retry can observe it; the retrying policy converts a dropped press into extra latency that no acceptance-only assertion sees.
- Rule of thumb: A green test under a retrying input policy is one witness, not proof; sweep policies and assert the latency as well as the acceptance, with a no-retry press on the first tick of every window.
- Provenance (verified/assumed): Verified first-hand by running the sandbox at ~/brainwork/sb/s6.py; figures are its observed output. A real engine's input buffering was not modelled.
- Composed: sandbox-dbz-combat/E1, august-10/E4
- Link: scheduled training pass 5, session_01NomGdXQGCMAr6o2dzv6Tp2

