# local/sandbox-comedy-escalation — lessons

Project: local/sandbox-comedy-escalation. Newest first.

---

## E1 — sandbox comedy escalation needs a step coherence term and reversal slot varies
- Date: 2026-10-10
- Project: local/sandbox-comedy-escalation
- Tags: [humor][narrative][comedy][escalation][simulation][testing]
- What: A deterministic toy model of an escalating-absurdity comedy arc (the bat-house negotiation of progressively more
  unhinged renders, ending on a reversal: the tenant arrives on its own schedule, possibly never). Beat intensity
  sequences (flat at the ceiling, linear, geometric, a 3-beat rule-of-three) are scored against assumed audience models
  (habituation, an adapting expectation level, an inverted-U expectation term for the reversal). Habituation and
  adaptation alone do NOT justify progressive escalation: a single jump to the ceiling beat linear and geometric
  schedules in all four audience models (contrast-driven totals 1.410 flat vs 1.264 linear vs 1.183 geometric).
  Escalation only wins once a step-coherence term is added (a jump too large to resolve loses its payoff), and then the
  winning step is small, the ceiling is coupled to the beat count, and the reversal slot moves with how fast the
  audience builds the expectation that it breaks.
- Why built: The kernel says to stage the pitch as progressively more absurd renders, and a sibling kernel says escalation
  has to outrun an exponential habituation decay. I wanted to know whether those two combine into "escalate", where the
  claim breaks (habituation rate, intensity ceiling, reversal placement), and whether "rule of three" and "reversal
  last" fall out of the structure or only out of constants. This sandbox models the SHAPE of a sequence under stated
  assumptions; it says nothing about real audiences or real people, and every constant is assumed.
- Design: Beat k has intensity I_k clipped to a ceiling C (default 10, start 2, mundane baseline 1, six beats). Response
  is h * ((1-mu) * I/C + mu * contrast), with habituation h = exp(-0.2 * X) where X grows by 1/(1+I/5) per beat (weaker
  beats accumulate more exposure) and contrast = max(0, ln(I/A)) normalised, against an adapting level A that moves half
  way to each beat. Four audience models: level-driven (mu 0), mixed, contrast-Weber, contrast-linear. Part 2 adds an
  assumed coherence gate exp(-(ln(I/A)/rho0)^2) (rho0 0.8) and a fixed normalisation. The reversal is a drop to the
  mundane level scored as downward contrast against the adapted level, times an inverted-U 4P(1-P) where P is the
  audience confidence the pattern continues, P = 1 - (1-P0) * exp(-kappa * beats seen), then slotted at positions 2 to 6.
  Seeds are not needed (no randomness). Part 1 predictions (11) were written before the first run; Part 2 predictions
  (7) were written after seeing Part 1 miss and before Part 2 ran, and Part 2 is labelled as post-hoc in the file.
- Got right: Eight of 18 predictions held. Habituation retention matched the hand calculation (beat 6 over beat 1: 0.490
  for mild beats vs 0.717 for intense ones), so weak beats do burn out first. A fixed-ratio arc clipped at the ceiling
  has dead beats: beat 8 adds 4.2% of what beat 2 added. An anticipated catch (P0 0.9) cuts the reversal payoff by 86.4%
  (0.716 to 0.097). Best reversal slot moved earlier as kappa rose (slot 6, 5, 4 at kappa 0.10, 0.25, 0.50). With the
  gate on, three different schedules win under the four audience models (flat, flat, geometric 0.662 vs linear 0.624,
  linear 0.680 vs geometric 0.604).
- Where/why it failed: Ten predictions missed, and the misses are the lesson. Part 1: I expected geometric to beat
  linear by 10% or more under contrast-Weber and got 0.936; I expected a crossover weight mu where linear overtakes flat
  and there is none (flat wins at every mu); I expected one schedule not to win everywhere and flat won all four.
  Raising the ceiling from 10 to 20 at six beats LOWERED the total (-3.1% ungated, -6.6% gated) because the steps outgrow
  the coherence sweet spot, so the ceiling and the beat count are coupled, not independent. The gated flat-at-ceiling total
  was 0.296 vs 0.662 geometric (a ratio of 0.448, not under 0.2), the picky-audience half of Q6 held (96.6% cut) but a
  tolerant audience (rho0 3.0) did not let flat overtake geometric, and per-beat efficiency peaked at N=2 ungated and N=5
  gated, never at 3, so rule-of-three was not derived. The reversal was last in only 5 of 12 (gate, kappa, P0) cells.
  Exploratory: letting the beat count float, the best N hit the search cap of 12 because beats carry no cost in the model,
  so "best N" is unconstrained here. The coherence gate, the inverted-U reversal term and the Laplace-like expectation
  rate are my assumptions, and the result "the optimum is many small steps" follows from the gate shape.
- Fix: State the audience model before choosing a schedule: justify "progressive" escalation by a named coherence or
  resolvability limit on the size of each step, not by habituation, which on its own favours going straight to the
  ceiling. Size the step to that limit, set the beat count from ceiling / step, place the reversal by when the audience's
  confidence in the pattern crosses about one half (ln 2 / kappa beats), and check whether the catch is already expected.
