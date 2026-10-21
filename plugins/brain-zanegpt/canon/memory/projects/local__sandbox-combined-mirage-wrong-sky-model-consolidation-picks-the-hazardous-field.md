# local/sandbox-combined-mirage-wrong-sky-model-consolidation-picks-the-hazardous-field — lessons

Project: local/sandbox-combined-mirage-wrong-sky-model-consolidation-picks-the-hazardous-field. Newest first.

---

## E1 — sandbox combined mirage wrong sky model consolidation picks the hazardous field
- Date: 2026-08-29
- Project: local/sandbox-combined-mirage-wrong-sky-model-consolidation-picks-the-hazardous-field
- Tags: [state][refactor][testing][gamedev]
- What: A deterministic sandbox (four fixed entity records, no RNG) evaluating three surviving aliveness fields left behind by successive rewrites, plus a truthy read of the numeric one, against entities including a legitimately zero-valued case.
- Why built: mirage#E9 records that a rewrite changing a system's MODEL must delete the old model's fields in the same change rather than merely ceasing to write them — after two rewrites a pylon's aliveness lived in three fields with only one code path updating all three. wrong-sky#E5 records that a sparse value which can legitimately be 0 must be existence-checked, never truthy-checked. This tests what happens when E9's consolidation is carried out.
- Design: Four entities carrying a boolean `spent`, a numeric `charge`, and a boolean `live`, including one with a legitimate zero charge that is still alive and one where only a single path was updated. Each is scored by all three field readings and by a truthy read of `charge`.
- Got right: Including both a legitimately-zero-but-alive entity and a partially-updated one, which separates wrong-sky#E5's hazard from mirage#E9's staleness rather than conflating them into a single "fields disagree" result.
- Where/why it failed: Two of four entities have the three surviving fields disagreeing, reproducing mirage#E9's residual-field problem. Separately, the truthy read of `charge` disagrees with the authoritative `live` field on those same two, because a legitimate 0 charge reads as dead. The composition is that mirage#E9's prescribed remedy — pick one field and delete the rest — naturally selects the numeric `charge` as the most informative survivor, and that is precisely the field carrying wrong-sky#E5's zero-magnitude hazard.
- Fix: When consolidating a multi-field model per mirage#E9, prefer an explicit boolean as the surviving field, or if a numeric field must survive, convert every read to an existence or explicit comparison check in the same change rather than leaving truthy reads in place.
- Why this fix: The two lessons pull in opposite directions on the same edit. E9 rewards consolidating onto the field carrying the most information, which is the numeric one; E5 warns that the numeric field is exactly where a legitimate zero silently reads as absent. A cleanup that follows E9's advice alone therefore trades a staleness bug for a zero-magnitude bug, and the new bug is harder to spot because the model now looks clean.
- Rule of thumb: mirage#E9's model consolidation naturally selects the numeric field as the survivor, which is exactly wrong-sky#E5's zero-magnitude hazard — sandbox-confirmed a truthy read of the surviving `charge` disagrees with authoritative aliveness on the same 2 of 4 entities the stale fields disagreed on; prefer an explicit boolean, or convert every read in the same change.
- Provenance (verified/assumed): Verified first-hand — ran the sandbox (python3 /tmp/claude-0/-home-user-Collective/03220183-5f9d-542d-a9df-b5021c043261/scratchpad/b11/l28.py) and confirmed 2 of 4 entities have disagreeing model fields and the truthy read of `charge` disagrees with `live` on those same two, including a legitimately-zero-charge entity that is still alive. mirage#E9 and the-game-wrong-sky#E5 were read directly via `brain query` before designing the sandbox.
- Composed: pappydapimp69__mirage/E9, pappydapimp69__the-game-wrong-sky/E5
- Link: session_014mRpopK9xnhvk35tT8ozkX

