# local/sandbox-crypto-hmac — lessons

Project: local/sandbox-crypto-hmac. Newest first.

---

## E1 — hmac signing and constant time comparison both needed
- Date: 2026-07-20
- Project: local/sandbox-crypto-hmac
- Tags: [security][algorithm]
- What: Two composed findings about server-side score/token verification:
  (1) an unsigned score submission (`{playerId, score}`) has no way to
  detect client-side tampering at all; an HMAC-signed one
  (`{playerId, score, hmac(secret, playerId+score)}`) does, and correctly
  rejects an attacker replaying an OLD valid signature alongside a NEW
  tampered score. (2) verifying that HMAC with a naive early-exit
  string/byte comparison leaks a real timing signal proportional to how
  many leading characters of a guess match the correct value — the
  well-documented HMAC/token timing side-channel (OWASP guidance; the
  standard fix is a constant-time comparison, e.g. Python's
  `hmac.compare_digest`).
- Why built: `brain train new-domain`, seeding CRYPTOGRAPHY as a
  genuine gap (`brain query` returned zero real hits on HMAC/signing/
  constant-time-comparison topics specifically).
- Design: `sandbox.py` — real HMAC-SHA256 (Python's `hmac`/`hashlib`,
  not a toy reimplementation), zero RNG. Part 1: computed a real
  signature for `(player_id, score)`, confirmed an unsigned submission
  is always "accepted" (nothing to check), a tampered score's honestly-
  recomputed signature differs from the original, and replaying the
  ORIGINAL signature alongside a TAMPERED score fails verification.
  Part 2: modeled a naive early-exit comparison (`verify_naive_early_
  exit`, stops at the first mismatched character, counting comparison
  STEPS as the deterministic stand-in for wall-clock timing a real
  attacker would measure via repeated statistical sampling) against a
  constant-time comparison (`verify_constant_time`, XOR-accumulates
  across every character regardless of mismatches) for 4 guesses
  sharing 0, 4, 32, and all 64 correct leading hex characters of a
  real SHA-256 HMAC digest.
- Got right: used a REAL HMAC implementation (not a simplified stand-in)
  for the signing/tamper-detection half, and modeled the timing side-
  channel as a step COUNT rather than trying to measure real wall-clock
  time, which would have made the sandbox non-deterministic while
  testing the exact same underlying property (per-character comparison
  cost scales with matching prefix length in an early-exit comparison).
- Where/why it failed: the naive early-exit comparison's step count
  grew monotonically and substantially with the guess's matching prefix
  length — 1 step (0 matching chars) up to 64 steps (full 64-character
  match) — a real, exploitable signal: an attacker who can measure
  comparison timing (even noisily, via many repeated attempts) can
  recover the correct HMAC one character at a time by observing which
  guessed prefix takes longer to reject. The constant-time comparison
  took exactly 64 steps in every case, leaking nothing about how many
  characters matched.
- Fix: always sign score/leaderboard submissions with an HMAC (or
  equivalent MAC) over the full payload using a server-only secret,
  AND always compare the submitted MAC against the expected one with a
  constant-time comparison function (never a language's default
  `==`/byte-comparison, which very commonly short-circuits on first
  mismatch) — both halves are independently necessary; signing without
  constant-time comparison still leaks the correct signature via
  timing, and constant-time comparison without signing has nothing
  meaningful to compare in the first place.
- Why this fix: signing establishes WHAT should be trusted (a value
  the client cannot forge without the secret); constant-time comparison
  ensures the verification step itself doesn't leak information an
  attacker could use to forge that value anyway, incrementally, one
  character at a time — they defend against different attack shapes
  (payload tampering vs. side-channel signature recovery) and neither
  substitutes for the other.
- Rule of thumb: whenever verifying a value the client could have an
  incentive to forge (a leaderboard score, an auth token, a signed
  save file), check for BOTH properties independently: (a) is the
  value actually cryptographically signed/MACed over everything that
  matters, not just partially covered, and (b) is the comparison of
  the submitted signature against the expected one constant-time — a
  language's default equality/comparison operator on strings or byte
  arrays very commonly short-circuits on the first difference, and
  that short-circuit IS a measurable timing side-channel regardless of
  how strong the underlying MAC algorithm is.
- Provenance (verified/assumed): Verified first-hand — ran `sandbox.py`
  using Python's real `hmac`/`hashlib` (SHA-256), confirmed unsigned
  submissions are always accepted, signed ones detect a real tamper and
  reject a signature-replay attack, and the naive comparison's step
  count grows 1→5→33→64 across increasing prefix-match lengths while
  the constant-time comparison stays flat at 64. Re-ran as two
  independent process invocations; output byte-identical both times.
  Externally grounded in the standard HMAC timing-attack mitigation
  (OWASP; Python's own `hmac.compare_digest` documentation, which
  exists specifically for this reason).
- Composed: N/A
- Link: session 7195397b-63a9-5efe-a80b-2792eaa6645e (`brain train
  new-domain`, cryptography gap); sandbox
  `scratchpad/loop7/crypto/sandbox.py`, run twice as independent
  process invocations, outputs diffed identical
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E41 · compatible · sandboxes/2026-10-09__hmac-score-signing-needs-full-payload-and-constant-time-compare.py · observed RESULT: PASS early-exit compare leaked the full tag in 7949 queries, constant-time stopped it (5/5), and keyed-but-score-only, unkeyed and delimiter-free signing each still accepted forgeries · scheduled brain train run, gap pass 5; session_01MiqdeTN5cV7j1vm5wkPKVF
- Cited-by: 2026-10-09 · projects/pappydapimp69__brainwork.md#E43 · compatible · sandboxes/2026-10-09__pkce-s256-rfc-vector-and-interception-model.py · observed RESULT: PASS RFC 7636 Appendix B verifier and challenge reproduced exactly; padded standard base64 differs; plain redeemed by an interceptor, S256 not; 43-128 length bounds hold at 32/31/96/97 octets; hash-prefix leak costs 108 then 20778… · scheduled brain train run, loop 2 gap pass 5; session_01MiqdeTN5cV7j1vm5wkPKVF
- Audited: 2026-10-15 · modeled · Read the entry and its design. The signing half uses real HMAC-SHA256 from the standard library and computes tamper rejection and old-signature replay rejection, so that part is tested, not assumed. The timing half counts comparison steps in a hand-written early-exit comparison as a stand-in for wall-clock time; step count rising with matching prefix is true by construction of that comparison, and no real timing, network or library comparison was measured. The claim concerns real systems (timing side channels in verification code), so only the signing half is verified and the timing half is a model, hence modeled. · scheduled brain train audit, loop 1 pass 3; session_01Jm2ZpWfo7KnvQ1ij9SF8pV
