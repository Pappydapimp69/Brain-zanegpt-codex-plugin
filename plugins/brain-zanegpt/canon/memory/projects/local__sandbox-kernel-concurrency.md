# local/sandbox-kernel-concurrency — lessons

Project: local/sandbox-kernel-concurrency. Newest first.

---

## E6 — release acquire chain transitive
- Date: 2026-10-12
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][correctness][memory-model]
- What: Re-verified the happens-before kernel from a new angle: transitivity. sandbox-kernel-concurrency/E3
  showed a plain flag may never be re-read; its fix said to publish DATA with release/acquire because volatile
  orders nothing else, but it only tested the flag. This tests whether visibility carries through a three-thread
  chain of release/acquire hops, and whether a single weak hop breaks the whole chain.
- Why built: brain train loop concurrency pass on ideas:CONCURRENCY/happens-before, which has one source entry.
  E3 looked at compiler output for one flag. The ordering of OTHER data, and how hb composes across a relay
  thread, were stated but not tested.
- Design: An exhaustive axiomatic model of an RC11 fragment in stdlib Python, with no RNG and no threads. Every
  reads-from choice is enumerated. hb is built from sb, init, and sw (a release write read by an acquire read),
  then closed transitively. Executions that break coherence or acyclicity are dropped. Programs: 2-thread
  message passing (data=1; f1=1 | read f1; read data), and a 3-thread chain (T1 data=1, f1=1 | T2 read f1,
  f2=1 | T3 read f2, read data). hb is also computed as vector clocks joined along sb and sw, and compared
  with the closure on every event pair.
- Got right: Weakening each of the four chain annotations one at a time, instead of only comparing all-strong
  with all-relaxed. That showed every hop is load-bearing. The checker was negative-controlled twice: with the
  coherence rule off, the strong chain shows the stale read; with sw edges dropped from the vector clock, it
  disagrees with the closure on 136 pairs.
- Where/why it failed: Message passing with a relaxed flag, which behaves like volatile (it reloads but orders
  nothing), allowed 1 stale execution out of 4 (flag seen as 1, data read as 0). Release/acquire allowed 0 out
  of 3. The full release/acquire chain allowed 0 stale out of 7. Making any ONE of the four ordering annotations
  relaxed (f1 store, f1 load, f2 store, f2 load) brought back exactly 1 stale out of 8 consistent executions. The
  relay thread never touches data, yet it carries T1's write to T3 only when it both acquires and releases.
- Fix: When data goes through a relay (a worker that hands off to another worker), every hop needs a release
  store matched by an acquire load, or an acq_rel RMW. Audit each hop. Checking only the first producer and
  the final consumer is not enough.
- Why this fix: hb is the transitive closure of sb and sw, and an sw edge exists only for a release write that
  an acquire read reads from. One relaxed side removes that edge, so the path from T1's data write to T3's read
  is gone. Nothing else in the chain stands in for it, even though every flag value is still observed.
- Rule of thumb: Visibility through a release/acquire relay is transitive: in a 3-thread chain where only T1
  writes data, rel/acq on both hops allowed 0 stale reads out of 7 executions, but making ANY one of the 4
  annotations relaxed allowed a stale read (1 of 8 each), and so did a relaxed or volatile-style flag in plain
  message passing (1 of 4), so audit every hop; vector clocks joined on acquire matched the hb closure on
  3678 of 3678 pairs.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry: exhaustive enumeration, deterministic, with both
  negative controls run (coherence rule off gives stale=1 on the strong chain; vector clock without sw edges
  gives 136 mismatches and a FAIL).
  Assumptions, kept separate: the model is an RC11-style axiomatic fragment with one write per location, so
  modification order is trivial. Real hardware and compilers were outside this run. Data is modelled as a
  plain location whose stale read is a legal outcome, where C11 would call that a data race (UB), which is
  worse.
- Composed: sandbox-kernel-concurrency/E3, ideas:CONCURRENCY/memory-model/happens-before
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__release-acquire-chain-transitive.py
- Prediction: Written before the first run. Chain all rel/acq: 0 stale. Each of the 4 single weakenings: exactly
  1 stale. MP rel/acq: 0. MP relaxed: 1. Vector clock agrees with closure on 100% of pairs. Negative control
  (coherence off) shows stale above 0 on the strong chain.
- Observed: RESULT: PASS stale reads s1=0 s2=1 s3=0 s4=1 s5=1 s6=1 s7=1 s8=1; vc==closure 3678/3678.
  Consistent executions: MP rel/acq 3, MP relaxed 4, chain strong 7, each weakened chain 8.
