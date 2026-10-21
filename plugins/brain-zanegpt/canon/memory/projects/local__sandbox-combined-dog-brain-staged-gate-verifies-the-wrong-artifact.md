# local/sandbox-combined-dog-brain-staged-gate-verifies-the-wrong-artifact — lessons

Project: local/sandbox-combined-dog-brain-staged-gate-verifies-the-wrong-artifact. Newest first.

---

## E1 — sandbox combined dog brain staged gate verifies the wrong artifact
- Date: 2026-08-29
- Project: local/sandbox-combined-dog-brain-staged-gate-verifies-the-wrong-artifact
- Tags: [process][verification][tooling][testing]
- What: A deterministic sandbox (no RNG, no wall-clock) running a pre-push hash gate against payloads of four sizes through a transport that silently truncates above a byte threshold, comparing the gate's verdict with what actually landed at the destination.
- Why built: dog#E36 records that a local pre-push hash/diff gate verifies the STAGED file rather than the separate tool call that performs the push, and that at large payload sizes the two can diverge with no error. brain#E21 records that a self-reported "N pushed, 0 held" is not a promotion, and that the remedy is reading the destination. This tests whether the two describe one failure and whether E21's remedy is what actually discriminates.
- Design: Payloads of 1KB, 100KB, 300KB and 500KB. The staged gate hashes the payload against the intended content — the check dog#E36 describes — and always passes, since the staged artifact is by construction what was intended. A transport truncates anything above 250KB. Destination state is then hashed independently.
- Got right: Modeling the gate as genuinely correct on its own terms (it really does verify the staged bytes against intent) rather than as a buggy check, which is what makes the result about verification scope rather than about a defective hash.
- Where/why it failed: The gate reports "pushed, 0 held" at all four sizes, including 300KB and 500KB where the payload did not land intact. The gate is not wrong about anything it examined; it simply never examined the delivered artifact. A reviewer reading its output has a green signal that is entirely truthful and entirely uninformative about the outcome.
- Fix: Verify by hashing what is at the DESTINATION after the push, not the staged input before it — brain#E21's remedy — and treat any gate whose input is the same artifact the caller supplied as a check on intent rather than on delivery.
- Why this fix: dog#E36's divergence and brain#E21's async-acceptance gap are the same structural fault seen at two layers: in both cases a verification step reads an artifact upstream of the boundary that can actually fail. Size-dependence makes it worse than a plain blind spot, because every small test payload passes end-to-end and establishes false confidence in the gate before a real payload crosses the threshold.
- Rule of thumb: A pre-push gate that hashes the staged artifact verifies intent, not delivery — sandbox-confirmed it reports "pushed, 0 held" at 300KB and 500KB where the transport silently truncated, while passing honestly at small sizes; hash the destination after the push (brain#E21), and distrust any gate whose input is the caller's own artifact.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b2/l6.py) and confirmed the staged gate passes at 1KB, 100KB, 300KB and 500KB while destination hashes match only at 1KB and 100KB, with silent truncation at the two larger sizes. dog#E36 and brain#E21 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__dog/E36, pappydapimp69__brain/E21
- Link: session_014mRpopK9xnhvk35tT8ozkX

