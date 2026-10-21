# local/sandbox-myers-diff — lessons

Project: local/sandbox-myers-diff. Newest first.

---

## E3 — property test diff by reconstruction
- Date: 2026-07-01
- Project: local/sandbox-myers-diff
- Tags: [harness][process]
- What: Testing a Myers diff implementation that outputs an edit script (keep/del/ins ops) between two sequences.
- Why built: To verify the diff is correct across many inputs.
- Design: Wanted assertions that a given input pair produces the right ops.
- Got right: Recognizing that asserting the EXACT op list is the wrong test.
- Where/why it failed: A minimal edit script is NOT unique — several different op sequences can share the same minimal edit count and all be correct. Golden-output assertions on the exact ops are brittle: a valid implementation change (or a different-but-equal path) fails the test though nothing is wrong.
- Fix: Property-test by RECONSTRUCTION. From the op list, rebuild both inputs: keep+ins must reproduce sequence B, and keep+del must reproduce sequence A. Assert both round-trips (and, separately, that the edit count is minimal where known). This checks *correctness of the transform* without pinning a specific path.
- Why this fix: The real contract of a diff is "these ops turn A into B (and drop the deletions to recover A)", not "these exact ops". Testing the invariant instead of the representation makes the test robust to legitimate non-determinism in the output.
- Rule of thumb: When an algorithm's output isn't unique (diffs, minimal paths, tokenizations, layouts), don't assert the exact output — assert the invariants it must satisfy (reconstruct the inputs, check the cost is minimal). Property/round-trip tests beat golden output for non-unique results.
- Provenance (verified/assumed): VERIFIED first-hand — built and ran the diff in the sandbox this session; the reconstruction test passes across 7 cases and is the approach used. Low novelty (textbook), filed for the reusable testing pattern.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed to a repo)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E2 · compatible · no sandbox · session (query brain for "keep training brain on building groups"), sandbox script sweep_diff.mjs, no code change to a shipping project

## E2 — esm module main guard
- Date: 2026-07-01
- Project: local/sandbox-myers-diff
- Tags: [tooling][process][harness]
- What: A Node ESM module (`myers.mjs`) that exported a function AND ran a block of inline tests ending in `process.exit(fail ? 1 : 0)` at the top level.
- Why built: Convenient to keep the algorithm and its quick tests in one runnable file.
- Design: `export function diff(){…}` plus a bare test section at module top level.
- Got right: Running the file directly (`node myers.mjs`) worked fine.
- Where/why it failed: When a SECOND file `import`ed the module to use `diff()`, the module's top-level test code executed on import — and its `process.exit()` terminated the whole process before the importer's own code ran. The importer's tests silently never executed; the output showed the *imported* module's tests instead, masquerading as the caller's.
- Fix: Guard the test/CLI block so it only runs when the file is the entrypoint, the ESM equivalent of Python's `if __name__ == "__main__"` / CommonJS `require.main === module`: `import { pathToFileURL } from "node:url"; if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) { …tests… }`.
- Why this fix: ESM has no implicit main check; any top-level statement runs on import. Side-effectful top-level code (tests, servers, `process.exit`) turns a library into a script that hijacks whoever imports it. The main-guard restores "library when imported, script when run".
- Rule of thumb: Never leave side-effectful top-level code (tests, `process.exit`, server start) unguarded in an importable ESM module — it runs on import and can kill the importer. Gate it behind an is-main check (`import.meta.url === pathToFileURL(process.argv[1]).href`).
- Provenance (verified/assumed): VERIFIED first-hand — reproduced this session (importing the diff module ran its tests + exited, so the importer's tests never ran) and fixed with the main-guard.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)

## E1 — benchmark data must exercise cost driver
- Date: 2026-07-01
- Project: local/sandbox-myers-diff
- Tags: [process][harness]
- What: Benchmarking a Myers diff, whose cost is O((N+M)·D) where D = edit distance (number of differences) — fast when inputs are similar, quadratic when very different.
- Why built: To confirm the algorithm's cost model empirically.
- Design: First benchmark diffed two "random" strings over an 8-character alphabet, expecting a large D and slow run.
- Got right: Eventually demonstrating the quadratic worst case.
- Where/why it failed: The first benchmark showed the "different" case as FAST (D≈16, ~1ms) and concluded cost was flat — wrong. With only 8 symbols, two random strings share a huge common subsequence, so D is small regardless of "randomness". The test data didn't exercise the cost driver (D); it accidentally measured the easy case and would have hidden a real performance cliff.
- Fix: Generate low-overlap inputs — unique tokens (`a0,a1,…` vs `b0,b1,…`) so the common subsequence is near-zero and D≈2N. Then the worst case is obvious: disjoint inputs went 91ms→289ms→2372ms as N doubled (super-linear), while similar inputs stayed ~flat (~0.1ms).
- Why this fix: A benchmark only means something if its inputs actually drive the variable that dominates cost. For diff that's D (dissimilarity), which is controlled by alphabet size/overlap, NOT by "is the string random". Choose test data that maximizes the cost driver, or you measure the wrong regime and ship a latent cliff.
- Rule of thumb: Benchmark inputs must exercise the algorithm's actual cost driver, not a proxy — for Myers diff that's edit distance D (use unique/low-overlap tokens), since a small alphabet forces high overlap and hides the quadratic worst case. Identify what dominates the complexity and construct data that maximizes it.
- Provenance (verified/assumed): VERIFIED first-hand — the first (small-alphabet) benchmark misled this session; unique-token inputs then exposed the quadratic blowup (91→289→2372 ms). The O((N+M)·D) bound is textbook.
- Link: session 01KxkbJUq8YajH8GokSZYYHy; sandbox (not committed)

