# local/sandbox-kernel-room-acoustics — lessons

Project: local/sandbox-kernel-room-acoustics. Newest first.

---

## E2 — fitzroy and arau puchades reduce to eyring and overshoot in diffuse lumped rooms
- Date: 2026-10-12
- Project: local/sandbox-kernel-room-acoustics
- Tags: [acoustics][reverberation][simulation][sandbox]
- What: Tested whether the published non-uniform reverberation formulas, Fitzroy (1959) and
  Arau-Puchades (1988), settle the open Sabine-vs-Eyring question in very dead or
  lumped-absorption rooms, against the same deterministic Lambertian ray tracer that opened it.
  9 rooms: the 5 dead/lumped rooms of the tension plus 4 held-out layouts.
- Why built: The tension found Eyring closer in compact uniform dead rooms but Sabine closer in a
  corridor and a flat hall with lumped absorption. The hypothesis was that Sabine vs Eyring is the
  wrong axis and the per-axis formulas built for uneven, elongated rooms resolve it.
- Design: Tracer copied verbatim from the earlier bracket sandbox (4000 rays, seed 12345, 1 ms
  bins, T60 from the -5..-35 dB slope, mean free path checked against 4V/S). Fitzroy
  T = 0.161V/S^2 * sum_j(-S_j/ln(1-a_j)) and Arau-Puchades T = prod_j[0.161V/(-S ln(1-a_j))]^(S_j/S)
  over the three opposite-wall pairs, with Sabine, Eyring, Millington-Sette and Kuttruff (traced g2)
  alongside. Pass bar: Fitzroy or Arau-Puchades within 15% of traced T60 in all 9 rooms.
- Got right: The prediction held on its main points: under uniform absorption both formulas are
  algebraically Eyring (identical to 0.000%), so the corridor stays at -53% whatever formula is
  used; Arau-Puchades lands within 10% in the floor+ceiling flat hall (+9.5%) while Fitzroy
  overshoots it by +656%; in the one-face cube Fitzroy +329% and Arau-Puchades +129%.
- Where/why it failed: The hypothesis failed: Fitzroy was within 15% in 0/9 rooms (worst +656%),
  Arau-Puchades in 1/9 (worst +129%), Millington-Sette in 0/9 (about -50% wherever one face is
  very absorbent). Both per-axis formulas let a reflective wall pair carry the decay, which only
  happens when reflections stay specular along that axis; diffuse reflection re-randomises direction
  every bounce, so the absorbent face drains every axis. Fitzroy over-predicted 1.3x to 7.6x in all
  6 lumped rooms; Arau-Puchades ranged from -58% to +129%.
  My guess that Arau-Puchades over-predicts by 30% or more in every held-out room was too
  pessimistic: +15% (corridor with absorbent end walls) and +27% (floor-only hall).
- Fix: In a diffusely reflecting room keep the Sabine/Eyring bracket, and treat Kuttruff with a
  measured or modelled path-length variance as the closer single estimate where it holds
  (within 11% in 5 of 9 rooms: every compact or one-face-lumped room). Reserve Fitzroy and
  Arau-Puchades for rooms whose surfaces reflect specularly, where a grazing axis mode really
  survives. In the three rooms with absorption on the large faces of a long or flat room (uniform
  corridor, floor+ceiling hall, absorbent-sided corridor) Sabine stayed closest (-5%, -3%, -28%).
- Why this fix: The per-axis formulas encode a non-diffuse decay model; the evidence says their
  error tracks how reflective the weakest axis pair is, not room shape. Kuttruff's correction is
  the only one here that uses the room's real path statistics, and it is what tracked the trace
  in compact and single-face-lumped layouts.
- Rule of thumb: Fitzroy and Arau-Puchades do not settle Sabine-vs-Eyring for a diffusely
  reflecting room: with uniform absorption they are Eyring exactly, and with lumped absorption
  they let the reflective axis pair carry the decay (Fitzroy 1.3x to 7.6x too long in 6/6);
  use them only when the surfaces reflect specularly, and otherwise bracket with Sabine and Eyring.
- Provenance (verified/assumed): Verified first-hand by the sandbox in this entry (9 rooms, all
  numbers below rerun with python3 -I) and the formulas checked first-hand against Prawda, Schlecht
  and Valimaki, "Evaluation of Reverberation Time Models with Variable Acoustics", SMC 2020,
  eqs. 3, 5 and 6 (m set to 0). The modelling assumptions are fully diffuse (Lambertian)
  reflection, no air absorption, no edge diffraction, shoebox geometry and a T30 fit extrapolated
  to 60 dB; real rooms with specular hard walls sit between this model and the one Fitzroy assumed.
- Composed: ideas:ROOM-ACOUSTICS/reverberation/bracket-t60-between-eyring-and-sabine/add-kuttruff-path-variance-to-close-the-gap, sandbox-kernel-room-acoustics/E1
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-12__fitzroy-and-arau-puchades-reduce-to-eyring-and-overshoot-in-diffuse-lumped-rooms.py
- Prediction: Fitzroy and Arau-Puchades equal Eyring to under 0.1% in the 3 uniform rooms (corridor
  stays about -53%); flat hall floor+ceiling 0.8: Arau-Puchades within 15%, Fitzroy over +100%;
  one-face cube: Fitzroy over +200%, Arau-Puchades over +50%; held-out lumped rooms: both over
  +30%; overall RESULT: FAIL (neither within 15% in all rooms).
