# pappydapimp69/creativity — lessons

Project: pappydapimp69/creativity. Newest first.

---

## E1 — creativity single log vs per project dirs
- Date: 2026-07-18
- Project: pappydapimp69/creativity
- Tags: [architecture][process]
- What: Creativity existed as three competing, unmerged self-definitions on separate
  branches (a per-project `explorations/` directory with a graduation lifecycle and
  `archive/`; a generative agent filing straight into `ideas`; a single
  `creativity-log.md` with four typed entry kinds) before the owner ruled. The ruling
  didn't select one of the three — it retired the whole standalone node. Creativity is
  now FROZEN on `main`, its one proven value (an alternative parked *with the reason
  it was parked*) moved to `tension`, and its experiment/synthesis/speculation
  entries moved to `ideas/exploration.md`.
- Why built: Three independent sessions had each proposed a different storage shape
  for the same role (exploration/synthesis) without a shared ground truth to check
  against, so the ambiguity was left to accumulate across three full branches rather
  than resolved at the first divergence.
- Design: The per-project-directory laboratory model (one of the three) optimized for
  rich process — per-record lifecycle states, signal-based triggers, an archive — on
  the theory that exploration needed its own home with its own discipline.
- Got right: The single-log model (`creativity-log.md`) was the one actually
  populated and exercised against a real build (the shattered-realm RPG project)
  before the ruling, not just designed on paper — it demonstrated the retrieval loop
  closing (a speculation promoted to a shipped guard within one milestone) that the
  other two definitions could only argue for hypothetically.
- Where/why it failed: The owner's stated rationale for freezing the whole node, not
  merely picking a winner: "in practice the node never changed a build on
  retrieval." A per-project directory structure fragments the one thing Brain
  actually needs to scan before building (parked alternatives, so a declined road
  isn't blindly re-walked) across N folders instead of one place; that scan cost,
  combined with the node's output not measurably changing downstream decisions, was
  worse than folding the two real functions (parked-alternative-with-reason;
  experiment/synthesis/speculation) into repos that already had a scanning surface
  Brain reads on every retrieval pass (`tension`, `ideas/exploration.md`).
- Fix: Not this session's action — recording the ruling and its rationale as a
  lesson, not re-litigating it. If a similar "should this be its own node/directory,
  or folded into an existing scanned surface" question comes up again, this is the
  precedent.
- Why this fix: N/A — a design-decision lesson, not a bug fix.
- Rule of thumb: A knowledge-architecture node earns its own standalone home only if
  something downstream actually reads it before deciding something. A rich process
  (typed lifecycle, archive, graduation rules) sitting behind a directory nobody
  scans by default is indistinguishable, in practice, from not existing — and a
  single scannable file that's actually been exercised against a real build beats a
  well-designed-but-unproven directory structure, even when the directory structure
  is architecturally "cleaner" on paper. Prefer proof-of-use over elegance-on-paper
  when a node's value depends on being retrieved, not just being well-organized.
- Provenance (verified/assumed): VERIFIED first-hand — read Creativity's actual
  `main` branch README.md/CLAUDE.md (the owner's ruling text, dated 2026-07-02, and
  the three tombstoned branch names/rationale) and Brain's `main` branch
  README.md/orchestration.md (confirming the `creativity` node is listed as "frozen —
  being folded into `ideas` as a tagged section", and the NODES tuple in `bin/brain`
  itself omits Creativity from the four actively-cloned knowledge repos) directly,
  not secondhand.
- Composed: N/A
- Link: Creativity repo `main` @ commits 173081b/2f17e8e/e829663; Brain repo `main` @
  README.md/orchestration.md; three tombstoned branches:
  claude/creativity-synthesis-exploration-rcaijq, claude/tension-tracker-ppdkc8,
  claude/shattered-realm-architecture-lv3lb4
- Cited-by: 2026-10-11 · projects/pappydapimp69__brainwork.md#E114 · compatible · sandboxes/2026-10-11__parked-alternatives-single-log-reason-recheck.py · observed RESULT: PASS cost {'none': 32.0, 'fragmented': 24.0, 'log_blind': 16.0, 'log_first_reason': 12.0, 'log_all_reasons': 13.5}; blind-skip misses 8; first-reason recheck rewalks 2; recheck crossover at check cost 0.143. The last prediction (fu… · scheduled brain train session; session_01BWCnQ783SE9ph58n6xAc6f
