# Rebuild of: a content-word subsequence title matcher that keeps hyphens does worse than plain substring on stutter
# hooks; splitting on hyphens makes it find all. Own 8 (title, line) pairs written by me; stopwords are my own list.
# Empty content-word title falls back to substring. Prediction: substring 4/8, hyphens-kept 3/8, hyphens-split 8/8.
import re
STOP = {"i", "a", "the", "it", "and", "you", "me", "to", "be"}
def toks(s, keep_hyphen): return re.findall(r"[a-z'-]+" if keep_hyphen else r"[a-z']+", s.lower())
def subseq(need, have):
    it = iter(have); return all(any(w == h for h in it) for w in need)
def token_match(title, line, keep):
    need = [w for w in toks(title, keep) if w not in STOP]
    return title.lower() in line.lower() if not need else subseq(need, toks(line, keep))
PAIRS = [("Bye Bye Bye", "bye-bye-bye, don't wanna be a fool"), ("Na Na Na", "na na na, hey hey"),
         ("I-I-I", "and I-I-I will always love you"), ("Ba-Ba-Baby", "ba ba baby come back"),
         ("Shake It Off", "shake, shake, shake it off"), ("Ooh La La", "ooh-la-la, the night is young"),
         ("Hey Ya", "hey-ya! hey-ya!"), ("Stop", "s-s-stop right there")]
BREAK = [("Stop", "the bus stopped"), ("Na Na", "banana nation")]   # false-positive check, not stutter hooks
sub = sum(t.lower() in l.lower() for t, l in PAIRS)
kept = sum(token_match(t, l, True) for t, l in PAIRS)
split = sum(token_match(t, l, False) for t, l in PAIRS)
for t, l in PAIRS: print(f"{t!r:15} sub={t.lower() in l.lower()!s:5} kept={token_match(t, l, True)!s:5} split={token_match(t, l, False)!s:5}")
fp = [(t, l, t.lower() in l.lower(), token_match(t, l, False)) for t, l in BREAK]
print("false-positive probes (title absent): (title, line, substring, split) ->", fp)
ok = kept < sub and split == len(PAIRS)
print("RESULT: %s stutter titles: substring %d/8, hyphens-kept token matcher %d/8, hyphens-split %d/8; substring false-positives %d/2, split %d/2" % (
    "PASS" if ok else "FAIL", sub, kept, split, sum(x[2] for x in fp), sum(x[3] for x in fp)))
