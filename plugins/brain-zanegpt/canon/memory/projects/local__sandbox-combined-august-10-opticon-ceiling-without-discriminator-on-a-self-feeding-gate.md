# local/sandbox-combined-august-10-opticon-ceiling-without-discriminator-on-a-self-feeding-gate — lessons

Project: local/sandbox-combined-august-10-opticon-ceiling-without-discriminator-on-a-self-feeding-gate. Newest first.

---

## E1 — sandbox combined august 10 opticon ceiling without discriminator on a self feeding gate
- Date: 2026-08-29
- Project: local/sandbox-combined-august-10-opticon-ceiling-without-discriminator-on-a-self-feeding-gate
- Tags: [tooling][process][verification][method]
- What: A deterministic sandbox (fixed tension keyword table and diff text, no RNG) running a commit gate that scans both the diff and the commit message, with realistic acknowledgement prose fed back as the next round's input, under no ceiling and under a retry ceiling.
- Why built: august-10#E11 records that a commit gate scanning the MESSAGE as well as the diff matches on the acknowledgement text it just demanded, producing new matches from the ack prose alone and forcing extra attempts; it prescribes excluding that response from the scan or imposing a round ceiling. opticon#E27 records that a verified "just retry it" remedy needs both an explicit CEILING and a DISCRIMINATOR. This tests what the ceiling alone actually buys on E11's self-feeding loop.
- Design: Five tensions with distinct keywords and a realistic rationale sentence each — explaining why one tension is acknowledged naturally uses vocabulary belonging to others, which is E11's actual mechanism. The gate loops until a round produces no new matches, run with message scanning on and off, and with and without a 3-round ceiling.
- Got right: An initial construction did not reproduce because the ack prose only restated each tension's own keyword and converged in two rounds; replacing it with rationale text that references neighbouring concerns reproduced the escalation E11 describes rather than a contrived one.
- Where/why it failed: Message scanning escalates a 2-round commit into 4 rounds and 2 acknowledged tensions into 5 — each acknowledgement supplies the keywords the next scan matches on. opticon#E27's ceiling does terminate the loop at 3 rounds, but it reports the identical "CEILING" outcome whether the cause is this self-feeding loop or a genuine unacknowledged tension, so the operator learns only that the gate gave up.
- Fix: Pair the ceiling with the discriminator opticon#E27 also requires, and here the discriminator is available for free — record whether each new match came from the DIFF or from the MESSAGE. Matches originating only in the message are the self-feed and should not count; matches in the diff are real.
- Why this fix: august-10#E11's two prescriptions are not equivalent. Excluding the response from the scan removes the loop; a round ceiling only bounds it, converting an unbounded retry into a bounded failure that still cannot be distinguished from a legitimate refusal. opticon#E27 already names exactly what is missing, and this composition shows the ceiling half being adopted without the discriminator half produces a gate that fails safe but uninformatively.
- Rule of thumb: A round ceiling on august-10#E11's self-feeding commit gate bounds the loop without explaining it — sandbox-confirmed message scanning turns a 2-round commit into 4 rounds and 5 acked tensions, while a 3-round ceiling reports "CEILING" identically for the self-feed and for a genuine unacked tension; record each match's origin (diff vs message) as opticon#E27's discriminator.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b6/l17.py), including a first construction whose ack prose did not introduce new keywords and converged in 2 rounds; confirmed message scanning yields 4 rounds and 5 acked tensions against 2 and 2 without it, and that a 3-round ceiling fires with outcome CEILING. august-10#E11 and opticon#E27 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__august-10/E11, pappydapimp69__opticon/E27
- Link: session_014mRpopK9xnhvk35tT8ozkX

