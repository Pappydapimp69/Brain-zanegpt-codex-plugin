# local/sandbox-combined-dog-recursion-nan-gate-polarity — lessons

Project: local/sandbox-combined-dog-recursion-nan-gate-polarity. Newest first.

---

## E1 — sandbox combined dog recursion nan gate polarity
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-recursion-nan-gate-polarity
- Tags: [state][testing][determinism][method]
- What: A deterministic sandbox (no RNG, no wall-clock) feeding one NaN into two structurally identical distance gates — an exclude-if-far gate (`if d > R: skip`) and an include-if-near gate (`if d < R: take`) — and comparing their outputs against a healthy input set.
- Why built: dog#E38 records that a NaN fed into a `<`/`>` threshold gate never throws and collapses the gate to a constant set by the OPERATOR. recursion#E1 records that a reducer touching a newly-added nested field is one missing initializer away from poisoning it with NaN forever. Composed, the question is what a regression test proving "our NaN guard works" on one gate actually establishes about a sibling gate fed from the same poisoned field.
- Design: Four items with healthy distances (1.0, 5.0, 50.0, 500.0) and the same four with every distance replaced by NaN, run through both gate polarities at R=10.0.
- Got right: Using genuinely identical gate logic differing only in comparison direction, so the divergence is attributable to operator polarity alone rather than to any difference in guard quality between the two call sites.
- Where/why it failed: The same NaN drives the two gates to exactly opposite failures. The exclude-if-far gate admits all 4 items (every `d > R` is False under NaN, so nothing is skipped) where healthy input admits 2. The include-if-near gate admits 0 items (every `d < R` is False) where healthy input admits the same 2. Neither throws.
- Fix: Guard NaN at the value's source or at the gate's input explicitly (`isFinite` check with a defined fallback), and when writing the regression test, assert against BOTH polarities present in the codebase — a test that pins the over-inclusion direction cannot express the starvation direction and vice versa.
- Why this fix: Because NaN makes every comparison False, the failure direction is decided entirely by whether the code branches on the true or false arm. Two gates reading the same poisoned field therefore produce symptoms that look like unrelated bugs — one system processing far too much, another processing nothing — which invites two separate investigations of what is a single missing initializer.
- Rule of thumb: A NaN reaching two `<`/`>` gates of opposite polarity produces opposite symptoms from one root cause — sandbox-confirmed an exclude-if-far gate admitting 4/4 while an include-if-near gate admits 0/4 on identical poisoned input; a NaN regression test on one gate is not evidence for the other, so assert both polarities.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b1/l1.py) and confirmed exclude_if_far returns [0,1,2,3] and include_if_near returns [] on NaN input, against [0,1] for both on healthy input, with no exception raised in either case. dog#E38 and the-game-the-recursion#E1 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E38, pappydapimp69__the-game-the-recursion/E1
- Link: session_014mRpopK9xnhvk35tT8ozkX

