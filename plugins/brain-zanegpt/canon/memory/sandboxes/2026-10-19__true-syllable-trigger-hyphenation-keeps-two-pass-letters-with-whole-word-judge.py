"""Sandbox: true-syllable hyphenate trigger + two-pass lettering (stdlib, deterministic)."""
import random, re
random.seed(7)
# word -> (true syllables, rhyme tail key, vowel-class key)
W = {
 'night':(1,'ight','i'),'light':(1,'ight','i'),'fight':(1,'ight','i'),'sight':(1,'ight','i'),
 'rain':(1,'ain','a'),'pain':(1,'ain','a'),'train':(1,'ain','a'),'chain':(1,'ain','a'),
 'fire':(2,'ire','i'),'desire':(3,'ire','i'),'higher':(2,'igher','i'),'wire':(2,'ire','i'),
 'quiet':(3,'iet','i'),'diet':(3,'iet','i'),'poem':(2,'oem','o'),'piano':(3,'ano','o'),
 'heart':(1,'art','a'),'apart':(2,'art','a'),'start':(1,'art','a'),'part':(1,'art','a'),
 'alone':(2,'one','o'),'stone':(1,'one','o'),'home':(1,'ome','o'),'bone':(1,'one','o'),
}
FILL=['the','and','i','will','keep','on','running','through','every','single','beautiful','memory','of','you','we','sing','a','song','tonight','forever']
FSYL={'beautiful':3,'memory':3,'every':2,'single':2,'running':2,'forever':3,'tonight':2,'will':1}
def tsyl(w): return W[w][0] if w in W else FSYL.get(w,1)
def vg(w):  # vowel-group counter
    w=w.lower(); return max(1,len(re.findall(r'[aeiouy]+',w)) - (1 if w.endswith('e') and len(w)>2 and not w.endswith('le') else 0))
def line_true(ws): return sum(tsyl(w) for w in ws)
def line_vg(ws): return sum(vg(w) for w in ws)
BUDGET=9; SLACK=3
def hyph(w):  # break at vowel groups
    parts=re.findall(r'[^aeiouy]*[aeiouy]+(?:[^aeiouy]+$)?',w)
    return '-'.join(parts) if len(parts)>1 else w
def mk_line(endw,n):
    return [random.choice(FILL) for _ in range(n)]+[endw]
ends=list(W)
def stanza():
    a,b=random.sample(['night','rain','heart','stone'],2)
    pool=lambda k:[w for w in ends if W[w][1]==W[k][1]]
    es=[random.choice(pool(a)),random.choice(pool(b)),random.choice(pool(a)),random.choice(pool(b))]
    return [mk_line(e,random.choice([2,4,6,8,9])) for e in es]
def letters(st,judge):
    # pass1: perfect groups (same tail) uppercase; pass2: same vowel class lowercase
    keys=[judge(l[-1]) for l in st]; out=[];seen={}
    for i,k in enumerate(keys):
        out.append(k)
    tails={};res=[]
    for k in keys: tails.setdefault(k,len(tails))
    return tuple(tails[k] for k in keys)
def whole(w): return W[w.replace('-','')][1]
def lastseg(w): return w.split('-')[-1]
def hyph_line(ws,all_end=True): return ws[:-1]+[hyph(ws[-1])]
N=2000; res=dict(crowded=0,true_flag=0,vg_flag=0,whole_ok=0,last_ok=0,hy_lines=0,last_hyp_end=0,raised=0)
for _ in range(N):
    st=stanza(); base=letters(st,whole)
    new=[]
    for l in st:
        t=line_true(l); v=line_vg(l)
        crowded=t>BUDGET
        if crowded: res['crowded']+=1
        if t>BUDGET: res['true_flag']+=1
        if v>BUDGET+SLACK: res['vg_flag']+=1
        if t>BUDGET:
            res['hy_lines']+=1
            nl=hyph_line(l)
            if nl[-1]!=l[-1]: res['last_hyp_end']+=1
            if line_vg(nl)>v: res['raised']+=1
            new.append(nl)
        else: new.append(l)
    # judge sees hyphenated end words
    if letters(new,whole)==base: res['whole_ok']+=1
    if letters(new,lambda w:lastseg(w) if '-' in w else W[w][1])==base: res['last_ok']+=1
print(res)
tf=res['true_flag']/max(1,res['crowded']); vf=res['vg_flag']/max(1,res['crowded'])
print(f"true-trigger recall {tf:.2f}, vowel-slack recall {vf:.2f}, whole-word letters kept {res['whole_ok']}/{N}, last-segment kept {res['last_ok']}/{N}")
ok = tf==1.0 and vf<1.0 and res['whole_ok']==N and res['last_ok']<N
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" true-recall {tf:.2f} vs vg-slack {vf:.2f}; whole-word {res['whole_ok']}/{N}; last-seg {res['last_ok']}/{N}; hyphenated-ends {res['last_hyp_end']}")
