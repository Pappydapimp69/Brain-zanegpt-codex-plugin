# local/2026-10-10__mean-synodic-new-moon-error-vs-independent-elongation-root-meeus-ch49-vs-ch47 — lessons

Project: local/2026-10-10__mean-synodic-new-moon-error-vs-independent-elongation-root-meeus-ch49-vs-ch47. Newest first.

---

## E1 — mean synodic new moon error vs independent elongation root meeus ch49 vs ch47
- Date: 2026-10-10
- Project: local/2026-10-10__mean-synodic-new-moon-error-vs-independent-elongation-root-meeus-ch49-vs-ch47
- Tags: [astronomy][lunar-phase][method][sandbox][verification]
- What: Re-checked the mean-synodic-phase kernel against an independent ground truth, the root of moon-minus-sun ecliptic longitude found by bisection from a truncated Meeus ch.47 lunar series and a solar equation-of-center series, over 2401 lunations (about 1903 to 2097). The mean phase, the dominant-term-only fix and the full ch.49 correction were each compared to that root.
- Why built: The kernel and its first sandbox compared against 17 new-moon instants recalled from almanac tables; a recalled table is a weak reference and 17 moons cannot say what the worst case is.
- Design: Deterministic python, dynamical time throughout so no delta-T enters the comparison. Bisection on a 1.2-day bracket around each candidate. Variants: mean phase only, minus 0.4072 sin M', the full 15-term ch.49 correction, and a four-term version without the eccentricity factor. Also an amplitude-sum bound, a 17-moon spread sample, and the share of lunations above 12 hours.
- Got right: The core of the kernel holds against an independent reference. The full correction agreed with the elongation root to 3.4 minutes at worst (rms 1.3 minutes, limited by my truncated longitude series), the dominant term alone left up to 5.0 h, and the four-term version left 21.9 minutes.
- Where/why it failed: The kernel's "off by up to about 12 hours" is a sample figure, not a bound. Over 2401 lunations the mean phase missed by up to 14.16 h, about 10% of lunations exceed 12 h, and a 17-moon sample spread across the span reached 13.9 h. My first two predictions (a 9 to 14 h range, then a sample under 12.5 h) were both wrong.
- Fix: State the mean-phase error as a bound of roughly 15 h (the sum of the periodic-term amplitudes, 14.99 h), observed 14.16 h, not as about 12 h; keep the correction and the UTC storage advice unchanged.
- Why this fix: The amplitude sum gives a bound that does not depend on which moons were sampled, and the run shows the observed maximum is within 1 h of it.
- Rule of thumb: Never quote a worst-case error from a hand-picked sample of reference points; bound it from the term amplitudes and check it on thousands of cases against a reference computed a different way, not recalled.
- Provenance (verified/assumed): Verified first-hand by running the sandbox, which failed on runs 1 and 2 and passed on run 3 with predictions rewritten between runs as recorded in its header. The Meeus coefficients were written from memory of the published method, not fetched, and agreement within minutes is what supports them.
- Composed: ideas:ASTRONOMY/lunar-phase/mean-synodic-phase-is-a-proxy-for-the-true-new-moon, sandbox-lunar-phase/E1, ideas:ZEN/verification/finger-is-not-the-moon-proxy-gauge
- Polarity: compatible
- Sandbox: sandboxes/2026-10-10__mean-synodic-new-moon-error-vs-independent-elongation-root-meeus-ch49-vs-ch47.py
- Prediction: Run 3: mean-phase max error in 13 to 15.2 h, a 17-moon spread sample max in 11 to 15 h, 5% to 15% of lunations above 12 h; dominant-only 3 to 6 h; full correction under 5 minutes against the elongation root; four-term version more than 3x the full error.
- Observed: RESULT: PASS mean max=14.16 h, dominant max=5.02 h, full ch49 max=3.40 min (rms 1.34), four-term max=21.9 min over k=-1200..1200; amplitude sum bound 14.99 h; spread-sample max 13.90 h; 10.1% of lunations above 12 h
- Scenarios: 1) mean phase over 2401 lunations; 2) dominant-term-only; 3) full 15-term correction against the independent elongation root; 4) BREAK: four-term correction without the eccentricity factor; 5) 17-moon spread sample versus the full span
- Link: scheduled brain train loop 2 pass 1, 2026-10-10; session_01GAVruHUPWaSKqD2KpxhoYC
- Audited: 2026-10-10 · modeled · Read the entry and its stored sandbox and reran it (RESULT: PASS, identical numbers: mean-phase max 14.16 h, full correction 3.40 min, four-term 21.9 min, 10.1% of lunations above 12 h). The result is computed, not built in: the reference is a bisection root of moon-minus-sun longitude from a separate series, and the entry honestly records two failed predictions. But the claim is about the real Moon, and the only reference is another hand-typed analytic series (Meeus coefficients written from memory, truncated), not observed or almanac data, so agreement within minutes shows the two chapters are mutually consistent, not that the 14 h and 15 h figures hold for real new moons. The amplitude-sum bound of 14.99 h is arithmetic over those same typed coefficients. The scope of the Rule of thumb (bound by amplitudes, test on thousands of cases against a differently computed reference) is covered by what was run; the astronomical numbers are modeled. · scheduled brain train auto loop 2 pass 3; session_017XFDGZpVKZxwBrhoPDGsz8
