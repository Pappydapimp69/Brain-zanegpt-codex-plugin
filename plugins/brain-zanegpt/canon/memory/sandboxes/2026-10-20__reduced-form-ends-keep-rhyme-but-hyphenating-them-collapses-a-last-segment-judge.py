# Sandbox: reduced-form end words (gonna) + hyphenate-to-slow (gon-na) + two-pass lettering.
# PREDICTION (written before first run): reduced ends give AABB under any judge; expanded ends (going to) lose the
# rhyme (3+ lines end in 'to' -> repeated-word group, not AABB); hyphenated reduced ends read AABB under a whole-token
# judge but collapse to AAAA under a last-segment judge ('na' for all four).
import re

def seg(w, mode):
    p = w.lower().split('-')
    return p[-1] if mode == 'last' else (p[0] if mode == 'first' else ''.join(p))

def rime(w, mode):
    w = seg(w, mode)
    m = re.search(r"[aeiou]+[^aeiou]*[aeiou]?$", w)  # last vowel group + coda (+ final vowel)
    m2 = re.search(r"[aeiou]+[^aeiou]+[aeiou]$", w)  # 2-syllable ending like onna
    return (m2 or m).group(0) if (m2 or m) else w

def vowel(w, mode):
    r = rime(w, mode); m = re.match(r"[aeiou]+", r); return m.group(0)

def letters(ends, mode):
    out = [None]*len(ends); nxt = 0; keys = {}
    for i, w in enumerate(ends):
        k = rime(w, mode)
        if k in keys: out[i] = keys[k]
        elif sum(rime(x, mode) == k for x in ends) > 1:
            keys[k] = chr(65+nxt); nxt += 1; out[i] = keys[k]
    for i, w in enumerate(ends):
        if out[i] is None:
            for j, v in enumerate(ends):
                if out[j] and out[j].isupper() and vowel(v, mode) == vowel(w, mode):
                    out[i] = out[j].lower(); break
            else: out[i] = 'x'
    return ''.join(out)

S1 = ["gonna", "Donna", "wanna", "Anna"]            # reduced
S2 = ["to", "Donna", "to", "Anna"]                  # expanded: going to / want to
S3 = ["gon-na", "Don-na", "wan-na", "An-na"]        # hyphenated reduced
S4 = ["gonna", "Donna", "wanna", "Anna"]            # BREAK: hyphen only inside the line, ends plain
res = {}
for name, st in (("reduced", S1), ("expanded", S2), ("hyphenated", S3), ("interior-hyphen", S4)):
    res[name] = {m: letters(st, m) for m in ("whole", "last", "first")}
    print("%-16s whole=%s last=%s first=%s" % (name, res[name]['whole'], res[name]['last'], res[name]['first']))
ok = (res['reduced']['whole'] == res['reduced']['last'] == 'AABB'
      and res['expanded']['whole'] != 'AABB'
      and res['hyphenated']['whole'] == 'AABB' and res['hyphenated']['last'] == 'AAAA'
      and res['interior-hyphen']['last'] == 'AABB')
print("RESULT: %s reduced AABB all judges=%s; expanded=%s; hyphenated whole=%s last=%s first=%s; interior hyphen last=%s"
      % ("PASS" if ok else "FAIL", res['reduced']['first'] == 'AABB', res['expanded']['whole'],
         res['hyphenated']['whole'], res['hyphenated']['last'], res['hyphenated']['first'], res['interior-hyphen']['last']))
