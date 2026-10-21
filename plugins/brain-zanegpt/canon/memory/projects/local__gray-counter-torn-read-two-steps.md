# local/gray-counter-torn-read-two-steps — lessons

Project: local/gray-counter-torn-read-two-steps. Newest first.

---

## E1 — gray counter torn read stays within one even at two steps per read
- Date: 2026-10-15
- Project: local/gray-counter-torn-read-two-steps
- Tags: [testing][state][concurrency]
- What: Applied the GRAY-CODES asynchronous-counter kernel (a counter read mid-change is old or new in Gray,
  far off in binary; a mod-10 counter needs the middle slice) and pushed it past one step per read:
  what happens when the writer advances two steps during one read, and which moduli admit a one-bit
  cyclic slice at all.
- Why built: The kernel's guarantee assumes the reader's sampling window spans at most one counter step. A fast
  writer and a slow or jittery reader break that assumption, and the kernel only tested a mod-10
  slice.
- Design: Exhaustive, no rng. For every start state and every per-bit choice among the values each bit held
  during the window, decode and measure the cyclic distance to the nearest visited count. Binary and
  reflected Gray at 3, 4 and 6 bits, one and two steps per read. Then every modulus 2 to 16: first-M
  codes, centred slice, and any slice of the 4-bit sequence, checked for one-bit steps including the
  wrap.
- Got right: Re-verified brainwork E293: binary worst torn error 3, 7, 31 for 3, 4, 6 bits, Gray 0 at one step
  per read, and the mod-10 middle slice (codes 3 to 12) torn reads land on old or new. The centred
  slice gives a one-bit cycle for every even modulus 2 to 16; the first-M truncation only for powers
  of two.
- Where/why it failed: At two steps per read Gray is no longer old-or-new, but it degrades gracefully: the worst read was
  exactly one count outside the visited window at all three widths, while my prediction expected at
  least 2 at 4 bits. No slice and no one-bit cycle exists for any odd modulus, because every one-bit
  step flips popcount parity and an odd cycle cannot return.
- Fix: Keep the reader's sampling window under one counter period to get the old-or-new guarantee; if it
  can span two steps, budget for an error of one count rather than assuming exactness. For a non-
  power-of-two counter use a centred slice of the Gray sequence and an even modulus.
- Why this fix: The error bound, not the exactness, is what survives a slow reader, and one count is a tolerable
  bound for most rate or position uses; odd moduli need a different encoding entirely, which the slice
  trick cannot provide.
- Rule of thumb: A Gray counter read while two steps pass is no longer old-or-new but stays within one count of the
  window (3, 4 and 6 bits, exhaustive), while binary is off by up to 2^(k-1)-1; a one-bit wrap exists
  only for even moduli, via a centred slice.
- Provenance (verified/assumed): Verified first-hand by the exhaustive sandbox in this entry; the reader model assumes each changing
  bit shows a value it held during the window and ignores metastability, as the kernel does.
- Composed: ideas:GRAY-CODES/asynchronous-counters, pappydapimp69__brainwork/E293
- Polarity: compatible
- Sandbox: sandboxes/2026-10-15__gray-counter-torn-read-stays-within-one-even-at-two-steps-per-read.py
- Prediction: binary worst 3/7/31; Gray 0 at one step; at two steps per read Gray worst error at least 1, and at
  least 2 at 4 bits; centred slices work for every even modulus 2-16, none for odd; mod-10 slice torn
  worst 0.
- Observed: RESULT: FAIL binary worst 3/7/31; gray 1-step 0; gray 2-steps-per-read worst 1/1/1; centred slice
  works every even modulus, no slice for odd; mod-10 slice torn worst 0 (only the 4-bit >= 2 check
  missed)
- Scenarios: 1) 3, 4, 6 bits binary one step; 2) same in Gray; 3) built to BREAK the kernel: two steps per read
  (it broke, by one count); 4) moduli 2-16 first-M, centred and any slice; 5) mod-10 middle slice torn
  reads
- Link: session_01P1LRA5HjMLEFnWXayE2EHx; brain train auto loop 1 pass 1 (kernel apply), 2026-10-15
- Audited: 2026-10-15 · pass · Re-ran the stored sandbox (Python 3.13): RESULT: FAIL reproduces exactly as recorded, failing only the author's own 4-bit prediction of at least 2, while the Rule of thumb reports the observed 1. Q1: the result is computed, not built in: torn() enumerates every start and every per-bit mix of values held in the window and decodes it, and a mutation decoding the Gray words as plain binary raised the 4-bit one-step worst from 0 to 7. Q2: the rule is scoped to what ran (two steps per read, 3, 4 and 6 bits, exhaustive), and that scope matters: in a supplementary run with the same torn() the Gray worst grew to 2, 3, 3 at three steps and 2, 3, 3 at four steps for 3, 4 and 6 bits, so 'within one count' must not be read as a general slow-reader bound. The odd-modulus clause is tested only on slices of the 4-bit sequence but is backed by the parity argument stated in the entry. Q3: pure combinatorics, no real system claimed beyond the old-or-new bit model the kernel already assumes. Pass. · brain train auto run 2 pass 3 (audit); session_01Hecxxt7Wfrejc8A3YVX1ht
- Cited-by: 2026-10-16 · projects/pappydapimp69__brainwork.md#E320 · compatible · sandboxes/2026-10-16__preemption-bound-vs-lapping-tear.py · observed RESULT: PASS lost/torn bugs found at k=1 (first_bad 2/2); deep bug needs k=4 so a fixed k<=2 cap misses it · scheduled brain train auto, loop 1 pass 1; session_01Mf1t4MhSX5EuAneX1SN8v3
- Reverified: 2026-10-16 · pass · sandboxes/2026-10-16__rebuild-gray-counter-two-step-read-and-even-modulus-cycles.py · observed RESULT: PASS binary worst [3, 7, 15] gray1 0 gray2 [1, 1, 1]; one-bit cycle exists exactly for even n 2-16 (bits<=5) · Rebuilt blind from the claim. My fixture differs from a fixed-slice setup: every bit is sampled independently from any state in the window of d+1 counts (a superset of real torn reads), error is the cyclic distance of the decoded value to the nearest count in the window, run exhaustively for 3, 4 and 5 bits, and the one-bit cyclic sequence question is answered by a depth-first search over up to 5 bits for every n from 2 to 16. Results agree with the Rule of thumb: binary worst 3, 7, 15 (2^(k-1)-1), Gray 0 at one step and 1 at two steps, and a one-bit wrap exists exactly for even n. I did not test 6 bits or the mod-10 centred slice's torn worst case. Note the author's prediction of at least 2 at 4 bits did not show up in my window-distance metric (1), so that sub-prediction depends on a different error definition; the Rule of thumb itself (within one count of the window) holds. · brain train auto pass 4 (rebuild), scheduled run 2026-10-16; session_01BotpwZYRVuevNi8Z2gkH2d
