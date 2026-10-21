# local/sandbox-kernel-doctest-wiring — lessons

Project: local/sandbox-kernel-doctest-wiring. Newest first.

---

## E1 — doctest catches drift only where examples are wired and counted
- Date: 2026-10-09
- Project: local/sandbox-kernel-doctest-wiring
- Tags: [documentation][testing][tutorial]
- What: Ran the real stdlib doctest module against a small API whose behavior changed between v1 and v2 while its docs did not. It caught every stale example in module docstrings (3 of 3) and in a README wired in with testfile (1 of 1), but missed a stale example written as a plain indented code block without a prompt, and a file containing no prompt examples at all reported zero failures.
- Why built: brain train gap listed the doctest kernel as unapplied, with doc-rot as a sibling kernel and a tutorial-starvation memory entry as a candidate re-verification.
- Design: A v2 module with three docstring examples written for v1 (int result, old label prefix, list vs tuple), a README with one prompt example and one plain-fence example, a prose-only module, and a whitespace-only output mismatch. Compared four checks: no checking, doctest over module docstrings, doctest.testfile on the README, and a count of attempted examples per file.
- Got right: Unrun docs detected 0 of 5 stale claims, the kernel's silent-drift half; doctest turned 4 of them into failures. A zero-example file produced failed=0 attempted=0, the same shape as sandbox-resolver-starves-tutorial/E2, where an endpoint check passes while the middle layer is silently empty.
- Where/why it failed: Doctest alone is not the whole guarantee: the plain-fence stale claim was never attempted (1 of 5 hidden), a README only counts when wired in explicitly (the doc-rot kernel's point that docs outside the checked path rot), and a pure whitespace difference failed one example until NORMALIZE_WHITESPACE was set.
- Fix: Fail the docs check when attempted is 0 for any file that is supposed to carry examples, write examples with prompts, wire every doc file in by name, and set comparison flags deliberately for whitespace or ordering sensitive output.
- Why this fix: The runner can only judge what it attempts; the number of attempted examples is the one value that distinguishes a clean pass from an empty one.
- Rule of thumb: Executable examples fail loudly only for examples that are wired in and actually attempted (4 of 5 stale claims caught here, 1 plain-fence claim invisible): assert attempted is greater than 0 for each doc file, because a file with no prompt examples passes with 0 failed.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox against the real doctest module of the local Python 3; deterministic. The API, README and counts are synthetic; other doc tools such as Rust doc-tests were not exercised.
- Composed: ideas:DOCUMENTATION/executable-docs/doctest, ideas:DOCUMENTATION/maintenance/doc-rot, sandbox-resolver-starves-tutorial/E2
- Sandbox: sandboxes/2026-10-09__doctest-catches-drift-only-where-examples-are-wired-and-counted.py
- Prediction: Before the run: unrun docs catch 0 of 5 stale claims, doctest catches the 3 docstring examples, a wired README catches 1 more, a plain-fence claim stays hidden, a zero-example file passes vacuously, and a whitespace-only mismatch fails until normalised.
- Observed: RESULT: PASS doctest caught 4 of 5 stale claims (3 docstring + 1 wired README); 1 plain-fence claim hidden; unrun docs caught 0; zero-example file passes with failed=0 attempted=0; whitespace-only mismatch fails until NORMALIZE_WHITESPACE
- Scenarios: 1) no checking; 2) doctest over module docstrings; 3) README wired through testfile; 4) prose-only file built to break the "doctest passed so docs are fine" reading; 5) whitespace-only mismatch with and without the flag
- Link: https://claude.ai/code/session_01GfAHwy3Bruhswzp52FBWqr
- Cited-by: 2026-10-10 · projects/pappydapimp69__brainwork.md#E90 · compatible · sandboxes/2026-10-10__why-comment-stale-sandbox.py · observed RESULT: PASS value-only: what-comments stale 6/6 (checker caught 6), why-comments 0/6; premise-only: why-comments stale 6/6 but checker caught 0 · brain train auto loop 1 pass 1; session_01LphKr4r2NDaVJxz3d1yx7B
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E490 · compatible · sandboxes/2026-10-19__doctest-attempted-gate-must-exempt-explanation-pages-in-a-diataxis-doc-set.py · observed RESULT: PASS naive gate false-flags 2 explanation pages of 4 flags; quadrant-aware gate flags exactly the 2 real defects (stale example, how-to with no example) · brain train auto loop 2 pass 5, session 2026-10-19; session_01M3VVz3RFpipo1Jc6ecPoW2
- Cited-by: 2026-10-19 · projects/pappydapimp69__brainwork.md#E497 · compatible · sandboxes/2026-10-19__verified-examples-beat-prose-for-copying-after-api-drift-but-miss-unexercised-defaults.py · observed RESULT: PASS v1 prose 6/6; v2 prose 3/6; doctest caught 2/2 exercised drifts; examples+CI copy 5/6 (unexercised retry default still wrong) · brain train auto pass 5, session 2026-10-19; session_01M3VVz3RFpipo1Jc6ecPoW2
