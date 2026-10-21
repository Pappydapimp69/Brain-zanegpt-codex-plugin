# local/sandbox-npc-memory-guardrails — lessons

Project: local/sandbox-npc-memory-guardrails. Newest first.

---

## E1 — npc memory hysteresis asymmetric tiered guardrails
- Date: 2026-10-09
- Project: local/sandbox-npc-memory-guardrails
- Tags: [simulation][npc][architecture][testing]
- What: A 24-NPC, 120-day relationship-decay toy shows the sticky floor keeps strong bonds (24/24 above 20 versus 0/24 for pure exponential decay) but also keeps hostile ones (12/12), while asymmetric retention and flag-only tiering held only for some bond strengths and contact cadences.
- Why built: The NPC memory guardrails kernel (floor with debounce, asymmetric retention, tiered fidelity) had no memory entry applying it, so this tests where each guardrail stops holding.
- Design: Python stdlib, no RNG. Per-day decay of s by (1 - rate) unless |s| is at or above 40 or fewer than DEB idle days have passed. Key NPCs use rate 0.02, background 0.08. A flag-only background model is compared with the full model. The stored event trace is replayed and NPC update order is reversed to compare state.
- Got right: Replay from the event trace and reversed update order both reproduced live state exactly. The floor protected strong bonds from erosion.
- Where/why it failed: My prediction that asymmetric rate alone keeps key bonds above 20 for 120 days was wrong (62 days to fall below 20 versus 15 for background). A one-day debounce did nothing when contact came every second day (weak bond decayed to 11.5), while a two-day debounce froze decay (weak bond reached 65.0). A sticky flag matched the full model 20/20 for strong bonds but 0/20 for mid-strength bonds of 30.
- Fix: Tune the debounce to the contact cadence, make the floor sign-aware if grudges should fade, and give flag-tier NPCs an expiry rule rather than a sticky flag.
- Why this fix: Each failure traces to a threshold interacting with cadence or magnitude that the kernel states without numbers.
- Rule of thumb: In this toy, a sticky floor protects strong and hostile bonds alike, and debounce length versus contact cadence decides whether decay ever runs, so test each guardrail against mid-strength bonds and regular light contact, not only strong idle bonds.
- Provenance (verified/assumed): Verified first-hand by running the saved sandbox; it is a reduced one-score model and no shipped game code was run.
- Composed: ideas:NPC-SIM/memory/practical-guardrails-at-scale, sandbox-one-state-vector-pheromone-view-outcome/E1, sandbox-combined-brain-builder-dog-trace-replay-parity-vs-order-dependence/E1
- Polarity: compatible
- Sandbox: sandboxes/2026-10-09__npc-memory-hysteresis-asymmetric-tiered-guardrails.py
- Prediction: Pure decay keeps 0 strong bonds; floor keeps all including hostile; asymmetric rate keeps key bonds above 20 at day 120; flag tier agrees fully; alternate-day contact blocks a one-day debounce.
- Observed: RESULT: FAIL A_kept=0 B_kept=24 B_hostile_kept=12 C_key=0 mid_sticky_agree=0.0 days_to_20 key=62 bg=15 poke debounce1=11.5 debounce2=65.0 parity=True order_ok=True
- Scenarios: 1) pure exponential; 2) floor plus debounce; 3) asymmetric rates; 4) flag tier on strong and mid bonds; 5) alternate-day contact, built to BREAK the debounce; 6) trace replay and reversed order
- Link: brain train auto pass 5
- Audited: 2026-10-12 · pass · Read the entry and its stored sandbox and re-ran it; it reproduces the recorded FAIL line exactly (A_kept=0 B_kept=24 hostile 12 days_to_20 key=62 bg=15 debounce1=11.5 debounce2=65.0 trace and order parity true). The decay, debounce-versus-cadence, mid-strength (30) and days-to-20 results are computed by the daily loop, not assumed, and the entry honestly reports its own missed prediction. Two caveats on scope: hostile bonds being kept 12/12 and the flag matching 20/20 for strong bonds follow by construction from an absolute-value floor, so they restate the design rather than test it; and update-order independence is trivially true because NPCs do not interact in this model. The Rule of thumb's claims about debounce length versus cadence and mid-strength bonds are the part that carries evidence, and those are covered. The claim is about a design pattern in a one-score toy, not a real library, so pass rather than modeled. · scheduled brain train session; loop 1 pass 3 audit; session_01LL6VFqb8pBPKJxf8rLawar
