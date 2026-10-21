# Sandbox: does the vowel-group syllable warning (budget 9, slack 3) interact with two-pass lettering of the same stanza?
# PREDICTION (before run): (a) on 13-15 true-syllable lines the counter misses >=30% because hiatus/diphthong words
# (poem, quiet, idea, ocean, being, real) undercount; (b) the two-pass letters of the stanza are identical whether or
# not the line was flagged (0 differences, they read different properties); (c) BREAK: if end words are the undercounted
# ones, the flag miss rate rises above the overall miss rate (>=10 points higher).
import re, random, itertools
BUDGET, SLACK = 9, 3
UNDER = {"poem":2,"quiet":2,"idea":3,"ocean":2,"being":2,"real":1,"science":2,"giant":2}  # true count; counter undercounts
OVER = {"every":2,"fire":1,"hour":1}  # counter reads groups: every->e,e,y? see below
PLAIN = {"and":1,"the":1,"we":1,"go":1,"in":1,"to":1,"my":1,"so":1,"run":1,"tonight":2,"river":2,"over":2,"never":2,"again":2,"alone":2}
TRUE = {**UNDER, **OVER, **PLAIN}
def counter(w): return max(1, len(re.findall(r"[aeiouy]+", w)))
rng = random.Random(5)
def make(n_true, ends_from):
    words, t = [], 0
    pool_mid = list(PLAIN) + list(UNDER)
    while True:
        end = rng.choice(ends_from)
        body, t = [], TRUE[end]
        while t < n_true:
            w = rng.choice(pool_mid)
            if t + TRUE[w] <= n_true: body.append(w); t += TRUE[w]
            elif t < n_true: body.append("go"); t += 1
        return body + [end]
def stat(ends_from, T=3000):
    miss = tot = 0
    for _ in range(T):
        n = rng.choice([13, 14, 15]); L = make(n, ends_from)
        true = sum(TRUE[w] for w in L); cnt = sum(counter(w) for w in L)
        if true > BUDGET + SLACK:
            tot += 1; miss += cnt <= BUDGET + SLACK
    return miss, tot
all_ends = list(PLAIN) + list(UNDER)
m1, t1 = stat(all_ends); m2, t2 = stat(list(UNDER))
r1, r2 = m1/t1, m2/t2
print("scenario1 miss rate on true 13-15 lines, any end word: %d/%d = %.1f%%" % (m1, t1, 100*r1))
print("scenario3 BREAK end word undercounted: %d/%d = %.1f%%" % (m2, t2, 100*r2))
def rime(w):
    g = re.search(r"[aeiouy]+[^aeiouy]*$", w); return g.group(0) if g else w
def letters(ends, flags=None):
    keys, out = {}, []
    for e in ends:
        k = rime(e); keys.setdefault(k, chr(65+len(keys))); out.append(keys[k])
    return ''.join(out)
diff = n = 0
for st in itertools.product(["river","over","never","again","alone","poem","ocean","quiet"], repeat=4):
    n += 1
    flagged = [counter(w) > 3 for w in st]  # arbitrary flag derived from counter
    diff += letters(st) != letters(st, flagged)
print("scenario2 letters with vs without warning flags: %d of %d differ" % (diff, n))
ok = r1 >= 0.3 and diff == 0 and r2 - r1 >= 0.10
print("RESULT: %s miss any-end %.1f%%, undercounted-end %.1f%%, letters differ %d/%d" % ("PASS" if ok else "FAIL", 100*r1, 100*r2, diff, n))