- Observed: RESULT: FAIL F 0/9 AP 1/9 within 15% (S 4, E 3); uniform F=AP=E to 0.000%;
  mfp_ok=True. Errors S/E/F/AP in %: shoebox 0.8 +57/-22/-22/-22; small 0.7 +44/-16/-16/-16;
  corridor 0.8 -5/-53/-53/-53; flat hall floor+ceil -3/-37/+656/+9; cube one face +9/-1/+329/+129;
  BREAK corridor end walls -22/-25/+32/+15; shoebox one side wall +8/-1/+159/+76; flat hall
  floor only +17/-6/+163/+27; corridor sides+floor+ceil -27/-62/+63/-58. Kuttruff within 11% in
  5/9. Runtime 1.6 s.
- Scenarios: 1) shoebox 10x8x4 uniform 0.8; 2) small 6x5x3 uniform 0.7; 3) corridor 2x2x20
  uniform 0.8; 4) flat hall 20x16x3 floor+ceiling 0.8, walls 0.02; 5) cube 6^3 one face 0.9;
  6) BREAK: corridor 2x2x20 with only the two end walls at 0.9; 7) shoebox 10x8x4 one side
  wall 0.9; 8) flat hall 20x16x3 floor only 0.9; 9) corridor 2x2x20 sides, floor and ceiling 0.8,
  ends 0.02.
- Link: session; brain train gap (room-acoustics tension); session_01QGT1LfmPHPG99JEGaPhBwB

## E1 — eyring vs sabine in dead and flat rooms diffuse ray trace
- Date: 2026-10-12
- Project: local/sandbox-kernel-room-acoustics
- Tags: [acoustics][reverberation][simulation][sandbox]
- What: Built a deterministic diffuse ray tracer for shoebox rooms and compared traced T60 with Sabine, Eyring and Kuttruff, reproducing the kernel's 10x8x4 numbers and mapping where the estimator stops being reliable.
- Why built: The bracket-T60 kernel had no memory entry building against it and an open tension asked whether Eyring stays better in dead or lumped-absorption rooms.
- Design: Fibonacci start directions, golden-ratio low-discrepancy Lambertian reflections (no RNG), per-ray energy loss (1-a) at each wall hit, T60 from the -5 to -35 dB slope of the summed decay curve; four rooms.
- Got right: 10x8x4 at a=0.5 gave traced 0.272 s with Sabine +24.6%, Eyring -10.1% and Kuttruff +3.1%, matching the kernel's +23%, -11%, +1.6% within a few points.
- Where/why it failed: A 20x16x3 hall with floor and ceiling at 0.9 and walls 0.02 had Eyring 40.3% low and Sabine -0.3%, with Kuttruff -24.5%; uniform a=0.7 and 0.9 rooms had Eyring -12.2% and -23.0% (still closer than Sabine +51% and +96.9%) while Kuttruff overshot by +12.9% and +34.1%.
- Fix: Report Sabine and Eyring as bounds with Kuttruff as the estimate only near a=0.5; above that or with lumped absorption flag the estimate unreliable and prefer a trace, and do not assume Eyring is the safe side in a flat room with absorbing floor and ceiling.
- Why this fix: Diffuse-field formulas assume uniform decay across surfaces, and lumped absorption on the two largest faces breaks that, which is why the one lumped hall inverted the Sabine versus Eyring ranking while the uniform rooms kept it.
- Rule of thumb: Kuttruff's correction is a good estimate only near mean absorption 0.5 (+3.1% here, +12.9% at 0.7); with lumped absorption on the large faces of a flat room Sabine matched the trace and Eyring ran 40% low, so flag the estimate rather than trusting either.
- Provenance (verified/assumed): Verified first-hand by running the sandbox script in this session; all numbers are from that run.
- Composed: ideas:ROOM-ACOUSTICS/reverberation/bracket-t60-between-eyring-and-sabine
- Sandbox: sandboxes/2026-10-12__eyring-vs-sabine-in-dead-and-flat-rooms-diffuse-ray-trace.py
- Prediction: At 10x8x4 a=0.5 Sabine is +15 to +30% and Eyring -5 to -17%, Kuttruff within 5%; the lumped flat hall has Eyring more than 25% low with Sabine closer; uniform dead rooms keep Eyring closer than Sabine (the case that could have failed).
- Observed: RESULT: PASS A Sabine +25% Eyring -10%; B Sabine -0% Eyring -40%; D Sabine +97% Eyring -23% (C a=0.7 Sabine +51% Eyring -12%)
- Scenarios: 1) 10x8x4 uniform 0.5; 2) BREAK: 20x16x3 floor and ceiling 0.9; 3) 6x5x3 uniform 0.7; 4) 6x5x3 uniform 0.9
- Link: brain train auto session 2026-10-12; session_01QoYzipjYSp8DTBoAoj5Bdh
- Cited-by: 2026-10-12 · projects/local__sandbox-kernel-room-acoustics.md#E2 · incompatible · sandboxes/2026-10-12__fitzroy-and-arau-puchades-reduce-to-eyring-and-overshoot-in-diffuse-lumped-rooms.py · observed RESULT: FAIL F 0/9 AP 1/9 within 15% (S 4, E 3); uniform F=AP=E to 0.000%; mfp_ok=True. Errors S/E/F/AP in %: shoebox 0.8 +57/-22/-22/-22; small 0.7 +44/-16/-16/-16; corridor 0.8 -5/-53/-53/-53; flat hall floor+ceil -3/-37/+656/+9; cube on… · session; brain train gap (room-acoustics tension); session_01QGT1LfmPHPG99JEGaPhBwB
