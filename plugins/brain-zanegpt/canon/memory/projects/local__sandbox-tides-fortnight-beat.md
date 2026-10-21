# local/sandbox-tides-fortnight-beat — lessons

Project: local/sandbox-tides-fortnight-beat. Newest first.

---

## E1 — tides fortnight beat vs peak count vs alias
- Date: 2026-10-13
- Project: local/sandbox-tides-fortnight-beat
- Tags: [tides][sandbox][numerics][sampling][model]
- What: Deterministic tide model: M2 (12.4206 h) plus S2 (12 h) with an optional diurnal K1; the spring-neap cycle is read from the daily-range series by a period scan, by peak counting, and from a lone M2 sampled once a day.
- Why built: Apply the kernel that spring-neap is the M2/S2 beat, derived from two periods rather than stored, and re-check brainwork/E213's warning about reading cycles by peak counting.
- Design: 240 days of hourly heights; daily range = max minus min per day; DFT scan 5 to 30 d at 0.05 d steps; four scenarios, two built to break the claim (S2 removed; M2 alone sampled daily).
- Got right: Beat formula 1/(1/12 - 1/12.4206) = 14.765 d matched the scan (14.75 d with and without K1) and the lone-M2 case was flat (range spread 0.039) so the cycle needs both constituents.
- Where/why it failed: Daily sampling of M2 alone shows an apparent 14.75 d period (alias of 1.9323 cycles/day at 0.0677) with no S2 present, so a fortnight seen at day resolution is not proof of a beat. Also the K1 peak-counting failure of E213 did not reproduce on the daily-range series (14.67 d); that failure needs raw day-resolution heights.
- Fix: Derive the fortnight from the two periods, confirm by a period scan of an hourly-resolved envelope, and check that removing one constituent kills the cycle before trusting a day-sampled period.
- Why this fix: The removal test separates a real beat from a sampling alias that lands on nearly the same number, which a scan alone cannot do.
- Rule of thumb: Derive spring-neap from the M2/S2 beat and confirm by scan on hourly data; if the cycle survives with S2 removed or only appears at day-sampling, it is an alias, not a beat.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script. The raw-height peak counting of E213 was not re-run, only the daily-range variant.
- Composed: ideas:TIDES/spring-neap-is-the-m2-s2-beat-not-a-stored-cycle, brainwork/E213, ideas:DSP/peak-meter-blind-to-aliasing
- Sandbox: sandboxes/2026-10-13__tides-fortnight-beat-vs-peak-count-vs-alias.py
- Prediction: Scan reads 14.77 d within 0.4 in the M2+S2 and +K1 cases; peak counting with K1 reads more than 1 d off; M2 alone gives a flat range; daily-sampled M2 gives some spurious period.
- Observed: RESULT: PASS scan=14.75/14.75 d vs beat 14.765; K1 peakcount 14.67 d (prediction wrong: no big error); flat without S2 (0.039); daily-sampled lone M2 fakes 14.75 d.
- Scenarios: 1) M2+S2; 2) M2+S2+K1; 3) M2 only, built to BREAK the beat claim; 4) M2 only sampled once a day, built to BREAK day-resolution trust.
- Link: brain train auto session 2026-10-13; session_01WtWcTgcKWwuvhJ9RsCQX9c
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E221 · compatible · sandboxes/2026-10-14__tides-third-constituent-alternates-spring-heights.py · observed RESULT: PASS spring spacing 14.75 d (M2+S2), 14.78 d with N2; spring height step 0.000 vs 0.241; without S2 spacing 13.04 d · brain train auto loop 2 pass 5, 2026-10-14; session_01Fej6hmi1TecJBFrsQdbvMU
- Audited: 2026-10-14 · modeled · Read the entry and reran its stored sandbox (PASS, scan 14.75 d vs beat 14.765, flat range 0.039 without S2, daily-sampled lone M2 reads 14.75 d). The model computes its results rather than assuming them: the heights are summed cosines, the period comes from a DFT scan of the daily-range series, and the alias case is measured from samples, with the alias theory printed only as a comparison. It covers what the Rule of thumb says (scan on hourly data, remove S2, day-sampling alias). The limit is that the claim is about real tides, while every case is a hand-written sum of two or three cosines, where a beat is guaranteed by construction; no gauge record, nodal modulation or declination effect was tested, so the verdict is modeled rather than pass. · brain train auto loop 1 pass 3, session_01AMmNLeLopueLdsbKx7q1Lv
- Cited-by: 2026-10-14 · projects/pappydapimp69__brainwork.md#E268 · compatible · sandboxes/2026-10-14__atlas-pad-extrude-bleed-sandbox.py · observed RESULT: PASS s1=(0,0) s2=(1.0,0) s3=(0.5,0) s4=(0,0.5) s5=(0,0) min-clean-pad-by-mip-level={0:1,1:2,2:4,3:8}. The mip level sweep also showed that point-sampling every second texel of an alternating pattern reads 0.0 against a true mean of… · brain train auto pass 1, session_01CwpncTDkwf6YoSaQyXUsNe
