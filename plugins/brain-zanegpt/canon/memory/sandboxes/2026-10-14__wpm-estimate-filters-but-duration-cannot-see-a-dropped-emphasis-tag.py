"""Apply VOICE/timing/wpm-duration-estimate-is-a-filter-not-a-predictor with VOICE/markup/unsupported-tags-fail-silently,
re-verifying pocketzane/E5 (accepted-but-ignored tags) and warden-fables/E1 (a break tag that is a silent no-op).
Toy TTS: duration = words*60/wpm_voice + honoured break seconds. Voices differ in wpm and in which markup they honour.
Prediction (before first run):
 P1 estimate = words/150 (pauses ignored) used as a filter at budget 8 s: it flags every line that is truly over
    budget on a 150 wpm voice that honours breaks ONLY IF pauses are small; with 0.9 s breaks on verse lines it MISSES
    at least 1 over-budget line (false negative). Adding the pause allowance (+10%/+breaks) removes all misses.
 P2 as a predictor the relative error across voices at 130/150/180 wpm exceeds +-15% on at least one line.
 P3 a voice that silently drops <break> shortens each line by exactly its break seconds; a duration spot-check with a
    5% tolerance catches it on 100% of lines that carry breaks.
 P4 a voice that silently drops <emphasis> (assumed to cost 4 percent duration when honoured) is caught by 0 of 3 lines
    at a 5% duration tolerance, 3 of 3 at a 2% tolerance; the per-tag honoured check catches 3 of 3 at any tolerance.
 P5 (break) with no breaks and a 150 wpm voice the estimate is exact (0 error)."""
LINES = [  # (words, breaks_seconds_list, has_emphasis)
    (22, [0.9, 0.9], False), (18, [0.9], True), (26, [0.9, 0.9, 0.9], False), (14, [], True),
    (30, [0.9], False), (20, [0.9, 0.9], True), (12, [0.9], False), (24, [], False),
]
BUDGET = 8.0
VOICES = {"A": dict(wpm=150, breaks=True, emph=True), "B": dict(wpm=130, breaks=False, emph=True),
          "C": dict(wpm=180, breaks=True, emph=False)}

def actual(line, v):
    w, br, _ = line
    base = w * 60 / v["wpm"]
    if line[2] and v["emph"]:
        base *= 1.04          # assumed: honoured emphasis slows the line by 4 percent
    return base + (sum(br) if v["breaks"] else 0.0)

def est(line): return line[0] * 60 / 150
def est_pad(line): return line[0] * 60 / 150 + sum(line[1])

# P1
A = VOICES["A"]
over = [i for i, l in enumerate(LINES) if actual(l, A) > BUDGET]
miss = [i for i in over if est(LINES[i]) <= BUDGET]
miss_pad = [i for i in over if est_pad(LINES[i]) <= BUDGET]
print("P1 over-budget", over, "missed by plain estimate", miss, "missed with pause allowance", miss_pad)
# P2
errs = [(est(l) - actual(l, v)) / actual(l, v) for v in VOICES.values() for l in LINES]
print("P2 relative error range", round(min(errs), 3), round(max(errs), 3))
# P3 : same voice A with breaks vs dropped (silent)
drop_break = dict(A, breaks=False)
carry = [l for l in LINES if l[1]]
caught = sum(abs(actual(l, A) - actual(l, drop_break)) / actual(l, A) > 0.05 for l in carry)
exact = all(abs((actual(l, A) - actual(l, drop_break)) - sum(l[1])) < 1e-9 for l in carry)
print("P3 break drop caught by duration check", caught, "of", len(carry), "exact shrink", exact)
# P4
drop_emph = dict(A, emph=False)
em = [l for l in LINES if l[2]]
caught_e = sum(abs(actual(l, A) - actual(l, drop_emph)) / actual(l, A) > 0.05 for l in em)
caught_e2 = sum(abs(actual(l, A) - actual(l, drop_emph)) / actual(l, A) > 0.02 for l in em)
flag_e = sum(1 for l in em if not drop_emph["emph"])      # per-tag honoured check
print("P4 emphasis drop caught by duration at 5%", caught_e, "at 2%", caught_e2, "of", len(em), " by per-tag check", flag_e)
# P5
nb = (20, [], False)
e5 = abs(est(nb) - actual(nb, A))
print("P5 error with no breaks at 150 wpm", e5)
ok = (len(miss) >= 1 and miss_pad == [] and min(errs) < -0.15 or max(errs) > 0.15) and caught == len(carry) and exact \
     and caught_e == 0 and caught_e2 == len(em) and flag_e == len(em) and e5 == 0
print("RESULT:", "PASS" if ok else "FAIL",
      f"missed_plain={len(miss)} missed_padded={len(miss_pad)} err_range=({min(errs):.2f},{max(errs):.2f}) break_drop_caught={caught}/{len(carry)} emph_drop_caught_by_duration_5pct={caught_e}/{len(em)} at_2pct={caught_e2}/{len(em)} by_tag_check={flag_e}/{len(em)}")
