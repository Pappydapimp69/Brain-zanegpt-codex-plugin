# Sandbox: does one hyphen-split rule fix BOTH the title matcher and two-pass lettering on stutter hooks?
# PREDICTION (written before first run): hyphen-kept matcher finds the title in 3/8 stutter hooks, split finds 8/8;
# hyphen-kept end-word judge mislabels (differs from last-segment judge) in at least 6 of 8 stanzas.
import re

HOOKS = [  # (line1, title, rhyme-partner line)
    ("uh-uh-undo it", "undo it", "i never knew it"),
    ("oh-oh-oh run to", "run to", "i will come through"),
    ("na-na-na-nothing", "nothing", "you gave me something"),
    ("hey-hey-heavy rain", "heavy rain", "feel the pain"),
    ("yeah-yeah-yesterday", "yesterday", "you went away"),
    ("la-la-lonely night", "lonely night", "hold me tight"),
    ("go-go-go go home", "go home", "feeling alone"),
    ("whoa-whoa-wild fire", "wild fire", "take me higher"),
]
VOW = "aeiouy"
def tok_keep(s): return re.findall(r"[a-z'-]+", s.lower())
def tok_split(s): return re.findall(r"[a-z']+", s.lower())
def title_keep(line, title): return all(t in tok_keep(line) for t in tok_keep(title)) and \
    ' '.join(tok_keep(title)) in ' '.join(tok_keep(line))
def title_split(line, title): return ' '.join(tok_split(title)) in ' '.join(tok_split(line))
def title_sub(line, title): return title in line

def rime(w, mode):
    w = w.split('-')[-1] if mode == 'last' else (w.split('-')[0] if mode == 'first' else w)
    m = re.search(r"[aeiouy]+[^aeiouy]*$", w)
    return m.group(0) if m else w
def vowel(w, mode):
    r = rime(w, mode); m = re.match(r"[aeiouy]+", r); return m.group(0) if m else r
def letters(ends, mode):
    """two-pass: perfect (full rime) first, then assonance (vowel) to resolved groups"""
    out = [None]*len(ends); nxt = 0; keys = {}
    for i, w in enumerate(ends):
        k = rime(w, mode)
        if k in keys: out[i] = keys[k]
        elif sum(1 for x in ends if rime(x, mode) == k) > 1:
            keys[k] = chr(65+nxt); nxt += 1; out[i] = keys[k]
    for i, w in enumerate(ends):
        if out[i] is None:
            for j, v in enumerate(ends):
                if out[j] and vowel(v, mode) == vowel(w, mode): out[i] = out[j].lower(); break
            else: out[i] = 'x'
    return ''.join(out)

def end(line): return line.split()[-1]
n = len(HOOKS)
k = sum(title_keep(h[0], h[1]) for h in HOOKS)
s = sum(title_split(h[0], h[1]) for h in HOOKS)
u = sum(title_sub(h[0], h[1]) for h in HOOKS)
print("scenario1 title matcher: keep=%d split=%d substring=%d of %d" % (k, s, u, n))

diff = 0; clean_diff = 0
for h in HOOKS:
    # stanza: hook line, partner, hook line variant, partner  -> intended ABAB-ish
    stanza = [h[0], h[2], h[0].replace('-', ' '), h[2]]
    e_hyph = [end(l) if '-' in end(l) else end(l) for l in stanza]
    e_hook = [h[0].split()[-1], end(h[2]), "undo", end(h[2])]
    a = letters([w for w in e_hook], 'whole'); b = letters(e_hook, 'last')
    if a != b: diff += 1
fdiff = sum(letters([h[0].split()[-1], end(h[2]), "undo", end(h[2])], 'first') != letters([h[0].split()[-1], end(h[2]), "undo", end(h[2])], 'last') for h in HOOKS)
print("scenario2b first-segment judge vs last-segment differs in %d of %d" % (fdiff, n))
print("scenario2 hyphenated end words: whole-token vs last-segment lettering differ in %d of %d" % (diff, n))

# scenario3 BREAK: plain (no hyphen) end words -> both judges must agree
plain = [["nothing","something","running","coming"],["rain","pain","gain","again"],["night","tight","light","fight"]]
agree = sum(letters(p,'whole') == letters(p,'last') for p in plain)
print("scenario3 BREAK plain end words agree: %d of %d" % (agree, len(plain)))

# scenario4: hook with mid-line hyphen only (end word plain): lettering unaffected, matcher still hurt
mid = [("uh-uh undo it","undo it")]
print("scenario4 mid-line hyphen only: keep=%s split=%s" % (title_keep(*mid[0]), title_split(*mid[0])))

ok = (k == 3 and s == n and diff >= 6 and agree == len(plain))
print("RESULT: %s title keep=%d/%d split=%d/%d, lettering differs %d/%d on hyphenated ends (first-vs-last judge %d/%d), plain ends agree %d/%d"
      % ("PASS" if ok else "FAIL", k, n, s, n, diff, n, fdiff, n, agree, len(plain)))
