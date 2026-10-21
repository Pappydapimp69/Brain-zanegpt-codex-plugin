# local/sandbox-humor-timing-figures — lessons

Project: local/sandbox-humor-timing-figures. Newest first.

---

## E1 — published timing figures vs stand in ratio law in the punchline syllable cap
- Date: 2026-10-10
- Project: local/sandbox-humor-timing-figures
- Tags: [humor][localization][simulation][testing]
- What: An external-fact check of the stand-in used for punchline timing in the humor-localization sandbox. That stand-in
  is a triangular law for the Spanish/English syllable ratio (mean 1.55, range 0.90 to 1.88) fitted to ten author-written
  hook pairs, plus a fixed 7.7 syllables/s rate, a 2.8 s window and no pause. It is a syllable-count law, not a published
  pause or laughter-latency figure. Published timing figures read in the sources: median conversational gap +100 ms, mean
  +208 ms, language means +7 to +469 ms (Stivers et al. 2009); laughter starts within 0.3 s of the laughable in only 30%
  of cases, mean start gap 1.3 to 2.2 s in dyadic talk (Tian, Mazzocconi and Ginzburg 2016); no evidence that punch lines
  are preceded by pauses in twenty joke performances (Attardo and Pickering 2011, abstract only); speech rate mean 6.63
  syll/s, SD 1.15, speakers 4.3 to 9.1, and information per syllable 4.8 to 8.0 bits across 17 languages (Coupe, Oh,
  Dediu and Pellegrino 2019). Propagating them through a window-fit and a clip-budget model moved the 11-syllable cap
  by +1 to +2 for the ratio law, by -1 to -2 for an inside-the-window pause, and by -3 for a human speaker rate spread.
- Why built: The localization lesson says an English hook of about 11 syllables guarantees a Spanish fit, and its ratio
  law was fitted to figures nobody re-read. I wanted to know whether published figures differ from the stand-in and,
  if they do, whether any conclusion changes. The model scores arithmetic for a scripted voice under stated
  assumptions; it says nothing about real audiences, real speakers or any named person.
- Design: Fit probability = P(n times R fits r times (window minus pause)), R from three laws (stand-in; uniform 1.0 to
  1.67, whose top is the largest syllable-count gap between any two of the 17 languages; triangular 1.0, 1.44, 1.67 with
  a mode recalled from an earlier Spanish-English information-density figure), r fixed or a 99-point quantile grid of a
  normal (7.7, 1.15) clipped to 4.3-9.1. n_safe is the largest n with fit at least 0.99, n* the largest with fit at
  least 0.5. A 10 s clip budget gives setup syllables = (clip - pause - hold) * r / R - punchline syllables, with hold
  after the punchline 0.3, 1.3 or 2.2 s from the laughter-start gaps. No random numbers. Caveats: the dyadic
  laughter data are not audience laughter at a scripted video joke, the Attardo abstract gives no pause length so the
  0.6 s pause is my design value, and the 1.44 mode is recalled from memory of Pellegrino 2011.
- Got right: The stand-in baseline reproduced the earlier result (fit(11) 1.00, fit(14) 0.43, n_safe 11). A pause of the
  mean turn gap (0.208 s) put inside the window cut n_safe to 10 and 0.6 s cut it to 9. A human-speaker rate spread
  (SD 1.15) dropped fit(11) from 1.00 to 0.87 and n_safe to 8. A fixed 6.63 syll/s voice gave n_safe 9. In the setup
  budget the choice of hold after the punchline swung 9.4 syllables (0.3 to 2.2 s), the ratio law 6.3 and the pause 3.0,
  ranked in that order as predicted.
- Where/why it failed: Two of seven predictions missed. I predicted n_safe 12 for both published-bound ratio laws but
  the triangular one gave 13, because 13 times 1.67 only just exceeds the cap and the fit stays above 0.99. I also
  predicted the ratio-law shift would be at most 1 at the 2.8 s window and it was 2 (11 to 13). Also the stand-in ratio
  is not refuted: the published cross-language information gap tops out at 1.67, below the stand-in maximum 1.88,
  but a transcreated hook can grow more than equal information needs, so the data cannot separate them.
