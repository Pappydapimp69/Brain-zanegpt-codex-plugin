#!/usr/bin/env python3
"""Plain-language scorer, tested by metamorphic checks (stdlib only, deterministic).

PREDICTION (written before the first run):
  score = average sentence length (words)
        + 40 * share of words outside the common-word list
        + 0.5 * (digits + symbols per 100 words)
        + 2.0 * (jargon words per 100 words)          [weights fixed up front, never tuned]
  Higher = harder.  I expect:
   (1) tech > plainer in BOTH labeled pairs, by a margin of at least 10 points each.
   (2a) inserting jargon / long clauses into each plain reply raises its score by >= 3.
   (2b) a hand rewrite of each tech reply (long sentences split, jargon swapped for
        common words, every number kept) lowers its score by >= 10.
   (3) shuffling words inside each sentence leaves every word-based part identical (delta 0.0).
  Break scenario: a gamed text (every hard word replaced by 'thing', 3-word sentences)
  should score as the plainest of all even though it says nothing -> the scorer is a proxy.
  I expect to be wrong, if anywhere, on pair B (its plainer text has the number 650 and
  words like 'system', 'lessons', 'tested' that a small common list may not cover).

ADDENDUM (written AFTER the first run, which scored 18/22): v1 failed (2a) in two ways.
  A 55-word run-on of common words LOWERED the score (-1.0, -1.2) because the share-based
  parts dilute; a short extra sentence of hard words rose by only +1.3 / +2.0 (< my +3 bar).
  v2 adds one term motivated by the first failure only: + 0.5 * longest sentence (words).
  v2 prediction: the run-on now raises the score by >= 3; the hard-word insert stays under +3
  (nothing in v2 targets it); pairs still ranked right; shuffle still delta 0.0.
"""
import random
import re

COMMON = set("""
a an the and or but so if then than that this these those it its it's i you your yours we our us they them their he she him her his
is am are was were be been being do does did done doing have has had having not no yes can could will would should may might must
of in on at to for from by with about into out up down over under off as like also just only very more most much many some any all each
one two three four who what when where why how which there here now again still even too well
get got make made take took give gave say said tell told ask asked see saw look looked know knew think thought want wanted need needed
use used try tried work worked call called find found keep kept let put go went come came back
good bad new old big small long short high low right wrong true real same other own first last next
thing things way ways time times day days year years people person lot lots part kind bit
my me mine says saying hold held stop stopped start started help helped show showed turn turned run ran
choose chose pick picked agree agreed prove proved count counted drop dropped fix fixed beat beats
link links test tests tested guess guesses guessed idea ideas word words line lines example reason reasoned
because while after before until once never always maybe sure enough really almost without within through
don't doesn't didn't isn't wasn't can't won't couldn't wouldn't i'm you're we're they're that's there's what's let's i've you've
away already instead rather both few less least better worse best worst
number numbers weak strong stronger weaker shorter longer simple plain plainly
tells leave left case cases
""".split())

JARGON = set("""
confidence weights weight kernel rebuild audit audited audits metamorphic deterministic heuristic parameter parameters latency throughput
orchestration idempotent asynchronous serialization abstraction instantiate regression baseline threshold overturned unreviewed
discredited computed evaluation decision status owner family roll-up rollup repeats independent granular tension ledger
over-matches overmatches mock manner chart filed settled leaning leader propagation canonical canon provenance polarity
sandbox schema pipeline throttling heuristics orthogonal paradigm leverage utilize utilization methodology
""".split())

SYMBOLS = set("():;%+=/[]<>*#&_\\|{}$@^~")


def words(text):
    return re.findall(r"[a-z0-9]+(?:['\-][a-z0-9]+)*", text.lower())


def sentences(text):
    parts_ = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts_ if re.search(r"[A-Za-z0-9]", p)]