- Scenarios: 1) MP rel/acq; 2) MP relaxed flag, volatile-like; 3) chain all rel/acq; 4) BREAK f1 store relaxed;
  5) BREAK f1 load relaxed; 6) BREAK f2 store relaxed; 7) BREAK f2 load relaxed; 8) negative control: strong
  chain with the coherence check off (built to show a stale read)
- Link: session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E147 · compatible · sandboxes/2026-10-12__acquire-release-does-not-stop-store-buffering.py · observed RESULT: PASS 3/3; release store fenced gcc/clang False/False, seq_cst True/True; r1=r2=0 relaxed 2827 acqrel 3909 seqcst 0 of 200000 · session; brain train follow-up (aim: happens-before single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E5 — print lock does not hide race
- Date: 2026-10-12
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][correctness][debugging][scheduling]
- What: Tested the assumption sandbox-kernel-concurrency/E1 left open: that a print hides a race through the
  print's own internal lock. A probe that acquires and releases its own shared lock inside the load..store
  window of an unprotected increment did not hide the race. It left every wrong outcome reachable and, under
  a scheduler that rarely preempts, raised the lost-update rate instead of lowering it.
- Why built: E1 measured a lock-free probe inside and outside the window and marked the print-lock mechanism
  as assumed. E93 tested lock scope over check-then-act, not a lock that covers only an unrelated part of the
  window. That gap is the usual explanation for why adding logging makes a race go away.
- Design: Two threads each do K=2 increments (load, then store of the loaded value plus one) on a shared counter. There are four
  variants: no probe; a plain 3-step probe between load and store; the same probe wrapped in acquire/release
  of a shared print lock; and a lock spanning load..store. A memoised DP counts every legal schedule (a blocked
  acquire is not runnable) and computes the exact lost-update probability under a uniform-random scheduler and
  under a sticky scheduler that switches threads with q=0.01 per step. There is no RNG and no real timing.
- Got right: Computing exact probabilities under two scheduler shapes instead of only listing reachable
  outcomes. With the reachable set alone the lock probe looks the same as no lock. The sticky scheduler shows
  the lock pushing the result the opposite way from the heisenbug story.
- Where/why it failed: The lock probe still reached final values {2,3,4}, the same as the no-probe and plain-probe cases
  (62230 of 62236 schedules lose an update). Its uniform-scheduler failure probability was 0.9999 against
  0.9979 for the plain probe. Under the sticky scheduler it was 0.114 against 0.078 for the plain probe and
  0.020 for no probe. A thread blocked on the print lock forces a switch back to the holder, which then
  stores while the blocked thread is still holding a stale load. Only the lock spanning load..store gave {4}
  with probability 0.
- Fix: Do not read "it stopped failing once I added logging" as evidence that the logging's lock serialized
  the race. A lock that covers only part of the window cannot remove a wrong outcome. Fix the race with a
  lock or atomic covering the whole read-modify-write, and use logging only to widen the window.
- Why this fix: Mutual exclusion only orders the code inside the critical section. The load and the store sit
  outside the print lock, so every bad interleaving survives. Blocking on that lock is itself a forced
  context switch at the worst moment, inside the window.
- Rule of thumb: A probe that takes its own lock inside a load..store window does not hide the race: final values {2,3,4} stayed reachable, and with rare preemption (q=0.01) it raised lost updates from 7.8% to 11.4%, because blocking on the probe's lock forces a switch inside the window; only a lock spanning load..store gave 0.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry
  (2026-10-12__print-lock-does-not-hide-race.py), with exact DP over every schedule and no randomness.
- Assumptions outside the model: a real printf may also hide a race through its long duration, syscalls
  or cache effects. This sequential-consistency model does not include those. It rules out only the lock
  mechanism as the cause.
- Composed: sandbox-kernel-concurrency/E1, ideas:CONCURRENCY/race-conditions
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__print-lock-does-not-hide-race.py
- Prediction: Final values {2,3,4} stay reachable for no-probe, plain-probe and lock-probe, and the spanning
  lock gives {4}. Under the uniform scheduler, lock-probe P(bad) is within 10 pp of plain-probe. Under the
  sticky q=0.01 scheduler, lock-probe P(bad) >= plain-probe.
