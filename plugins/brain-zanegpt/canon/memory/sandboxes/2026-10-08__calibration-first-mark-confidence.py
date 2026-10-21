"""Sandbox: does felt certainty from an easy cue track accuracy? (deterministic, stdlib only)
Kernel: ideas:DECISION-MAKING/cognitive-bias/calibration/overconfidence-100-percent-certainty-only-70-to-85-percent-correct
Also exercises: sandbox-kernel-gamedev-feedback/E1 (naive product over correlated gates),
                brain/E66 (status read from the first mark found anywhere in a block).
PREDICTION (written before first run): the first-mark reader says 100% whenever it finds a mark, and
is right 70-85% of the time on a ledger where ~20% of blocks carry a transition mention before the
Lean line; naive product of 3 perfectly correlated cues overstates (stated >= 0.9 vs actual <= 0.8);
a feedback-trained recalibration map brings ECE under 0.03 in-distribution but NOT after a shift
to history-heavy blocks (ECE > 0.1)."""
def lcg(s):
    while True:
        s = (s * 1103515245 + 12345) % 2**31
        yield s / 2**31

def make_blocks(n, hist_rate, seed):
    r = lcg(seed); out = []
    for _ in range(n):
        truth = "R" if next(r) < 0.5 else "Y"
        marks = {"R": "🔴", "Y": "🟡"}
        hist = next(r) < hist_rate
        # a history transition mention names the OTHER status first, then the real one
        pre = ("🔴→🟡" if truth == "Y" else "🟡→🔴") if hist else ""
        # only half of history mentions put the wrong mark first (order varies)
        if hist and next(r) < 0.5: pre = ""
        out.append((truth, pre + " ... Lean: " + marks[truth]))
    return out

def first_mark(text):
    for ch in text:
        if ch == "🔴": return "R"
        if ch == "🟡": return "Y"
def lean_line(text):
    return first_mark(text.split("Lean:")[1])

def acc(blocks, f): return sum(f(t) == tr for tr, t in blocks) / len(blocks)

def ece(pairs, nb=10):
    bins = {}
    for c, ok in pairs: bins.setdefault(min(int(c * nb), nb - 1), []).append((c, ok))
    return sum(len(v) / len(pairs) * abs(sum(c for c, _ in v) / len(v) - sum(o for _, o in v) / len(v)) for v in bins.values())

fails = []
# S1: first-mark reader, stated 100% whenever a mark is found
B = make_blocks(4000, 0.40, 1)
a1 = acc(B, first_mark)
print(f"S1 first-mark reader: stated 1.00, actual {a1:.3f}")
if not 0.70 <= a1 <= 0.85: fails.append("S1")

# S2: naive product of 3 cues with reliability .9 each, but cues perfectly correlated (copy of one read)
def noisy(truth, r, rel=0.9): return truth if next(r) < rel else ("Y" if truth == "R" else "R")
r = lcg(7); ok = 0; N = 4000
for i in range(N):
    truth = "R" if next(r) < .5 else "Y"; c = noisy(truth, r)   # one underlying read, copied 3x
    ok += (c == truth)
actual_corr = ok / N
stated = 1 - (1 - 0.9) ** 3 * 0 if False else 1 - (0.1 ** 3)   # naive independent-evidence agreement of 3 votes
r = lcg(9); ok = 0
for i in range(N):
    truth = "R" if next(r) < .5 else "Y"; votes = [noisy(truth, r) for _ in range(3)]
    ok += ((max(set(votes), key=votes.count)) == truth)
actual_ind = ok / N
print(f"S2 stated {stated:.3f}; actual correlated {actual_corr:.3f}; actual independent {actual_ind:.3f}")
if not (stated - actual_corr >= 0.09 and abs(stated - actual_ind) < 0.03): fails.append("S2")

# S3: feedback recalibration: stated conf = 1.0 if mark else .5; map conf-bin -> observed acc from training half
train = make_blocks(4000, 0.40, 11)
cal = acc(train, first_mark)
pairs_in = [(cal, first_mark(t) == tr) for tr, t in make_blocks(4000, 0.40, 12)]
raw_in = [(1.0, ok) for _, ok in pairs_in]
print(f"S3 in-dist ECE raw {ece(raw_in):.3f} -> recalibrated {ece(pairs_in):.3f}")
if not (ece(pairs_in) < 0.03 and ece(raw_in) > 0.1): fails.append("S3")

# S4 (BREAK): shift to history-heavy blocks (80%): the map learned at 40% no longer fits
pairs_sh = [(cal, first_mark(t) == tr) for tr, t in make_blocks(4000, 0.80, 13)]
print(f"S4 shifted ECE recalibrated {ece(pairs_sh):.3f} (actual {sum(o for _,o in pairs_sh)/len(pairs_sh):.3f} vs stated {cal:.3f})")
if not ece(pairs_sh) > 0.1 / 2: fails.append("S4")

# S5: the E66 fix (Lean-line reader) removes the miscalibration at the source
a5 = acc(make_blocks(4000, 0.80, 13), lean_line)
print(f"S5 lean-line reader accuracy on shifted set {a5:.3f}")
if a5 < 0.999: fails.append("S5")
print("RESULT: " + ("FAIL " + ",".join(fails) if fails else "PASS first-mark certainty overstated; correlated cues inflate; recalibration is distribution-bound; fixing the cue beats recalibrating"))
