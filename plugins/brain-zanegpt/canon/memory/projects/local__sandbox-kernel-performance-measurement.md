# local/sandbox-kernel-performance-measurement — lessons

Project: local/sandbox-kernel-performance-measurement. Newest first.

---

## E1 — a sink on the output still times nothing if the input is constant
- Date: 2026-09-28
- Project: local/sandbox-kernel-performance-measurement
- Tags: [performance][measurement][compiler][benchmark]
- What: Applied the ideas kernel that a microbenchmark can time nothing because the compiler eliminates dead code and folds constant inputs, so outputs must be consumed and inputs read from mutable state. Both failure modes reproduced in real gcc and clang output, and each half of the fix fails without the other; a third case defeats both.
- Why built: brain train gap listed the kernel as unapplied, and memory had no benchmarking entry. The kernel quotes JMH comments; it had never been checked against a compiler.
- Design: Seven benchmark loops over a 64-bit mix function (two multiplies) compiled with gcc 13.3 and clang 18.1 at -O2, reading the assembly for whether a loop survives and how many multiplies it runs per iteration. Variants: result unused; result summed from a constant input; result kept by an empty asm sink with a constant input; the same with the input also passed through an opaque asm barrier; result summed from a varying input; and a sum of i*x returned or sunk each iteration.
- Got right: Reading multiplies per iteration, not just whether a loop exists. The sink-with-constant-input case keeps a loop, which looks like success until the loop is seen to contain no multiply.
- Where/why it failed: With the result unused, or summed from a constant input, both compilers removed the loop entirely. Sinking the output with a constant input kept a loop in both but with 0 multiplies, because mix(42) was folded at compile time. Only the opaque input plus the sink, or a summed varying input, kept 2 multiplies per iteration. For a plain sum of i*x with a runtime x, clang replaced the loop with a closed form and gcc kept a loop with the multiply strength-reduced to an add, so neither timed the written operation even though the result was consumed.
- Fix: Hide both ends from the optimiser: pass the input through an opaque barrier (or read it from mutable state) and sink the output each iteration, then read the generated code once to confirm the operation survives.
- Why this fix: Dead-code elimination is stopped by consuming the output, constant folding by making the input opaque; they are independent. Loop-level rewrites such as closed forms and strength reduction can still replace the timed operation, which only reading the output code shows.
- Rule of thumb: Sinking a benchmark's output is not enough: with a constant input gcc and clang kept the loop but folded the work to 0 multiplies, and only an opaque input plus a sink kept the 2 real multiplies per iteration; a consumed sum of i*x was still turned into a closed form by clang and an add by gcc, so read the generated code before trusting the timing.
- Provenance (verified/assumed): VERIFIED first-hand in cognitive-updates/sandbox_train_gap_b05.py loop 21 in Pappydapimp69/Brain from real gcc 13.3.0 and clang 18.1.3 -O2 assembly, deterministic for those versions. Observed per variant: no loop / no loop / loop 0 mul / loop 2 mul / loop 2 mul / gcc loop 0 mul and clang no loop / loop 0 mul, identical across both compilers except the sum of i*x. JIT compilers such as the JVM's were not exercised.
- Composed: ideas:PERFORMANCE/measurement/microbenchmarking/a-microbenchmark-can-measure-nothing-and-still-report-a-number
- Link: session 2026-09-28, brain train gap batch 5 loop 21
- Sandbox: sandboxes/2026-09-28__train-gap-b05.py (backfilled 2026-09-30 from Brain/cognitive-updates/; a batch script covering several entries)
- Cited-by: 2026-10-15 · projects/pappydapimp69__brainwork.md#E290 · compatible · sandboxes/2026-10-15__batching-knee-measured-on-recycled-messages-moves-with-pool-size.py · observed RESULT: PASS recycled inputs overstate batch-128 ratio [19.2, 11.5, 5.4, 1.9] vs varied 3.37; identical shows no knee; pool P appears as a ratio jump at batch {'pool4': 8, 'pool16': 32, 'pool64': 128}; varied knee was 64 (predicted <=16, m… · brain train auto loop 2 pass 2; session_01Kx9Pq1H5qpcbvZJ9u2DPKR