- Observed: RESULT: PASS lockprobe finals=[2, 3, 4] P_uni=1.000 vs plain 0.998; sticky 0.1141 vs 0.0776;
  span finals=[4] P=0. Schedules counted: none 70 (64 bad), plain 184756 (184750 bad), lockprobe 62236
  (62230 bad), span 6 (0 bad). Sticky: none 0.0200.
- Scenarios: 1) no probe (baseline, 70 schedules); 2) plain probe inside window; 3) probe taking its own
  shared lock inside the window, under the uniform and sticky schedulers; 4) BREAK case: a lock spanning
  load..store, the one placement where locking does hide the race, which would falsify the claim if the
  probe's lock behaved like it.
- Link: session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E149 · compatible · sandboxes/2026-10-12__preemption-bounded-search-finds-races-stress-misses.py · observed RESULT: FAIL 1/3; 2x3 first lost update at schedule 3, all 5 results by schedule 1171, min preemptions {2: 4, 3: 1, 4: 2, 5: 2, 6: 0}; 3x2 min preemptions {2: 1, 3: 2, 4: 1, 5: 2, 6: 0} · session; brain train follow-up (aim: race-conditions single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E4 — aba tag wraps on increments not head changes
- Date: 2026-10-12
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][lock-free][correctness][data]
- What: Re-verified the ABA tag-width lesson by exhaustive adversarial schedules instead of
  random stalls, and under a second counter policy. With a tag bumped on every head change the
  E2 rule held exactly; with a tag bumped only on push, corruption appeared at odd change counts,
  so the wrap predicate is the counter's own increments mod 2^k, not the number of head changes.
- Why built: sandbox-kernel-concurrency/E2 measured the wrap boundary with seeded random stalls
  and a single counter policy (bump on every head change). Random sampling cannot show a count is
  exactly zero, and the rule's wording names head changes, which is only true for that policy.
- Design: Treiber stack over a 5-node pool, initial stack X,Y,Z with P,Q free. Thread A snapshots
  head X, next Y and the tag, then stalls; the adversary runs EVERY sequence of L ops (pop, or
  push of any free node, so freed nodes recycle), L=1..12, counted exactly with a DP over (stack,
  pushes). A corrupt success is a CAS that matches while X's real successor is not Y. Tags of
  0-3 bits under per-change and push-only counters; a negative control checks the untagged case.
- Got right: Counting all schedules exactly rather than sampling, so the zero cells are real zeros,
  and adding a second counter policy as the scenario built to break the head-change wording.
- Where/why it failed: Per-change tag: corrupt successes equalled the untagged count at every L that
  is a multiple of 2^k (L=4: 5, L=8: 930, L=12: 123783) and were exactly 0 elsewhere; minimum
  adversary length 3 untagged, 4 for 1 and 2 bits, 8 for 3 bits. Push-only 1-bit tag corrupted at
  every odd L (3, 5, 7, 9, 11; first at L=3 via pop X, push P, push X), and its 2-bit tag first
  failed at L=6, not 4. My pre-registered guess that the first odd hit was L=5 was wrong.
- Fix: State the sizing rule in counter increments: the tag must not wrap within the maximum number
  of increments one stall can see. For a push-only counter count pushes, not head changes, and note a
  3-op pop, push, push already defeats a 1-bit push-only tag.
- Why this fix: The CAS compares the tag value, and the tag value only knows how many times IT was
  bumped; which operations bump it decides which adversary schedules wrap it, so the sizing bound has
  to be stated against the same events the counter counts.
- Rule of thumb: An ABA tag wraps on its OWN increments mod 2^k, not on head changes: exhaustive
  schedules gave a per-change tag exactly the untagged corrupt count at L%2^k==0 (930 at L=8) and 0
  elsewhere, but a push-only 1-bit tag corrupted at every odd L from 3, so size by what bumps it.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry: exhaustive
  deterministic enumeration of every adversary schedule up to length 12, all counts above copied
  from its output.
- Assumptions: a sequential model with one stalled popper; real hardware memory ordering, multiple
  concurrent poppers and node reclamation schemes are outside this model.
- Composed: sandbox-kernel-concurrency/E2, ideas:CONCURRENCY/lock-free/definition-and-aba
- Polarity: compatible
- Sandbox: sandboxes/2026-10-12__aba-tag-wraps-on-increments-not-head-changes.py
- Prediction: (written before the run) 1) per-change k-bit tag: corrupt == untagged when L%2^k==0,
  else exactly 0. 2) minimal defeating L: untagged 3, 1-bit 4, 2-bit 4, 3-bit 8. 3) push-only
  counter: 1-bit corrupts at odd L with the first odd hit at L=5; 2-bit min defeating L=6.
