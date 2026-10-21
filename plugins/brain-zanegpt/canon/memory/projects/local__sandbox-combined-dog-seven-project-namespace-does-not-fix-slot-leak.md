# local/sandbox-combined-dog-seven-project-namespace-does-not-fix-slot-leak — lessons

Project: local/sandbox-combined-dog-seven-project-namespace-does-not-fix-slot-leak. Newest first.

---

## E1 — sandbox combined dog seven project namespace does not fix slot leak
- Date: 2026-09-29
- Project: local/sandbox-combined-dog-seven-project-namespace-does-not-fix-slot-leak
- Tags: [save][state][browser][gamedev]
- What: The shared-origin fix from seven#E5 (namespace storage keys by project) and the multi-slot leak from dog#E64 (a raw "shown once" flag outside the save payload) are independent axes. Namespacing by project fully closes the first and leaves the second untouched.
- Why built: Both lessons prescribe key hygiene for browser storage, so it is easy to assume the project prefix from one covers the other.
- Design: Deterministic model of one shared origin, 2 projects (dog, seven) by 2 slots, one flag key set when the prologue finishes in one (project, slot) pair. For each of 4 originating pairs, check the flag in the other 3 pairs (12 ordered pairs). Three key schemes: bare key, project-prefixed, project plus slot prefixed.
- Got right: The bare scheme reproduces both recorded defects at once: 8 cross-project and 4 cross-slot leaks of 12 ordered pairs.
- Where/why it failed: The project-prefixed scheme, the exact fix seven#E5 prescribes, drops cross-project leaks to 0 but cross-slot leaks stay at 4 of 12, so a game that adopted the namespace can still report the multi-slot flag bug as fixed by mistake.
- Fix: Key any per-profile flag by project AND slot (0 and 0 leaks observed), or better, move the flag inside the per-slot save payload so it inherits the slot scoping.
- Why this fix: Scope is the product of every axis a key can vary along, and a prefix only removes the axis it names; a payload field is scoped by construction.
- Rule of thumb: When fixing a storage-key collision, enumerate every scoping axis (origin, project, slot, version) and test a leak matrix across all of them, not only the axis the bug report named.
- Provenance (verified/assumed): Verified first-hand by running the sandbox in this session; leak counts above are observed output.
- Composed: seven/E5, dog/E64
- Link: session https://claude.ai/code/session_01VDpEDT2ry2U1WXLUnGqdYD

