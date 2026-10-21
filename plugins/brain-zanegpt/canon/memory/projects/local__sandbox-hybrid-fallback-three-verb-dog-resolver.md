# local/sandbox-hybrid-fallback-three-verb-dog-resolver — lessons

Project: local/sandbox-hybrid-fallback-three-verb-dog-resolver. Newest first.

---

## E1 — sandbox hybrid fallback three verb dog resolver
- Date: 2026-09-30
- Project: local/sandbox-hybrid-fallback-three-verb-dog-resolver
- Tags: [ui][input][state][gamedev][testing]
- What: Sandbox applying the hint-first-with-validity-fallback press policy to the three-verb (talk, pet, sit) single resolver from the dog lessons, to see whether it converts the valid-only policy's no-op presses into valid actions.
- Why built: The hybrid lesson used a two-role model and the dog lesson used a three-verb model with three other policies; the pair was single-source, so this checks the hybrid on the dog's own verb set.
- Design: Deterministic, no RNG, 600 ticks, period 5. Talk is available at phases 0 and 1, pet at phases 1 to 3, sit always; priority talk over pet over sit. Hint is the resolve at tick t, press lands at t plus lag, lags 0/1/2/4. Policies: re-resolve, valid-only token, and hybrid (hint if still valid, else re-resolve).
- Got right: Hybrid is rule-valid 600/600 at every lag. Presses the valid-only token policy drops (0/240/480/120 at lags 0/1/2/4) all become valid actions under the hybrid, and hybrid hint mismatch equals that same count.
- Where/why it failed: Re-resolve mismatches the hint 0/360/600/360 and the hybrid 0/240/480/120, so mismatch is not monotonic in lag: lag 4 (one below the period) is better than lag 2, since a lag close to a whole cycle realigns the availability phase.
- Fix: Use the hybrid for the dog press handler and evaluate lag values around multiples of the availability period, not only small lags.
- Why this fix: The hybrid never idles on an invalid hint and never executes an invalid verb, and its only deviation from the hint is on presses the token would have wasted.
- Rule of thumb: In a multi-verb resolver a hint-first fallback turns every dropped press into a valid action; test lags near the availability period because mismatch is not monotonic in lag.
- Provenance: Verified first-hand by running the Python sandbox (sb/p3.py) and observing the counts listed above; the absolute counts differ from the dog entry because the availability phases here are my own choice.
- Composed: sandbox-combined-action-resolver-hybrid-fallback/E1, sandbox-combined-action-resolver-dog-stale-hint-press-lag/E1, dog/E20
- Link: session_01AfTzT5iniwzFpQZUQQxJ7F