- Observed: RESULT: FAIL per-change wraps only at L%2^k==0 (=untagged there), min L {0: 3, 1: 4,
  2: 4, 3: 8}; push-only 1-bit corrupts at odd L [3, 5, 7], min L {1: 3, 2: 6, 3: None}. The FAIL
  is only my first-odd-L=5 guess (actual 3); predictions 1, 2 and the push-only 2-bit L=6 held.
  Totals over L<=12: untagged 178192, per-change 1/2/3-bit 135659/124718/930, push-only
  93738/5843/0.
- Scenarios: 1) per-change tag, 1-3 bits, all schedules L=1..12: zero except at multiples of 2^k,
  equal to untagged there; 2) minimum adversary length per width; 3) BREAK: push-only counter,
  corrupting schedules at odd L contradict the head-change wording; 4) total corrupt schedules per
  policy and width; negative control: untagged predicate must see corruptions.
- Link: session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E148 · compatible · sandboxes/2026-10-12__gc-stops-aba-only-for-references-not-pools-or-indices.py · observed RESULT: PASS 3/3; corrupt of 62: gc 0 pool(fifo) 6 index 6 tag4 0 pool-lifo 0; gc-repush 22 of 363 · session; brain train follow-up (aim: definition-and-aba single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E3 — a plain flag spin wait hangs under gcc and vanishes under clang
- Date: 2026-09-28
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][compiler][correctness][c]
- What: Applied the ideas kernel that without a happens-before edge a write may never become visible to another thread, so a plain flag can legally fail and passing tests prove nothing. The kernel quotes the Java spec; the same failure appeared in real C compiler output, in two different forms from the same source.
- Why built: brain train gap listed the kernel as unapplied, and memory had no memory-model entry. Reading compiler output gives deterministic evidence without timing a race.
- Design: Four C functions: spin while a plain int flag is zero, the same with volatile, the same with a C11 atomic acquire load, and a plain spin that counts iterations. Each compiled by gcc 13.3 and clang 18.1 at -O0 and -O2; the assembly was read for whether the loop survives and how many flag loads it performs per iteration.
- Got right: Comparing -O0 with -O2. The debug build does exactly what the source says, which is why a plain flag passes testing.
- Where/why it failed: At -O0 both compilers reloaded the plain flag every iteration. At -O2, gcc loaded it once and compiled the wait into a jump to itself that never reloads, so a thread waiting on a flag set elsewhere spins forever. clang at -O2 deleted the wait loop entirely and returned at once, so the caller proceeds without waiting at all. The counting variant compiled to a jump to itself under both compilers at -O2. The volatile and atomic-acquire versions reloaded the flag every iteration under both compilers at both levels.
- Fix: Signal across threads with an atomic (release store, acquire load) or a lock, never a plain variable; volatile keeps the reload but gives no ordering for other data, so publish data with release/acquire.
- Why this fix: The compiler may assume a plain variable is not changed by another thread, so it can hoist or drop the read; an atomic acquire load creates the happens-before edge and forces the read.
- Rule of thumb: A spin-wait on a plain flag reloads it at -O0 but not at -O2, where gcc turns it into a jump-to-self that never re-reads (hangs) and clang deletes the loop and returns at once (never waits), so the same source fails in opposite directions by compiler; an atomic acquire load re-read the flag every iteration under both.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b08.py loop 40 in Pappydapimp69/Brain from real gcc 13.3.0 and clang 18.1.3 assembly, deterministic for those versions, cross-checked by hand on clang's -O2 output (spin_plain compiles to a bare ret). The Java memory model itself was not exercised; C11's rules stand in for it.
- Composed: ideas:CONCURRENCY/memory-model/happens-before/without-a-happens-before-edge-a-write-may-never-become-visible
- Link: session 2026-09-28, brain train gap batch 8 loop 40
- Sandbox: sandboxes/2026-09-28__train-gap-b08.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-concurrency.md#E6 · compatible · sandboxes/2026-10-12__release-acquire-chain-transitive.py · observed RESULT: PASS stale reads s1=0 s2=1 s3=0 s4=1 s5=1 s6=1 s7=1 s8=1; vc==closure 3678/3678. Consistent executions: MP rel/acq 3, MP relaxed 4, chain strong 7, each weakened chain 8. · session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E147 · compatible · sandboxes/2026-10-12__acquire-release-does-not-stop-store-buffering.py · observed RESULT: PASS 3/3; release store fenced gcc/clang False/False, seq_cst True/True; r1=r2=0 relaxed 2827 acqrel 3909 seqcst 0 of 200000 · session; brain train follow-up (aim: happens-before single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E2 — an aba tag fails when stall changes are a multiple of its range
- Date: 2026-09-28
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][lock-free][correctness][data]
- What: Applied the ideas kernel defining lock-free as a progress guarantee and naming the ABA problem. Both reproduced in a Treiber stack model, and the usual ABA fix, a version tag beside the head pointer, has a sharp boundary set by its width.
- Why built: brain train gap listed the kernel as unapplied. sandbox-combined-audio-realtime/E1 covered a lock-free SPSC queue's work budget, not ABA or the progress claim.
- Design: A stack of 4 nodes with a head pointer and an n-bit tag incremented on every head change. Thread A reads head, tag and next to pop, then stalls while thread B runs 2, 6, 16, 40 or 256 random pushes and pops that recycle freed nodes; then A's CAS runs. A corrupt success is a CAS that matches but leaves a head that differs from a correct pop. 4000 seeded stalls per cell, tags of 0, 1, 2, 4 and 8 bits. Separately, 4 threads round-robin for 4000 steps with thread 0 suspended mid-operation, once holding a mutex and once between its read and its CAS.
- Got right: Sweeping stall length past each tag's range. At the stall lengths first tried (2, 6, 40) a 4-bit tag looked sufficient.
- Where/why it failed: With no tag, corrupt CAS successes per 4000 stalls were 0, 4, 53, 69 and 26 for the five stall lengths. A tag stopped them only when the number of head changes during the stall was not a multiple of 2^bits: 4 bits removed all 69 at 40 changes but none of the 53 at 16, and 8 bits held until 256 changes, where all 26 came back. With thread 0 suspended, the other threads finished 0 operations while it held the mutex and 1500 with the CAS version.
- Fix: Size the tag so that no possible stall can see 2^bits head changes (a full-width counter, or pointer-plus-counter on a double-width CAS), or reclaim nodes with a scheme that forbids reuse while a reader holds them.
- Why this fix: A wrapped tag is indistinguishable from an unchanged one, so it fails deterministically at exact multiples of its range, and the longest stall, not the typical one, sets the needed width.
- Rule of thumb: A version tag against ABA fails exactly when the head changed a multiple of 2^bits times during the stall: a 4-bit tag removed all 69 corrupt CAS successes at 40 changes but none of 53 at 16, and 8 bits failed all 26 at 256, so size it for the longest possible stall; the lock-free version kept others progressing through a suspension (1500 ops vs 0 for a held mutex).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b02.py loop 10 in Pappydapimp69/Brain, deterministic seeded operations. Observed: untagged 0/4/53/69/26 corrupt per 4000 stalls; 4-bit tag 0 at 40 and 53 at 16; 8-bit 0 through 40 and 26 at 256; suspension 0 versus 1500 ops. Assumed: real hardware adds memory-ordering effects this sequential model does not include.
- Composed: ideas:CONCURRENCY/lock-free/definition-and-aba/lock-free-is-a-progress-guarantee-not-just-the-absence-of-a-mutex
- Link: session 2026-09-28, brain train gap batch 2 loop 10
- Sandbox: sandboxes/2026-09-28__train-gap-b02.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-concurrency.md#E4 · compatible · sandboxes/2026-10-12__aba-tag-wraps-on-increments-not-head-changes.py · observed RESULT: FAIL per-change wraps only at L%2^k==0 (=untagged there), min L {0: 3, 1: 4, 2: 4, 3: 8}; push-only 1-bit corrupts at odd L [3, 5, 7], min L {1: 3, 2: 6, 3: None}. The FAIL is only my first-odd-L=5 guess (actual 3); predictions 1,… · session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E148 · compatible · sandboxes/2026-10-12__gc-stops-aba-only-for-references-not-pools-or-indices.py · observed RESULT: PASS 3/3; corrupt of 62: gc 0 pool(fifo) 6 index 6 tag4 0 pool-lifo 0; gc-repush 22 of 363 · session; brain train follow-up (aim: definition-and-aba single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ

