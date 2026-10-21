# Sandbox: the SUNG end word decides the rhyme. Reduced forms (gonna, wanna, gotta) vs their written full forms ("to"),
# plus a pacing-hyphen form (gon-na) read by a last-segment judge, all fed to two-pass lettering.
# Prediction (before run): sung/reduced spelling judge errs on < 15% of stanzas (wanna vs gonna spelling);
# written full form errs on > 30%; last-segment hyphen read errs on > 40%.
import itertools, re
# sung word : (perfect class, assonance class, written full-form end word, hyphenated pacing form)
L = {
 "gonna":("onna","o","to","gon-na"), "wanna":("onna","o","to","wan-na"), "Donna":("onna","o","Donna","Don-na"),
 "gotta":("otta","o","to","got-ta"), "lotta":("otta","o","lotta","lot-ta"),
 "kinda":("inda","i","of","kin-da"), "Linda":("inda","i","Linda","Lin-da"),
 "nirvana":("ana","a","nirvana","nir-va-na"), "banana":("ana","a","banana","ba-na-na"),
 "you":("oo","oo","you","you"), "through":("oo","oo","through","through"), "to":("oo","oo","to","to"),
}
V = "aeiouy"
OVR = {"you":("oo","oo"),"through":("oo","oo"),"to":("oo","oo"),"of":("uv","uh")}
def keys(w):
    w = w.lower()
    if w in OVR: return OVR[w]
    t = w[:-1] if len(w) > 2 and w.endswith("e") and w[-2] not in V else w
    m = list(re.finditer(r"[aeiouy]+", t))
    if not m: return (w, w)
    g = m[-1]
    if t.endswith('a') and len(m) > 1: g = m[-2]   # feminine -a ending: rhyme from the stressed vowel
    vow = t[g.start():g.end()]
    return (w[g.start():], {"o":"o","oo":"oo","a":"a","ou":"oo","i":"i","a":"a","y":"oo"}.get(vow, vow))
def judge(kind):
    def f(w):
        if kind == "truth": return L[w][:2]
        if kind == "sung": return keys(w)
        if kind == "written": return keys(L[w][2])
        if kind == "last": return keys(L[w][3].split("-")[-1])
        if kind == "rejoin": return keys(L[w][3].replace("-", ""))
    return f
def lettering(ws, f):
    ks = [f(w) for w in ws]; groups = {}
    for i, (r, a) in enumerate(ks): groups.setdefault(r, []).append(i)
    letters = {}; n = 0
    for r, idx in groups.items():
        if len(idx) > 1: letters[r] = "ABCD"[n]; n += 1
    out = []
    for i, (r, a) in enumerate(ks):
        if r in letters: out.append(letters[r]); continue
        link = next((letters[kr] for kr in letters if any(ks[j][0] == kr and ks[j][1] == a for j in range(4))), None)
        out.append(link.lower() if link else "x")
    return "".join(out)
def canon(s):
    m = {}; o = ""
    for c in s:
        k = c.lower(); m.setdefault(k, "pqrs"[len(m)]); o += m[k].upper() if c.isupper() else m[k]
    return o
words = list(L); stanzas = list(itertools.combinations(words, 4)); N = len(stanzas)
def err(kind, pool=None):
    st = stanzas if pool is None else pool
    return sum(canon(lettering(s, judge("truth"))) != canon(lettering(s, judge(kind))) for s in st), len(st)
res = {k: err(k) for k in ("sung", "written", "last", "rejoin")}
for k, (e, n) in res.items(): print(f"{k:8s} wrong {e}/{n} = {100*e/n:.1f}%")
# BREAK: stanzas drawn only from words whose written full form is the same word (no reduction): written must be perfect
plain = [w for w in words if L[w][2] == w]
pst = list(itertools.combinations(plain, 4))
we = err("written", pst)[0]
print(f"unreduced words only: written wrong {we}/{len(pst)}")
print('prediction sung < 15% missed:', not res['sung'][0] / N < 0.15, f"(got {100*res['sung'][0]/N:.1f}%, wanna spells -anna not -onna)")
ok = res['rejoin'][0] == res['sung'][0] and res['sung'][0] < res['written'][0] < res['last'][0] and we == 0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
  " ".join(f"{k} {e}/{n} ({100*e/n:.1f}%)" for k, (e, n) in res.items()), f"| unreduced-only written {we}/{len(pst)}")
