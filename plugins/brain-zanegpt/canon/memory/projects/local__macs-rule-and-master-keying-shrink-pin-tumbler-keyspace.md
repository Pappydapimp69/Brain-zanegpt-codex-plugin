# local/macs-rule-and-master-keying-shrink-pin-tumbler-keyspace — lessons

Project: local/macs-rule-and-master-keying-shrink-pin-tumbler-keyspace. Newest first.

---

## E1 — macs rule and master keying shrink pin tumbler keyspace
- Date: 2026-10-20
- Project: local/macs-rule-and-master-keying-shrink-pin-tumbler-keyspace
- Tags: [lockpicking][combinatorics][sandbox][testing]
- What: For a five-pin lock with ten cut depths 0 to 9 the quoted 100000 keys fall to 79666 once a maximum adjacent cut specification of 7 is enforced (20.3 percent removed, a count the brute force and a DP agree on), and a master-keyed lock opens at most 2 to the power of 5 = 32 key combinations, only 16 for two of the three sample locks.
- Why built: Seed run for a new lockpicking domain, starting from the usual quoted keyspace of depths to the power of pins and asking how much of it is really usable once a manufacturing rule and master keying are applied.
- Design: Brute force over all 100000 depth tuples with the adjacent-difference rule at most 7, checked against a transition-count DP; three hand-picked change keys against one master key, counting the cut combinations that open each lock after the same adjacency rule; a count of change keys that differ from the master in every chamber.
- Got right: Brute force and DP both gave 79666, inside the written range of 70000 to 85000, and the 32 maximum held with the full count reached on the first lock.
- Where/why it failed: Two of the three locks gave 16 and not 32, because one chamber shared the master depth (one option) in the third lock and the adjacency rule discarded half the combinations in the second; I had expected the 32 only as a ceiling. The depths, the rule value 7 and the master key are my own picks, not a real manufacturer chart, and no physical lock was tested.
- Fix: Size a keyspace from the rule-filtered count and size a master-keyed system from the number of chambers where change and master depths differ, instead of depths to the power of pins.
- Why this fix: The adjacency rule removes whole combinations before any key is cut, and a chamber that matches the master has only one shear line, so each correction is a direct count rather than a ratio.
- Rule of thumb: Count a pin-tumbler keyspace with the adjacent-cut rule applied (79666 of 100000 here, 20.3 percent gone) and give a master-keyed lock at most 2 to the power of the differing chambers openers (32, or 16 in two sampled cases), not the full quoted figure.
- Provenance: Verified first-hand by running the sandbox script in this session; the model is plain counting on assumed parameters.
- Composed: N/A
- Sandbox: sandboxes/2026-10-20__macs-rule-and-master-keying-shrink-pin-tumbler-keyspace.py
- Prediction: With MACS 7 the five-pin ten-depth count lands between 70000 and 85000 and DP equals brute force; every master-keyed lock opens at most 32 combinations and at least 1.
- Observed: RESULT: PASS MACS7 keeps 79666 of 100000 (20.3% removed); master-keyed locks open [32, 16, 16] keys of max 32; all-different change keys 47864
- Scenarios: (1) five pins ten depths MACS 7 brute force against DP; (2) first sample lock differing from master in every chamber; (3) second sample lock where the adjacency rule filters master combinations; (4) BREAK: third sample lock sharing one chamber depth with the master, built to show the 32 ceiling is not reached
- Link: scheduled brain train auto run, 2026-10-20; session_0193ruCZULAVFBK6Q3cwQk5z

