# Tension

The **unresolved-contradiction** node of the cognitive architecture. This repo
holds the forks the project is deliberately keeping open — tradeoffs, assumptions,
open questions, and contradictions — so that uncertainty is *preserved* rather
than silently collapsed into a decision.

- **Canonical file:** [`tension-ledger.md`](tension-ledger.md).
- **A tension is not a bug** (that's `memory`) **and not a decision** (those are
  ADRs in the build repo). It is a live question with stakes.
- **Retrieval:** the `brain` orchestrator greps this ledger before a system is
  built. An *open* tension touching the work means the call is not Claude's to make
  silently — surface it to the user.

Sibling nodes: `ideas` (reusable kernels + exploration residue) ·
`memory` (hard-won lessons) · `brain` (orchestration).
*(`creativity` is frozen; its parked alternatives migrated here, the rest to
`ideas/exploration.md`.)*

## Status lifecycle (Phase 1 contract)

States: `🔴 open` · `🟡 leaning` · `🟢 resolved` · `⚪ superseded`.

**1. Transitions are evidence-bearing appends, never silent edits.**
Every status change appends a dated line to the entry's `Updates:` log citing a
linkable artifact, then flips the status marker in the same commit. No citation,
no transition. Admissible citations:
- a `memory` entry (`projects/<owner>__<repo>.md#E<n>`), commit, PR, or ADR —
  closes as **🟢 resolved (evidence)**: the fork was settled by facts; durable.
- a recorded owner decision — closes as **🟢 resolved (decision)**: the fork was
  not disproven, it was *chosen*. The `Updates:` line itself (e.g.
  `2026-07-02 closed by owner: responsiveness wins — <who>`) is the citation once
  committed; its commit SHA is the anchor. Reopenable if the decision is revisited.
The parenthetical matters: a future reader must never mistake a preference for a
proof.

**2. Leans are a cache, and caches expire.**
A `🟡 leaning` records a default to honor — it saves re-deliberation, but left
untouched it hardens into an unexamined decision (this happened: T2/T9). Rule:
a 🟡 with no `Updates:` line for **2 consecutive milestones** is stale — flag it
`🟡⏰` at the milestone pass and re-examine it before the next system touches its
area. Re-examination is itself an `Updates:` append (even "re-examined, lean
holds" — that resets the clock).

**3. Cross-project promotion (Brain-decided).**
The ledger is one file, so recurrence is visible by grep: the same fork appearing
under multiple `## Project:` headings is a promotion trigger. Brain (never the
ledger itself) may then create an entry under `## Cross-project` scoped to the
axis, and mark the per-project copies `⚪ superseded → <cross-project id>`.

**4. Append-mostly.**
Never delete an entry; the history is the value. Correct via `Updates:` appends
and status flips.