def parts(text):
    ws = words(text)
    sents = sentences(text)
    n = len(ws)
    asl = n / len(sents)
    # a token is "outside the list" if it is not common, and not a pure number
    uncommon = [w for w in ws if w not in COMMON and not w.isdigit()]
    unc_share = len(uncommon) / n
    digits = sum(c.isdigit() for c in text)
    syms = sum(c in SYMBOLS for c in text)
    jarg = sum(1 for w in ws if w in JARGON)
    return dict(n=n, sents=len(sents), asl=asl, unc_share=unc_share,
                digsym=digits + syms, jargon=jarg)


def score(text):
    p = parts(text)
    n = p["n"]
    return (p["asl"] + 40 * p["unc_share"] + 0.5 * (100 * p["digsym"] / n)
            + 2.0 * (100 * p["jargon"] / n))


WORD_PARTS = ("n", "asl", "unc_share", "digsym", "jargon")

# ---------------- fixtures: copied from replies.json (one rater, n=2 pairs) ----------------
PAIRS = {
    "A": dict(
        tech="Mock test on T1 (the later events are made up, and the weights are my guesses): step 1, as filed (chart + your call + new kernel) leader manner chart confidence 67 settled; step 2, a lesson says the chart over-matches, confidence 43 leaning; step 3, an audited lesson agrees, confidence 11 open. What held up: your call alone only reaches 33, which is leaning. Take your call away and it drops from 67 to 60. What failed on the first run: 10 repeats from one family scored as high as one independent rebuild. Halving each repeat fixed it: 10 repeats now give 75 against 78 for the rebuild.",
        plainer="Example 2: should the system accept a link that was only reasoned out, or only one that was actually tested? You chose tested only. When filed, it counted as settled. This session it got stronger, because one of my reasoned guesses was proven wrong when I tested it. If new evidence said testing misses good links, it would drop to leaning, then open. Your choice doesn't protect it."),
    "B": dict(
        tech="Result of the system's evaluation. Claim: the age-cutoff family should be heavily discredited (decision A, owner). Computed confidence: 38, leaning B (keep full weight). Decision status: overturned (evidence leads B at 38, above the 30 threshold). Evidence on the tension: A: 1 item, the roll-up lesson, unreviewed, weight 1. B: 2 items, one passed an independent rebuild (weight 3), one passed an audit (weight 2). The owner decision carries weight 0.",
        plainer="You said the age-cutoff family is a flaw. The system said maybe, but prove it. It agreed the family has way too many lessons. About 650 of them say the same few things. So it stopped training on them. It didn't agree the lessons should be thrown out. Most of them passed their tests. Three out of four held up. The system doesn't count opinions without proof. That goes for yours and mine."),
}

# Hand rewrites of the TECH replies: sentences split, jargon swapped for common words,
# EVERY number kept (so the intrinsic content is not cut, only the packaging).
TECH_REWRITE = {
    "A": "This is a test run. The later events are made up. The weights are my guesses. At first, the idea counted as settled, at 67. Then one lesson said the idea matches too much. It dropped to 43, which is leaning. Then a tested lesson agreed. It dropped to 11, which is open. Your call alone only reaches 33. That is still leaning. Take your call away and the number drops from 67 to 60. The first run had a problem. 10 repeats from one family scored as high as one new test. So I halved each repeat. Now 10 repeats give 75. The new test gives 78.",
    "B": "Here is what the system found. The claim was that the age-cutoff family should be mostly dropped. That was your choice. The system gave it a score of 38, so it leans to keep full weight. Your choice was overturned. The other side leads at 38, and the bar is 30. On your side there is 1 item. It is the summary lesson, and nobody has checked it yet. It counts as 1. On the other side there are 2 items. One passed a fresh test and counts as 3. One passed a check and counts as 2. Your choice counts as 0.",
}

KEY_NUMBERS = {
    "A": ["67", "43", "11", "33", "60", "10", "75", "78"],
    "B": ["38", "30", "1", "2", "3", "0"],
}

