# Sandbox: reduce (going to->gonna), hyphenate crowded lines, then two-pass letter 4-line stanzas.
# Prediction (written before run): with a whole-word judge, hyphenation changes 0/N letterings;
# reduction changes letterings only when it rewrites a LINE-END word (going to / to -> gonna),
# expected 1 of 4 scenarios broken (the end-reduction one), counted syllables drop only for going-to.
import re
VOW = re.compile(r'[aeiouy]+')
def syl(w):
    w = w.lower().replace('-', '')
    n = len(VOW.findall(w))
    if w.endswith('e') and not w.endswith(('le','ee')) and n > 1: n -= 1
    return max(n, 1)
def line_syl(l): return sum(syl(w) for w in l.split())
def reduce(l):  # reduce only before a bare verb
    return re.sub(r'\bgoing to (?=(?:go|be|run|stay|see|make|take|fly|find|try|say)\b)', 'gonna ', l)
def reduce_naive(l): return re.sub(r'\bgoing to\b', 'gonna', l)
def hyph(w):
    parts = re.findall(r'[^aeiouy]*[aeiouy]+(?:[^aeiouy]+$)?', w)
    return '-'.join(parts) if len(parts) > 1 and ''.join(parts) == w else w
def hyphenate_line(l): return ' '.join(hyph(w) for w in l.split())
RK = {'do':'oo','to':'oo','you':'oo','too':'oo','night':'ight','light':'ight','fly':'y','sky':'y','go':'o','know':'o','gonna':'onna','home':'ome','alone':'one','stone':'one','free':'ee','be':'ee'}
def key_whole(l): return RK.get(l.split()[-1].lower().replace('-',''), l.split()[-1])
def key_last(l):  return RK.get(l.split()[-1].split('-')[-1].lower(), l.split()[-1].split('-')[-1])
def letters(lines, kf):
    seen, out = {}, ''
    for l in lines:
        k = kf(l)
        if k not in seen: seen[k] = 'ABCD'[len(seen)]
        out += seen[k]
    return out
S = {
 'plain':      ['we will find the light','under the night','nothing to lose','I know I will see you','x'],
 'end_to':     ['the road is long and I am going to','I know the thing I have to do','the stars are out the sky is blue','I will find you and I am going to'],
 'mid_going':  ['I am going to be there tonight','holding the beautiful light','we are going to fly in the sky','when the morning is quiet and free'],
 'break_end':  ['tell them what I am going to','nothing is left to do','take me home','leave me alone'],
}
S['plain'] = ['we will find the light','nothing beats the night','hold me close and go','let me hear you know']
bad = {'hyph_whole':0,'hyph_last':0,'reduce_safe':0,'reduce_naive':0}; syl_drop = {'reduce_safe':0,'reduce_naive':0,'hyph':0}
for n, st in S.items():
    base = letters(st, key_whole)
    h = [hyphenate_line(l) for l in st]
    rs = [reduce(l) for l in st]; rn = [reduce_naive(l) for l in st]
    r = {'hyph_whole':letters(h,key_whole),'hyph_last':letters(h,key_last),'reduce_safe':letters(rs,key_whole),'reduce_naive':letters(rn,key_whole)}
    for k,v in r.items():
        if v != base: bad[k]+=1
    syl_drop['hyph'] += sum(line_syl(a)-line_syl(b) for a,b in zip(st,h))
    syl_drop['reduce_safe'] += sum(line_syl(a)-line_syl(b) for a,b in zip(st,rs))
    syl_drop['reduce_naive'] += sum(line_syl(a)-line_syl(b) for a,b in zip(st,rn))
    print(n, base, r)
print('changed lettering out of', len(S), bad); print('syllables saved', syl_drop)
ok = bad['hyph_whole']==0 and bad['reduce_safe']==0 and bad['reduce_naive']>=1 and syl_drop['hyph']<=0
print(('RESULT: PASS' if ok else 'RESULT: FAIL')+f" whole-word hyphenation 0/4 changed, safe reduction {bad['reduce_safe']}/4, naive end reduction {bad['reduce_naive']}/4, last-segment judge {bad['hyph_last']}/4, syllables saved by hyphen {syl_drop['hyph']}")
