# Sandbox: lettering (whole-word judge) + syllable warning (vowel-group counter, budget 9, slack 3) on hyphenated end words.
# PREDICTION (before run): (a) hyphenating the end word of a line leaves the vowel-group count unchanged in 100% of
# lines without a hiatus word; (b) with budget 9 + slack 3 the warning stays silent on lines of 12 true syllables
# (counter reads <=9), so a hyphenate-to-slow hint keyed off the warning fires 0 times even after the writer hyphenates;
# (iteration 3: rime rule now reads a final vowel after the coda, so gonna/Donna keep 'onna')
# (c) whole-word lettering of hyphenated vs plain stanzas is identical in 100%; last-segment judge differs in >=20%.
import re, itertools, random
BUDGET, SLACK = 9, 3
# (word, true syllables, hyphenated form); chosen so hyphen pieces keep vowel groups
LEX = [("remember",3,"re-mem-ber"),("tomorrow",3,"to-mor-row"),("forever",3,"for-ev-er"),("wonderful",3,"won-der-ful"),
       ("everything",3,"ev-ery-thing"),("diamond",2,"di-a-mond"),("silence",2,"si-lence"),("river",2,"riv-er"),
       ("burning",2,"burn-ing"),("falling",2,"fall-ing"),("fire",1,"fi-re"),("higher",2,"hi-gher"),("Donna",2,"Don-na"),("gonna",2,"gon-na"),("wanna",2,"wan-na"),("Anna",2,"An-na")]
LEXD = {w: (n, h) for w, n, h in LEX}
def count(word):  # vowel-group counter, silent trailing e not handled except via pattern
    return max(1, len(re.findall(r"[aeiouy]+", word)))
def line_count(words): return sum(count(w) for w in words)
def true_count(words): return sum(LEXD[w][0] if w in LEXD else 1 for w in words)
FILL = ["and","the","we","go","in","a","to","my","on","so"]
rng = random.Random(77)
def make_line(n_true):
    words = []; t = 0
    while t < n_true - 3:
        words.append(rng.choice(FILL)); t += 1
    ends = [w for w, n, h in LEX if n == 3 and w != "everything"]
    e = rng.choice(ends); words.append(e); t += 3
    return words
def hyph(words): return words[:-1] + [LEXD[words[-1]][1]]
same = warn_plain = warn_hyph = tot = 0
for _ in range(200):
    L = make_line(12); H = hyph(L); tot += 1
    cp, ch = line_count(L), line_count(H)
    same += cp == ch
    warn_plain += cp > BUDGET + SLACK; warn_hyph += ch > BUDGET + SLACK
print("scenario1 count unchanged by end hyphen: %d/%d; warnings plain=%d hyphenated=%d (true=12)" % (same, tot, warn_plain, warn_hyph))
# lettering: stanzas over rhyming end words
def seg(w, m): return w.split('-')[-1] if m == 'last' else w.replace('-', '')
def rime(w, m):
    w = seg(w, m); g = re.search(r"[aeiouy]+[^aeiouy]+[aeiouy]$", w) or re.search(r"[aeiouy]+[^aeiouy]*$", w)
    return g.group(0) if g else w
def letters(ends, m):
    out = []; keys = {}
    for e in ends:
        k = rime(e, m)
        if k not in keys: keys[k] = chr(65 + len(keys))
        out.append(keys[k])
    return ''.join(out)
pool = [w for w in LEXD]
diff_whole = diff_last = n = 0
for st in itertools.islice(itertools.product(pool, repeat=4), 0, 20736, 7):
    n += 1
    plain = list(st); hy = [LEXD[w][1] for w in st]
    diff_whole += letters(plain, 'whole') != letters(hy, 'whole')
    diff_last += letters(plain, 'whole') != letters(hy, 'last')
print("scenario2 lettering vs plain over %d stanzas: whole-word judge differs %d, last-segment differs %d (%.1f%%)" % (n, diff_whole, diff_last, 100*diff_last/n))
# BREAK: hyphenate a hiatus word (di-a-mond: 'ia' one group plain, two groups hyphenated)
d = count("diamond"), count("di-a-mond")
print("scenario3 BREAK hiatus word: plain=%d hyphenated=%d true=2" % d)
ok = same == tot and warn_plain == 0 and warn_hyph == 0 and diff_whole == 0 and diff_last / n >= 0.2 and d[0] != d[1]
print("RESULT: %s counts unchanged %d/%d, warnings 0 -> 0 on 12-syllable lines, whole-word lettering diff %d, last-segment diff %.1f%%, hiatus word %d->%d"
      % ("PASS" if ok else "FAIL", same, tot, diff_whole, 100*diff_last/n, d[0], d[1]))