# fixed insertions (2a)
JARGON_INSERT = "The orthogonal heuristic parameter baseline leverages idempotent asynchronous serialization throughput."
OUT_OF_LIST_INSERT = "The quantifier harmonizes subsystem tolerances across heterogeneous cohorts."
LONG_CLAUSE_INSERT = ("It is also true that, when you look at the whole thing again after a good while has gone by, "
                      "and when you think about what each of us said to the other at the start, and about what "
                      "we both knew then and what we still do not know now, the answer is the same.")


def insert_after_first(text, extra):
    s = sentences(text)
    return " ".join([s[0], extra] + s[1:])


def shuffle_within_sentences(text, seed=7):
    rng = random.Random(seed)
    out = []
    for s in sentences(text):
        m = re.search(r"[.!?]+$", s)
        end = m.group(0) if m else ""
        body = s[: len(s) - len(end)]
        toks = body.split()
        rng.shuffle(toks)
        out.append(" ".join(toks) + end)
    return " ".join(out)


def gamed(text):
    """Break scenario: replace every non-common word with 'thing', drop numbers, 3-word sentences."""
    ws = [("thing" if (w not in COMMON) else w) for w in words(text)]
    ws = [w for w in ws if not w.isdigit()]
    chunks = [" ".join(ws[i:i + 3]).capitalize() + "." for i in range(0, len(ws), 3)]
    return " ".join(chunks)


# register diagnostic (NOT part of the score): formal full pairs vs contractions
FORMAL_PAIRS = re.compile(r"\b(it is|i am|you are|we are|they are|do not|does not|did not|is not|was not|that is|there is|what is)\b", re.I)
CONTRACTION = re.compile(r"\b\w+n't\b|\b(it|that|there|what|i|you|we|they)'(s|m|re|ve|ll|d)\b", re.I)


def register(text):
    return len(FORMAL_PAIRS.findall(text)), len(CONTRACTION.findall(text))


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(f"  [{'ok' if ok else 'FAIL'}] {name}: {detail}")


print("== (1) labeled pairs: tech must score harder than plainer ==")
for k, p in PAIRS.items():
    st, sp = score(p["tech"]), score(p["plainer"])
    pt, pp = parts(p["tech"]), parts(p["plainer"])
    print(f"  pair {k}: tech={st:.1f} (asl {pt['asl']:.1f}, unc {pt['unc_share']:.2f}, digsym {pt['digsym']}, jargon {pt['jargon']})"
          f"  plainer={sp:.1f} (asl {pp['asl']:.1f}, unc {pp['unc_share']:.2f}, digsym {pp['digsym']}, jargon {pp['jargon']})")
    check(f"pair {k} ranked right with margin>=10", st - sp >= 10, f"gap {st - sp:.1f}")

print("== (2a) adding jargon / long clauses to a plain reply must worsen it ==")
for k, p in PAIRS.items():
    base = score(p["plainer"])
    for label, ins in (("listed jargon", JARGON_INSERT), ("out-of-list hard words", OUT_OF_LIST_INSERT), ("long clause", LONG_CLAUSE_INSERT)):
        s = score(insert_after_first(p["plainer"], ins))
        check(f"{k} + {label}", s - base >= 3.0, f"{base:.1f} -> {s:.1f} (+{s - base:.1f})")

print("== (2b) splitting + jargon swap on a tech reply must improve it (numbers kept) ==")
for k, p in PAIRS.items():
    before, after = score(p["tech"]), score(TECH_REWRITE[k])
    kept = sum(1 for n in KEY_NUMBERS[k] if n in words(TECH_REWRITE[k]))
    lost_in_plainer = sum(1 for n in KEY_NUMBERS[k] if n not in words(p["plainer"]))
    check(f"{k} rewrite lowers score by >=10", before - after >= 10, f"{before:.1f} -> {after:.1f}")
    check(f"{k} rewrite kept every key number", kept == len(KEY_NUMBERS[k]), f"{kept}/{len(KEY_NUMBERS[k])} kept")
    print(f"      (the labeled plainer rewrite dropped {lost_in_plainer}/{len(KEY_NUMBERS[k])} of those numbers: plain by deletion)")