- Fix: Treat the 11-syllable English cap as conservative on the ratio law (published bounds allow 12 to 13) but optimistic
  on delivery: subtract pause time from the window before counting syllables and check the voice rate directly, because
  a pause of 0.6 s or a 6.63 syll/s voice lowers the guaranteed cap to 9. Re-run the cap with the actual TTS rate and
  the actual pre-punchline pause, and size the post-punchline hold to the format (0.3 s for a cut, longer for a held
  reaction beat) before trimming the setup.
- Why this fix: The fit is a product of ratio and rate against window minus pause, so each input moves the cap in a
  known direction and size: the ratio law by 1 to 2 syllables, the pause by 1 to 2, the rate by 2 or 3. The pause
  and rate are controllable for a scripted voice, so measuring them removes the error, while the ratio law is a
  property of the line pairs and can only be bounded.
- Rule of thumb: When timing a scripted joke across languages, take the syllable cap from the ratio law but charge the
  pre-punchline pause against the window and use the actual voice rate: at a 2.8 s window the published figures moved the
  cap by about 1 to 2 syllables on the ratio and by 1 to 3 on pause and rate, and the hold after the punchline moved
  the setup budget most, so choose that hold deliberately and do not cite any published pause length as a rule,
  since the one study read here found no systematic pre-punchline pause.
- Provenance (verified/assumed): Verified first-hand: the full text of Stivers et al. 2009 (accepted-manuscript copy
  from the Max Planck repository) and Tian, Mazzocconi and Ginzburg 2016, the full text of Coupe et al. 2019 via
  Europe PMC, and the abstracts of Attardo and Pickering 2011 and Stivers 2009 via Crossref and PubMed; every quoted
  figure above was read in those texts. Verified first-hand by running the shipped sandbox this session: RESULT: FAIL
  with 5 of 7 pre-registered predictions held, numbers copied from that run. The laughter-hold values, the 0.6 s
  pause, the 10 s clip and the rate spread centre are my stated assumptions, and the 1.44 mode is recalled.
- Composed: ideas:LOCALIZATION/hooks/cap-the-english-hook-at-eleven-syllables-so-the-spanish-fits-three-seconds, local__sandbox-humor-localization/E1, pappydapimp69__tiktok-shop/E3
- Polarity: incompatible
- Sandbox: sandboxes/2026-10-10__published-timing-figures-vs-stand-in-ratio-law-in-the-punchline-syllable-cap.py
- Prediction: Before the first run: stand-in fit(11) 1.00, fit(14) 0.35-0.50, n_safe 11; both published-bound ratio laws
  n_safe 12; pause 0.208 s gives n_safe 10 and 0.6 s gives 9; a rate spread of SD 1.15 gives fit(11) 0.80-0.93 and
  n_safe at most 8; setup-budget swings hold 9.5, ratio 6.3, pause 3.0 (each within 1.5); ratio-law shift at most 1 at
  2.0 s and 2.8 s windows and 2 at 3.5 s; a fixed 6.63 syll/s voice gives n_safe 9.
- Observed: RESULT: FAIL 5/7 pre-registered predictions held; ratio-law swap moves n_safe 11 to 12/13, rate spread drops
  fit(11) to 0.87, hold choice swings setup budget 9.4 syllables. Missed: P2 (triangular gave 13) and P6 (shift 2 at 2.8 s).
- Scenarios: 1) three ratio laws at the 2.8 s window; 2) pause 0 to 1.0 s inside the window; 3) rate spread SD 0, 0.6
  and 1.15 for a human speaker; 4) 10 s clip setup budget under three hold lengths; 5) BREAK: ratio-law shift at
  windows 2.0, 2.8 and 3.5 s; 6) fixed scripted voice at 6.2, 6.63, 7.7 and 8.5 syll/s
- Link: session_01YFLLRpDsfZpRstb2KT2MQy

