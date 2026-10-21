# local/sandbox-research-methodology — lessons

Project: local/sandbox-research-methodology. Newest first.

---

## E1 — corroboration count fooled by citation echo chain
- Date: 2026-07-20
- Project: local/sandbox-research-methodology
- Tags: [process][research]
- What: Counting how many distinct SOURCES assert a claim ("N sources
  agree, it must be well-corroborated") does not measure independent
  confirmation — a claim asserted by many sources that form a citation
  echo chain (each derived from, or citing, an earlier one in the chain
  rather than reaching the claim independently) can outscore a claim
  genuinely confirmed by fewer, truly independent sources, on the naive
  count alone.
- Why built: `brain train new-domain`, targeting the METHODOLOGY of
  external research itself as a genuine gap (`brain query` returned
  only incidental, project-specific instances of citing external
  sources well or poorly — e.g. draft/collective's "reconstruct from
  the product's own data surface, not third-party summaries" and
  brain's "a study's finding doesn't automatically transfer beyond the
  population it tested" — never organized into a dedicated domain about
  research practice itself, source reliability, or corroboration).
- Design: `sandbox.py` — a fixed, hand-authored citation graph (zero
  RNG). Claim A (modeled as actually TRUE) is asserted by 2 sources,
  each a genuinely independent primary investigation (`derived_from =
  None` for both). Claim B (modeled as actually FALSE, a myth) is
  asserted by 5 sources, but 4 of them trace — directly or
  transitively, via a `derived_from` edge — back to a SINGLE root
  origin (`original_blog`): a wiki summarizes the blog, a second blog
  cites the wiki, a forum cites the blog directly, an aggregator cites
  the second blog. Two functions compared on the identical graph:
  `naive_corroboration_count` (count distinct source NAMES asserting
  the claim) and `independent_root_count` (trace every asserting source
  to its root via `derived_from`, count DISTINCT ROOTS).
- Got right: the citation graph itself is realistic in shape — a mix of
  direct-from-origin citations (forum→blog) and transitive chains
  (aggregator→second_blog→wiki→blog), not an artificially simple
  single-hop case, so the root-tracing logic is genuinely exercised
  across multiple hop depths, not just a trivial one-level check.
- Where/why it failed: the naive source-count check reports Claim B (5
  sources) as MORE corroborated than Claim A (2 sources) — exactly
  backwards, since B is the false claim and A is the true one in this
  model. The independent-root-count check correctly reverses this: A
  traces to 2 distinct roots, B collapses to exactly 1.
- Fix: for any external-research corroboration check (verifying a claim
  against multiple sources before treating it as reliable), trace each
  asserting source back through its own citation/derivation chain to
  its root origin, and count DISTINCT ROOTS, not distinct source names
  — a source repeating or summarizing an earlier source's claim adds
  visibility, not independent evidence.
- Why this fix: the number of places a claim is REPEATED is a
  popularity/visibility signal, not a reliability signal; only the
  number of genuinely separate INVESTIGATIONS that independently
  reached the same conclusion is evidence the claim is more likely
  true, and a citation chain (however long) that bottoms out at one
  origin still represents exactly one investigation's worth of
  evidence, however many times it gets re-published.
- Rule of thumb: when evaluating how well-supported an externally-
  researched claim is, do not stop at "how many sources say this" —
  for each source, ask "does this source's claim derive from another
  source already in my list, or is it an independent origin?" A claim
  repeated by many derivative sources (blogs summarizing blogs, wikis
  citing wikis) can look far better-corroborated than a claim confirmed
  by a couple of genuinely separate primary investigations, and naive
  counting will rank them backwards. Prefer sources that state their
  own methodology/investigation over sources that merely cite another
  source's conclusion, and explicitly check for a shared common
  ancestor before treating agreement as independent confirmation.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  (zero RNG, zero wall-clock, fixed citation graph), confirmed the
  naive count favors the false claim (5 vs 2) while the independent-root
  count correctly favors the true claim (2 roots vs 1 root). Re-ran as
  two independent process invocations; output byte-identical both
  times.
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, external-research-methodology gap); sandbox
  `scratchpad/research_domain/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-10-09 · projects/pappydapimp69__brain.md#E118 · compatible · sandboxes/2026-10-09__root-tracing-counts-independence-not-truth-and-needs-cycle-and-alias-handling.py · observed RESULT: PASS echo A naive 5>2 but roots 1<2; cycle->1 group; dropped link inflates 1->2 (all dropped 3); alias 2->1; independent-but-wrong still scores 2 · brain train auto pass 5 gap, unattended run 2026-10-09; session_01A7os5bwK2BHc7rwnvxx6Ts
- Cited-by: 2026-10-09 · projects/local__sandbox-negotiation-batna.md#E1 · incompatible · sandboxes/2026-10-09__batna-walk-away-alternative-sets-the-floor-willpower-only-buys-price-inside-it.py · observed RESULT: FAIL 5/7 checks. Held: threshold (51.85 flat, 64.0, 82.0), premium 7.1 to 41.3, no-zone impasse 6/6, non-binding spread 0.00 vs 47.4, anchor monotone and capped. Failed: naive willpower r 0.97 to 0.96 within BATNA (predicted halved… · brain train auto pass 5 (gap mode), sandbox run 2026-10-09; session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-09 · projects/pappydapimp69__dhw26.md#E1 · compatible · sandboxes/2026-10-09__event-date-latest-primary-beats-citation-count.py · observed RESULT: PASS latest-primary correct 3/3; majority wrong on S1 (3v2), distinct-roots TIE on S1 (1v1), authority-first wrong on S2, S1 verified, S2+S3 (single agreeing record) flagged unverified · https://claude.ai/code/session_015AHHmiNVQdgw5FUjWXGtgp · commit 3b74e8b
- Audited: 2026-10-14 · modeled · No sandbox file is stored with the entry (only a description of sandbox.py in Design), so I judged the described design. The counting is computed, not built in: the naive count of 5 versus 2 and the root count of 1 versus 2 follow from tracing the derived-from edges of a fixed graph. But the answer that matters is assumed by the author, because claim B is labelled false and claim A true before any counting, and the graph was authored so that four of five sources share one root; the model therefore shows that a naive count and a root count can disagree on a hand-made graph, not that real sources behave this way or that root counting tracks truth. The rule of thumb is about real external research, and a single independent root can itself be wrong while two roots can both be wrong, which this one graph cannot show. The mechanism (shared root counts once) is sound arithmetic; its transfer to real corroboration was not tested against a real citation graph, so the verdict is modeled rather than pass. · brain train auto scheduled run, loop 2 pass 3; session_013UbxUV5wii3FwAXCPW9kkg
