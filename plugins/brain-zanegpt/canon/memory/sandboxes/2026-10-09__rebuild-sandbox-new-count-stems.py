"""Blind rebuild: does counting new content words track new ideas per line,
and does a '>3 new words' flag match a hand 'overloaded' label?

PREDICTION (written before the first run, from a hand trace of this fixture):
  - raw new-word count differs from hand idea count on >= 8 of 12 lines (hand trace: 9)
  - stemming + stopwords alone does NOT fix it: stemmed count still differs on >= 6 of 12
    (compounds like 'kitchen light' stay two words)
  - the '>3 new words' flag matches the hand 'overloaded' label on only 7-9 of 12
    (false positives on noun-dense one/two-idea lines), NOT 12/12.
  - breaker scenarios: a 4-word one-idea line flags (false positive); a 3-word
    three-idea line does not flag (false negative).
Claim passes only if raw off >= 6 AND flag matches 12/12.
"""
import re

STOP = set("the a an and then she her he it on in up under beside of to near nothing two was were".split())

def stem(w):
    for suf in ("ing", "ed", "es", "s", "ly"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            break
    if w.endswith("e") and len(w) > 3:
        w = w[:-1]
    return w

def toks(line):
    return [t for t in re.findall(r"[a-z]+", line.lower()) if t not in STOP]

def new_counts(lines):
    seen_raw, seen_stem, out = set(), set(), []
    for ln in lines:
        ts = toks(ln)
        raw = {t for t in ts if t not in seen_raw}
        st = {stem(t) for t in ts} - seen_stem
        seen_raw |= set(ts)
        seen_stem |= {stem(t) for t in ts}
        out.append((len(raw), len(st)))
    return out

# (line, hand idea count, hand overloaded = 4+ distinct new ideas)
DOC = [
    ("The kitchen light flickers.", 2, False),
    ("Flickering lights annoyed the tired cook.", 2, False),
    ("She set a coffee cup on the counter.", 2, False),
    ("The counter held two cups.", 1, False),
    ("Then the fridge hummed, the kettle whistled, the toaster popped, and the dog barked.", 4, True),
    ("Morning sun warmed the tile floor.", 3, False),
    ("She sighed.", 1, False),
    ("The sun warmed her feet.", 1, False),
    ("Dishes piled up beside the sink, soaking in grey water.", 2, False),
    ("Dish soap, sponge, brush, and bleach waited under the sink.", 4, True),
    ("Water dripped slowly.", 1, False),
    ("Nothing moved.", 1, False),
]
BREAKERS = [  # fresh docs, each one line
    ("Big old red barn door.", 1, False),      # 4 words, 1 idea
    ("Wolf, rain, fire.", 3, False),            # 3 words, 3 ideas
    ("Dog, cat, bird, fish.", 4, True),         # 4 words, 4 ideas
]

counts = new_counts([d[0] for d in DOC])
raw_off = sum(1 for (r, s), d in zip(counts, DOC) if r != d[1])
stem_off = sum(1 for (r, s), d in zip(counts, DOC) if s != d[1])
flag_raw = sum(1 for (r, s), d in zip(counts, DOC) if (r > 3) == d[2])
flag_stem = sum(1 for (r, s), d in zip(counts, DOC) if (s > 3) == d[2])
for (ln, h, o), (r, s) in zip(DOC, counts):
    print(f"raw={r} stem={s} hand={h} over={int(o)} | {ln[:50]}")
bk = []
for ln, h, o in BREAKERS:
    r, s = new_counts([ln])[0]
    bk.append((r > 3) == o)
    print(f"breaker raw={r} hand={h} flag={r>3} hand_over={o} match={(r>3)==o} | {ln}")
print(f"raw off {raw_off}/12; stemmed off {stem_off}/12; flag raw {flag_raw}/12; flag stem {flag_stem}/12; breakers matched {sum(bk)}/3")
pred_ok = raw_off >= 8 and stem_off >= 6 and 7 <= flag_raw <= 9 and bk == [False, False, True]
claim_ok = raw_off >= 6 and flag_raw == 12
print(f"prediction held: {pred_ok}")
print(f"RESULT: {'PASS' if claim_ok else 'FAIL'} raw off {raw_off}/12 (claim >=6 ok), stem off {stem_off}/12, >3 flag matched {flag_raw}/12 raw ({flag_stem}/12 stemmed) vs claimed 12/12; breakers {sum(bk)}/3")