- Why this fix: The sandbox shows flat-at-ceiling beating every escalation until the gate is added, the optimum step
  shrinking with the gate, a fixed six-beat arc losing payoff when the ceiling doubles, and the reversal payoff falling
  86.4% when pre-expected. Each of those is controlled by a named term, so naming the term makes the arc testable.
- Rule of thumb: Habituation alone says hit the ceiling at once; "escalate" needs a stated limit on step size. Treat
  rule-of-three and "reversal last" as outputs of the audience's expectation rate, not laws, and discount a reversal the
  audience already expects.
- Provenance (verified/assumed): Verified first-hand: the sandbox ran twice with identical output, final line `RESULT:
  FAIL 8/18 predictions held`, and every number above was read from that run. The constants (habituation rate 0.2,
  half-saturation 5, adaptation 0.5, coherence width 0.8, kappa values, baseline) are assumed and the model scores
  structure only. The two sibling kernels were taken as written in the canon; their source papers were left unopened.
- Composed: ideas:narrative-design/comedy/negotiation-arc/escalation, ideas:ORAL-STORYTELLING/controlled-escalation/habituation/response-decays-fastest-on-the-weakest-beats, ideas:ORAL-STORYTELLING/suspense/information-gap/curiosity-peaks-at-about-fifty-percent-confidence
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-10__sandbox-comedy-escalation-needs-a-step-coherence-term-and-reversal-slot-varies.py
- Prediction: Eighteen numeric predictions written before each part ran. Headline ones: geometric beats linear by 10% or
  more under a contrast-driven audience (observed 0.936); a crossover weight exists where linear beats flat-at-ceiling
  (none); the best reversal slot is 3 or 4 of 6 (observed 5); doubling the ceiling adds 10% to 35% (observed -3.1%); no
  single schedule wins every audience model (observed flat won all four ungated).
- Observed: RESULT: FAIL 8/18 predictions held. Ungated contrast-Weber totals flat 1.410, linear 1.264, geometric 1.183;
  gated (rho0 0.8) flat 0.296, linear 0.624, geometric 0.662. Reversal-only payoff by slot 2..6 at kappa 0.25: 0.121,
  0.335, 0.525, 0.652, 0.716; best slot last in 5 of 12 cells. Anticipated catch: 0.716 to 0.097.
- Scenarios: 1) four audience models x flat/linear/geometric schedules, ungated; 2) the same with the coherence gate;
  3) habituation-rate sweep (lam 0 to 0.8); 4) reversal slot by kappa (0.10, 0.25, 0.50), P0 and gate (12 cells);
  5) BREAK: anticipated catch P0 0 to 0.9; 6) ceiling sweep C 3 to 100, fixed and floating beat count; 7) BREAK: fixed
  ratio arc clipped at the ceiling (dead beats); 8) coherence width rho0 0.3 to 3.0 (picky and tolerant audiences)
- Link: session_01YFLLRpDsfZpRstb2KT2MQy
- Audited: 2026-10-11 · modeled · Read the entry and the stored sandbox and reran it (RESULT: FAIL, 8 of 18 predictions held, matching the entry). The model computes its numbers from the stated formulas (habituation, adapting level, expectation term) and does not hard-code the answers, and 10 of the 18 misses are reported honestly. Two limits keep this from a plain pass. First, Part 2 adds a coherence gate with a chosen width after Part 1 missed, so the headline that escalation needs a step-size limit comes from a term added to rescue the story, with its constants assumed. Second, the Rule of thumb makes claims about real audiences (rule of three and reversal-last as expectation artefacts) that were tested only against a hand-written audience model with no human data. The mechanism within the model is sound; the transfer to real comedy is unverified, hence modeled and not audited. · scheduled brain train session, loop 2 pass 3; session_01CNA5AiMj7DcwaL9AXKp2Jn
- Cited-by: 2026-10-15 · projects/local__escalation-needs-matching-distance.md#E1 · compatible · sandboxes/2026-10-15__escalation-needs-matching-distance.py · observed RESULT: PASS best schedule: no gate flat (5.11), fixed distance mild (1.45; flat 0.00), matched distance flat (5.11); fixed-distance beats above I=6 keep at most 0.10 of their ungated value. · https://claude.ai/code/session_015qgYN9GL7cHD9BS1wmwyMx
- Cited-by: 2026-10-15 · projects/local__game-of-scene-hxe-check-column.md#E1 · compatible · sandboxes/2026-10-15__game-of-scene-hxe-check-column.py · observed RESULT: PASS naive exact 4/6, fixed 6/6, false-X 1 sheet (2 beats), flat flagged by plain column=False · session_01A5ZkeepCfk7CHTSxS7qQ4k
- Cited-by: 2026-10-18 · projects/local__step-coherence-limit-does-not-dethrone-plateau-under-matched-distance.md#E1 · incompatible · sandboxes/2026-10-18__step-coherence-limit-decides-winner-once-distance-and-card-cover-are-matched.py · observed RESULT: PASS (revised claim) flat still wins at L=3 (41.30 vs 51.12 ungated, 0.808 kept) and at every L 0.1..3.0; card inert diff 0.0; close d with card c 0.5 keeps flat winning (20.66 vs 15.92). Two parts of the prediction were refuted. · brain train auto loop 1 pass 1; session_01Q7rYJzNw1uctb9nhZsXCQx
