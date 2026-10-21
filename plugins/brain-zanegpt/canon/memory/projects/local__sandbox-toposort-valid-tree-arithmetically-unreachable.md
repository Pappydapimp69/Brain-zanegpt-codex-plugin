# local/sandbox-toposort-valid-tree-arithmetically-unreachable — lessons

Project: local/sandbox-toposort-valid-tree-arithmetically-unreachable. Newest first.

---

## E1 — toposort valid tree arithmetically unreachable
- Date: 2026-09-30
- Project: local/sandbox-toposort-valid-tree-arithmetically-unreachable
- Tags: [algorithm][architecture][gamedesign][testing]
- What: A dependency graph that passes topological validation (5 nodes, 0 cycles, 0 undeclared deps) can still be arithmetically unreachable when its total cost exceeds the shared supply.
- Why built: Cover the untested seam between the dependency-ordered formula system and the tech-tree supply-versus-demand finding.
- Design: 5-building tree costing 5/10/14/18/20 (sum 67), TopologicalSorter validation, cheapest-first purchase in topo order per faction, four supply and faction scenarios, plus a sum-demand-versus-supply precheck.
- Got right: Validation passed while 48 stone shared by 3 factions (16 each) reached 2 of 5 buildings; the precheck agreed with reachability on all 4 scenarios (48/3 short, 201/3 full, 67/1 full, 66/1 reaches 4).
- Where/why it failed: I predicted 3 of 5 reachable at 16 stone; the first run gave 2 because hut plus mill costs 15 and forge (14) no longer fits, and that first run reported FAIL until I corrected my expectation.
- Fix: Add a total-demand versus total-supply check alongside dependency validation, computed per consumer, and re-run it whenever a consumer is attached to a resource.
- Why this fix: Graph validity says nothing about resources; the precheck matched reachability exactly on 4 of 4 scenarios including the 66 versus 67 boundary.
- Rule of thumb: A green toposort does not mean content is obtainable; sum cost times consumers against supply as a separate check, because reachability is decided by arithmetic, not by the edges.
- Provenance (verified/assumed): Verified first-hand by running the sandbox, with the corrected expectation noted above; real game economy data was left out of scope.
- Composed: sandbox-combined-skilltree-formula/E1, august-10/E7
- Polarity: compatible
- Sandbox: sandboxes/2026-09-30__toposort-valid-tree-arithmetically-unreachable.py
- Prediction: validation passes and 16 stone reaches 3 of 5 (came out wrong: 2 of 5); precheck matches reachability in all scenarios.
- Observed: RESULT: PASS toposort passes (5 nodes, 0 undeclared) while 48 stone/3 factions reaches only 2/5; supply-vs-demand precheck matches reachability on 4 scenarios
- Scenarios: 1) 48 stone 3 factions; 2) 201 stone 3 factions; 3) 67 stone 1 faction exact fit; 4) 66 stone 1 faction one short, built to break the precheck.
- Link: scheduled brain train pass 3
- Audited: 2026-10-12 · pass · Read the entry and reran its stored sandbox (same output, RESULT: PASS). The reachability numbers are computed by walking the topological order with a budget, not typed in, and the first-run prediction miss (3 versus 2) is reported honestly, so the core claim, that a tree can pass toposort validation and still be unobtainable on a shared supply, is genuinely tested. Limits that do not change the verdict: the only goal in all four scenarios is 'obtain everything', and in this tree the top building's dependency closure is the whole tree (closure cost 67 equals the total), so 'precheck matches reachability on 4 of 4' is close to true by construction; the boundary case 66 versus 67 cannot fail. A quick extra check I ran shows the precheck as written (total cost times factions against supply) over-flags a subset goal: at 47 to 66 stone per faction the tower (closure cost 47) is reachable while the total-sum precheck still flags a shortfall, so the Rule of thumb's 'sum cost' should be the cost of the goal's dependency closure. Also untested: unequal faction demand, several resource types, and non-greedy purchase order. The assert on 16 stone reaching exactly 2 is the observed number written back as an expectation, a mild circularity, though the model computes it. · scheduled brain train session; loop 2 pass 3 audit; session_01FbNV33qUVqkwoe1aojdkah