print("== (3) negative control: shuffling words inside each sentence ==")
for k, p in PAIRS.items():
    for which in ("tech", "plainer"):
        sh = shuffle_within_sentences(p[which])
        a, b = parts(p[which]), parts(sh)
        same = all(a[x] == b[x] for x in WORD_PARTS)
        check(f"{k}/{which} word-based parts unchanged", same and score(p[which]) == score(sh),
              f"score {score(p[which]):.4f} vs {score(sh):.4f}")

print("== break scenario: gamed text (hard words -> 'thing', 3-word sentences) ==")
for k, p in PAIRS.items():
    g = gamed(p["tech"])
    sg, sp = score(g), score(p["plainer"])
    check(f"{k} gamed text fools the scorer (<= plainer)", sg <= sp, f"gamed {sg:.1f} vs plainer {sp:.1f}; sample: {g[:60]}...")

print("== register diagnostic (outside the score): full forms vs contractions ==")
for k, p in PAIRS.items():
    ft, ct = register(p["tech"])
    fp, cp = register(p["plainer"])
    print(f"  pair {k}: tech full-forms {ft}, contractions {ct}; plainer full-forms {fp}, contractions {cp}")
    check(f"{k} plainer has more contractions than tech", cp > ct, f"{cp} vs {ct}")
    t_exp = re.sub(r"\bdoesn't\b", "does not", p["plainer"])
    t_exp = re.sub(r"\bdidn't\b", "did not", t_exp)
    fe, ce = register(t_exp)
    check(f"{k} expanding plainer contractions adds formal forms", fe > fp, f"full forms {fp}->{fe}, contractions {cp}->{ce}")

v1_checks = list(checks)
v1_ok = all(v1_checks)


def longest(text):
    return max(len(words(x)) for x in sentences(text))


def score2(text):
    return score(text) + 0.5 * longest(text)


print("== v2 (adds 0.5 * longest sentence; added after v1 failed) ==")
for k, p in PAIRS.items():
    st, sp = score2(p["tech"]), score2(p["plainer"])
    check(f"v2 pair {k} still ranked right with margin>=10", st - sp >= 10, f"{st:.1f} vs {sp:.1f}")
    base = score2(p["plainer"])
    for label, ins in (("listed jargon", JARGON_INSERT), ("out-of-list hard words", OUT_OF_LIST_INSERT), ("long clause", LONG_CLAUSE_INSERT)):
        s2 = score2(insert_after_first(p["plainer"], ins))
        check(f"v2 {k} + {label}", s2 - base >= 3.0, f"{base:.1f} -> {s2:.1f} (+{s2 - base:.1f})")
    check(f"v2 {k} rewrite lowers score by >=10", score2(p["tech"]) - score2(TECH_REWRITE[k]) >= 10,
          f"{score2(p['tech']):.1f} -> {score2(TECH_REWRITE[k]):.1f}")
    for which in ("tech", "plainer"):
        check(f"v2 {k}/{which} shuffle unchanged", score2(p[which]) == score2(shuffle_within_sentences(p[which])), "equal")
v2_checks = checks[len(v1_checks):]

ok = all(checks)
print(f"checks passed: {sum(checks)}/{len(checks)}")
print(f"RESULT: {'PASS' if ok else 'FAIL'} v1 {sum(v1_checks)}/{len(v1_checks)}, v2 {sum(v2_checks)}/{len(v2_checks)}; "
      f"pairs ranked right 2/2 (gaps A {score(PAIRS['A']['tech']) - score(PAIRS['A']['plainer']):.1f}, B {score(PAIRS['B']['tech']) - score(PAIRS['B']['plainer']):.1f}); "
      f"run-on of common words lowered v1 score (dilution)")
