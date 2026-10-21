# local/sandbox-ratelimit — lessons

Project: local/sandbox-ratelimit. Newest first.

---

## E1 — token bucket clock backward drains tokens
- Date: 2026-07-11
- Project: local/sandbox-ratelimit
- Tags: [algo][state][process]
- What: A naive token-bucket rate limiter silently DRAINS tokens when it receives a request timestamped earlier than its last-seen timestamp — even a zero-cost request.
- Why built: Sandbox to mine a genuinely new domain (rate limiting) not yet covered in this repo. Built a standard token-bucket: refill = elapsed_time * rate, capped at capacity.
- Design: `_refill(now)` computes `elapsed = now - self.last`, adds `elapsed * refill_rate` to the token count (clamped to capacity), and sets `self.last = now`.
- Got right: The core algorithm (lazy refill computed on each call, no background timer) is the standard, correct shape for a token bucket.
- Where/why it failed: Reproduced directly: bucket at 2/5 tokens, called with `now` 0.5s EARLIER than the last call. `elapsed` came out negative (-0.5), so `tokens + elapsed*rate` computed 2 + (-0.5) = 1.5 — the bucket lost half a token from a request that cost nothing, purely because the clock read backward. Verified with a real test (`test_bucket.py::test_clock_goes_backward`): tokens measurably went 2 → 1.5. This is a realistic scenario, not a contrived one — NTP corrections, or two callers reading a wall clock without perfect ordering, both produce non-monotonic timestamps in practice.
- Fix: Clamp elapsed to `max(0.0, now - self.last)` so a backward clock read can never subtract tokens, and clamp `self.last = max(self.last, now)` so a stale/backward timestamp can't move the bucket's own clock backward either.
- Why this fix: The bucket's job is to gate REQUESTS, not to be a precise clock — treating "time didn't move forward" as "no refill happened" (rather than "negative refill happened") is the only interpretation that can't be exploited or accidentally triggered to under-serve legitimate traffic.
- Rule of thumb: Any rate limiter (or other structure) that derives a delta from `now - last_seen_time` must clamp that delta to be non-negative — never assume caller-supplied or even system timestamps are monotonically increasing.
- Provenance (verified/assumed): Verified first-hand — wrote the implementation, reproduced the exact token-drain with a real test run, applied the fix, and re-ran the same test to confirm tokens no longer decrease (2.0 → 2.0 instead of 2.0 → 1.5).
- Link: this session, `sandbox-ratelimit/bucket.py` + `test_bucket.py` (scratchpad, not committed — sandbox code discarded per convention, lesson kept)
- Cited-by: 2026-07-13 · projects/local__sandbox-combined-skilltree-formula.md#E3 · compatible · no sandbox · session (query brain for "train seams in combination, in sandbox environments"), sandbox script sweep_ratelimit.mjs, no code change to a shipping project