## E1 — a lost update hides under rare preemption and probes shift its rate
- Date: 2026-09-28
- Project: local/sandbox-kernel-concurrency
- Tags: [concurrency][correctness][debugging][scheduling]
- What: Applied the ideas kernel that a race condition is a timing-dependent outcome rather than a bad input, so passing runs carry little evidence. The claim reproduced, and the sandbox put numbers on how many clean runs a real race can produce and on which direction instrumentation moves it.
- Why built: brain train gap listed the kernel as unapplied. garden/E3 recorded a real check-then-insert race; no entry measured how rarely such a race shows up under test.
- Design: Two threads each run K unprotected increments as load, inc, store on a shared counter. First every interleaving for K=1..3, all from the same input. Then K=20 under a preemptive scheduler that switches thread with probability p per step (0.2, 0.01, 0.001), with 0 or 50 steps of unrelated work before each increment, 3000 seeded runs each. Then a 5-step log call placed inside the load..store window, or outside it.
- Got right: Placing the probe in two places. A single placement would have produced one direction and generalised it.
- Where/why it failed: The same input gave 2 final values for K=1, 3 for K=2 and 5 for K=3 across 20, 924 and 48620 interleavings. Under the scheduler, the failure rate per run was 100% at p=0.2, 35.3% at 0.01 and 4.4% at 0.001; at 4.4% it takes about 68 runs to have 95% odds of seeing one failure. Unrelated work before each increment barely changed rates (4.8% at 0.001). A log call inside the load..store window raised the rate from 39.9% to 84.6%; the same call outside the window left it at 40.5%.
- Fix: Treat a green run as no evidence about a suspected race; make the shared step atomic or locked. When instrumenting to reproduce, put the probe inside the suspected window, which widens it, instead of outside.
- Why this fix: The race's visibility is set by how often preemption lands inside a 2-step window, which a test run does not control; a probe that widens the window turns a rare failure into a common one.
- Rule of thumb: An unprotected load-inc-store gives 5 different results from one input across its 48620 interleavings, yet with rare preemption (p=0.001 per step) only 4.4% of runs lose an update, about 68 runs for 95% odds of one failure; a probe inside the load..store window doubled the failure rate (39.9% to 84.6%) while the same probe outside left it unchanged (40.5%).
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b02.py loop 8 in Pappydapimp69/Brain, deterministic seeded scheduler. Observed: outcome sets per K, run failure rates 100/35.3/4.4% (work 0) and 78.6/39.9/4.8% (work 50), probe inside 84.6% and outside 40.5%. Assumed: the classic heisenbug where printing hides a race comes from the print's own locking, which this model does not include.
- Composed: ideas:CONCURRENCY/correctness/race-conditions/a-race-condition-is-a-timing-dependent-outcome-not-a-bad-input
- Link: session 2026-09-28, brain train gap batch 2 loop 8
- Sandbox: sandboxes/2026-09-28__train-gap-b02.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-08 · projects/pappydapimp69__brain.md#E93 · compatible · sandboxes/2026-10-08__check-then-act-lock-scope.py · observed RESULT: PASS oversell interleavings none=4/6 check-only=20/70 act-only=60/70 whole=0/70 · brain train pass 2
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-concurrency.md#E5 · compatible · sandboxes/2026-10-12__print-lock-does-not-hide-race.py · observed RESULT: PASS lockprobe finals=[2, 3, 4] P_uni=1.000 vs plain 0.998; sticky 0.1141 vs 0.0776; span finals=[4] P=0. Schedules counted: none 70 (64 bad), plain 184756 (184750 bad), lockprobe 62236 (62230 bad), span 6 (0 bad). Sticky: none 0.0… · session; brain train loop (concurrency pass); session_01QGT1LfmPHPG99JEGaPhBwB
- Cited-by: 2026-10-12 · projects/pappydapimp69__brain.md#E149 · compatible · sandboxes/2026-10-12__preemption-bounded-search-finds-races-stress-misses.py · observed RESULT: FAIL 1/3; 2x3 first lost update at schedule 3, all 5 results by schedule 1171, min preemptions {2: 4, 3: 1, 4: 2, 5: 2, 6: 0}; 3x2 min preemptions {2: 1, 3: 2, 4: 1, 5: 2, 6: 0} · session; brain train follow-up (aim: race-conditions single-source edge); session_01KGZvxv8BDgpDMRFTYMfJoJ
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E217 · compatible · sandboxes/2026-10-14__ddmin-on-a-flaky-failure-needs-repeats.py · observed RESULT: PASS ddmin exact 1.00 at p=1; 0.00 at p=0.044 x1 run; 1.00 x20; 1.00 x68 · brain train auto loop 2 pass 1, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU
