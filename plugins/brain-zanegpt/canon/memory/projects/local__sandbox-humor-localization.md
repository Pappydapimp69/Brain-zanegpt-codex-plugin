# local/sandbox-humor-localization — lessons

Project: local/sandbox-humor-localization. Newest first.

---

## E1 — humor travel tracks items needed and norm mismatch injures only parsed jokes
- Date: 2026-10-10
- Project: local/sandbox-humor-localization
- Tags: [humor][localization][simulation][testing]
- What: A structural toy model of which joke payloads survive moving from audience A to audience B. A joke needs shared items
  (sound pairs, references, observed situations: missing one makes it blank; power, closeness and modesty norms: missing one
  makes it read under B's norms). Observation and self-directed jokes landed far more often than wordplay and reference jokes
  (0.77 and 0.50 vs 0.06 and 0.25 at overlap 0.5), but the label is a proxy: the gap is 56% item count and 44% how
  locale-bound each item type is, and only norm-bearing jokes (teasing, self-deprecation) can turn injurious.
- Why built: The claim that observational and self-directed humor travels better than wordplay and reference humor sounds
  right, and the open Spanish register tension (tu vs usted, neutral vs Mexican-US) is partly a question about teasing.
  I wanted to know whether the claim survives a decomposition, where a benign joke becomes injurious, and whether register
  choice matters for every kind of joke. The model scores structure under stated assumptions; it says nothing about the
  psychology of real people or any named person.
- Design: Audience B holds each of A's items with probability overlap**alpha, alpha per item type (sound pairs 2.0,
  references 1.0, power and modesty norms 0.6, observed situations 0.4; stated assumptions). Five mechanisms with item counts
  (wordplay 2 sound items; reference 2; teasing 2 norm + 1 situation; self-deprecation 1 norm + 1 situation; observation
  1 situation). Seeded Monte Carlo, 6000 jokes per cell, cross-checked against the analytic product (max gap 0.013). A joke
  benign in A (intensity at most 0.5) turns injurious when a missing norm shifts the threshold below its intensity. Register
  is a shift on felt intensity scaled by how register-dependent the mechanism is. The four-style frame (affiliative,
  self-enhancing, aggressive, self-defeating, from the Humor Styles Questionnaire) is RECALLED from the 2003 paper and checked
  only against a search summary, not the paper; I did not reproduce its items and mapped each style to a stand-in mechanism mix.
- Got right: Twelve predictions were written before the first run and eleven held. Class ordering held at every overlap from 0.1
  to 0.9. Wordplay and reference injury was exactly 0 because a missing content item blanks the joke. Teasing injury
  was 0.08 at overlap 0.5 and peaked near 0.10 at overlap 0.3 (the danger zone is the middle: low overlap blanks, high overlap
  matches norms). The break-even injury cost ratio against wordplay was 3.15 for teasing and 9.27 for self-deprecation;
  observation has none. Transcreating content items (0.8 each) lifted wordplay at overlap 0.1 from 0.000 to 0.645,
  and capping intensity at 0.25 cut teasing injury from 0.120 to 0.040 at overlap 0.3. Register choice moved harm by 0.000
  for observation and wordplay, and by a factor of 0.3 as much for self-deprecation as for teasing.
- Where/why it failed: Prediction P12 missed: I expected self-defeating mixes to land at least as often as affiliative at
  weight 0.6, but affiliative landed above it at every weight tested (0.57 vs 0.44 at 0.6). The hand estimate used a different mix than the code.
  Also the affiliative and self-enhancing rows are identical because both map to observation: payload cannot separate styles that
  differ by intent and target. The register crossover (0.714 expecting tu) is algebra from the two assumed shifts (0.25
  and 0.10), not a discovery, and the label ordering reverses for a locale-bound observation (3 items, alpha 1.0: 0.125 vs a
  global one-item reference 0.758 at overlap 0.5).
- Fix: Judge a joke for localization by listing its required items and classing each as content (blank if missing) or norm
  (misread if missing), then rank by count times locale-boundness, not by style label. Transcreate content items, re-aim
  norm-bearing jokes by capping intensity below the benign threshold minus the largest plausible norm shift, and measure
  the shift and the audience split before trusting any register crossover.
- Why this fix: Survival is a product over required items, so removing or swapping an item moves it multiplicatively,
  while a norm item adds a hurt channel that blanking does not have. Capping intensity removes that channel
  (0.25 cap gave exactly zero tu harm at every audience share) without changing the mechanism, the same move as keeping a
  comic mechanism and changing its target.
- Rule of thumb: Humor travels by the items it needs, not by its style label: count content items (blank when missing) and
  norm items (misread when missing), transcreate the first, cap the intensity of the second, and expect wordplay to fail
  silently while teasing and self-deprecation fail loudly.
- Provenance (verified/assumed): Verified first-hand by running the shipped sandbox in this session: RESULT: FAIL with 11 of
  12 pre-registered predictions held, all numbers above copied from that run. Model parameters (alpha per item type, norm shift
  0.2 per missing norm, register shifts 0.25 and 0.10, stand-in style mixes, the triangular law for the syllable ratio fitted
  to the stated mean 1.55 and range 0.90 to 1.88) are my stated assumptions, so every figure describes this model only.
- Composed: ideas:LOCALIZATION/ad-copy/transcreate-the-hook-and-cta-translate-the-product-facts, local__suno/E32, pappydapimp69__tiktok-shop/E3
- Polarity: compatible
- Sandbox: sandboxes/2026-10-10__humor-travel-tracks-items-needed-and-norm-mismatch-injures-only-parsed-jokes.py
- Prediction: Before the first run, at overlap 0.5 survival would be observation 0.70-0.80, self-deprecation 0.45-0.55, teasing
  0.28-0.38, reference 0.21-0.29, wordplay 0.04-0.09; the exponent alone would explain 0.40-0.50 of the observation vs
  wordplay log gap; teasing break-even cost ratio 2-5; tu/usted crossover 0.65-0.80; self-defeating would land at least as
  often as affiliative at weight 0.6.
- Observed: RESULT: FAIL 11/12 pre-registered predictions held; wordplay 0.06 vs observation 0.76 at overlap 0.5; tease injury 0.08; tu/usted crossover at 0.71 tu-expecting share
- Scenarios: 1) five mechanisms swept over overlap 0.1-0.9; 2) uniform-exponent ablation and item-count decomposition; 3) BREAK:
  locale-bound observation (3 items, alpha 1.0) against reference and wordplay; 4) parse vs misread injury and cost-ratio break-even;
  5) tu, usted, neutral over audience splits for teasing, self-deprecation and observation; 6) intensity caps 0.25 and 0.35;
  7) transcreation, bilingual overlap and punchline timing against the Spanish window; 8) four-style mixes at three weights
- Link: session_01YFLLRpDsfZpRstb2KT2MQy
- Cited-by: 2026-10-10 · projects/local__sandbox-humor-timing-figures.md#E1 · incompatible · sandboxes/2026-10-10__published-timing-figures-vs-stand-in-ratio-law-in-the-punchline-syllable-cap.py · observed RESULT: FAIL 5/7 pre-registered predictions held; ratio-law swap moves n_safe 11 to 12/13, rate spread drops fit(11) to 0.87, hold choice swings setup budget 9.4 syllables. Missed: P2 (triangular gave 13) and P6 (shift 2 at 2.8 s). · session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-10 · modeled · Read the entry and its stored sandbox. The landing rate is overlap raised to a per-item exponent that the author assigns (sound pairs 2.0, observed situations 0.4), multiplied by item counts the author also assigns, and the Monte Carlo is cross-checked against that same analytic product (gap 0.013), so the class ordering and the 56/44 decomposition follow from the stated assumptions rather than being discovered by the run. The sandbox does COMPUTE its numbers and honestly reports a missed prediction (11 of 12 held) and the break case for locale-bound observation jokes, and the entry says the four-style frame was recalled and not checked against the paper. But the Rule of thumb concerns how real jokes travel between real audiences, and only a hand-written model with assumed exponents was tested, so the verdict is modeled: the ordering is a consequence of the inputs and needs a measured exponent per item type to count as evidence about people. · scheduled brain train audit session 2026-10-10 (loop 2); session_012JxzWUk56eKHuHi3fNYxn2
