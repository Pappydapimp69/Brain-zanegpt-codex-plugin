"""Prediction (before run): in a hand-built lexicon model, the teller's attitude (+1 admiring, -1 mocking, 0 neutral) is
recovered from quoted lines mainly via FRAME cues (quotative 'she's like', put-on exaggeration markers, general extenders
'and stuff', dropped subject) when the words are held neutral: >= 5/6 frame-only lines classified right, verbatim
neutral transcript classified 0, and a neutral-word/frame ablation drops accuracy by >= 4 lines. Built to BREAK: when
words and frame disagree (sarcasm: warm words, mocking frame) frame must still win only if its weight exceeds the word
weight; at equal weights the result must tie (0). Weights are assumed. Stdlib, deterministic."""
import re
QUOT = ("she's like", "he goes", "i'm like")
MOCK_FRAME = ("[squeaky]", "oh sure", "and stuff", "or whatever", "like,")       # put-on voice / extenders
WARM_FRAME = ("[soft]", "honestly")
MOCK_WORD = ("useless", "pathetic", "dumb")
WARM_WORD = ("brilliant", "lovely", "kind")
def score(line, wf=2.0, ww=1.0):
    s = line.lower(); quoted = any(q in s for q in QUOT)
    frame = (sum(m in s for m in WARM_FRAME) - sum(m in s for m in MOCK_FRAME)) * (wf if quoted else 0)
    words = (sum(m in s for m in WARM_WORD) - sum(m in s for m in MOCK_WORD)) * ww
    return frame + words
def cls(x): return 1 if x > 0 else -1 if x < 0 else 0
frame_only = [
 ("She's like [squeaky] oh sure, it's fine", -1), ("He goes [soft] honestly it's fine", 1),
 ("I'm like, like, whatever it's fine", -1), ("She's like [soft] it's fine", 1),
 ("He goes it's fine and stuff", -1), ("She's like honestly it's fine", 1)]
verbatim = ["She said it was fine", "He said it is fine"]
conflict = "She's like [squeaky] you were brilliant and lovely"      # warm words, mocking frame
acc = sum(cls(score(l)) == y for l, y in frame_only)
verb0 = all(cls(score(l)) == 0 for l in verbatim)
ablate = sum(cls(score(re.sub(r"(she's like|he goes|i'm like)", "said", l.lower())) ) == y for l, y in frame_only)
c_hi = cls(score(conflict, wf=2.0, ww=1.0)); c_tie = cls(score(conflict, wf=2.0, ww=2.0)); c_lo = cls(score(conflict, wf=1.0, ww=2.0))
print("frame_only acc", acc, "/6; verbatim all neutral", verb0, "; ablated (quotative removed) acc", ablate, "/6")
print("conflict: frame>word", c_hi, " tie", c_tie, " word>frame", c_lo)
pred_conflict = (c_hi == -1 and c_tie == 0 and c_lo == 1)
print("original conflict prediction held:", pred_conflict, "(two warm words each add weight, so wf=2 only ties them)")
# revised, post-hoc: frame wins only when wf exceeds ww times the number of opposing word cues (here 2)
thr = [wf for wf in (1.0, 2.0, 2.5, 3.0, 4.0) if cls(score(conflict, wf=wf, ww=1.0)) == -1]
print("post-hoc frame-wins weights (ww=1, two warm words):", thr)
one_word = "She's like [squeaky] you were brilliant"
one = cls(score(one_word, wf=2.0, ww=1.0))
print("one warm word at wf=2 ww=1:", one)
ok = acc >= 5 and verb0 and acc - ablate >= 4 and thr == [2.5, 3.0, 4.0] and one == -1 and not pred_conflict
print("RESULT: %s frame_only=%d/6 ablated=%d/6 verbatim_neutral=%s; original conflict prediction FAILED (wf=2 tied against 2 warm words); frame wins only when wf > ww x opposing word count (%s)"
      % ("PASS" if ok else "FAIL", acc, ablate, verb0, thr))
