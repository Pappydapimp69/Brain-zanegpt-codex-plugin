# Sandbox: reduce-gonna (guarded) + hyphenate-to-slow + two-pass rhyme letters, composed.
import itertools, re
LEX = {  # word: (hyphenated, perfect-key, vowel-key, syllables)
 "light":("light","ight","i",1),"night":("night","ight","i",1),
 "fire":("fi-re","ire","i",2),"higher":("hi-gher","ire","i",2),
 "stone":("stone","one","o",1),"alone":("a-lone","one","o",2),
 "road":("road","oad","o",1),"home":("home","ome","o",1),
 "sky":("sky","y","i",1),"cry":("cry","y","i",1),
 "rain":("rain","ain","a",1),"again":("a-gain","ain","a",2),
 "gold":("gold","old","o",1),"told":("told","old","o",1),
}
WORDS=list(LEX)
VERBS={"run","fly","stay","fight","fall"}
def reduce_naive(s): return s.replace("going to","gonna")
def reduce_guard(s):
    m=re.sub(r"going to (\w+)",lambda m: ("gonna "+m.group(1)) if m.group(1) in VERBS else m.group(0),s)
    return m
def syl(line):
    n=0
    for w in re.findall(r"[a-z-]+",line):
        w2=w.replace("-","")
        if w2=="gonna": n+=2
        elif w2=="going": n+=2
        elif w2 in LEX: n+=LEX[w2][3]
        elif w2 in("to","i","we","run","fly","stay","fight","fall","the","a","will","am","are"): n+=1
        else: n+=1
    return n
def hyph_end(line):
    w=line.split()[-1]; return line[:-len(w)]+LEX[w][0]
def judge_whole(line):  # rejoins hyphens, looks up whole word
    w=line.split()[-1].replace("-",""); return LEX[w][1],LEX[w][2]
def judge_last(line):   # last-segment spelling judge: key = last 2 letters of the final fragment only
    w=line.split()[-1].split("-")[-1]
    return w[-2:],"?"
def letters(lines,judge):
    keys=[judge(l) for l in lines]; out=[None]*4; nxt=0; abc="abcd"
    for i in range(4):          # pass 1 perfect
        if out[i] is None:
            out[i]=abc[nxt]; nxt+=1
            for j in range(i+1,4):
                if out[j] is None and keys[j][0]==keys[i][0]: out[j]=out[i]
    for i in range(4):          # pass 2 assonance hint to earlier different group
        pass
    return "".join(out)
BASE=["we are going to run {}","I am going to fly {}","we will stay {}","I am going to the {}"]
order_diff=0; tot=0; letters_same=0; last_bad=0; naive_bad=0; guard_bad=0; saved=0; hy_saved=0; reducible=0; plain_vs=0
for ends in itertools.product(WORDS,repeat=4):
    plain=[b.format(e) for b,e in zip(BASE,ends)]
    red=[reduce_guard(l) for l in plain]
    redh=[hyph_end(l) for l in red]
    tot+=1
    if [hyph_end(l) for l in red]!=[reduce_guard(hyph_end(l)) for l in plain]: order_diff+=1
    if letters(plain,judge_whole)==letters(redh,judge_whole): letters_same+=1
    if letters(plain,judge_whole)!=letters(redh,judge_last): last_bad+=1
    naive_bad+= sum(1 for l in plain if "to the" in l and reduce_naive(l)!=l)
    guard_bad+= sum(1 for l in plain if "to the" in l and reduce_guard(l)!=l)
    for p,r,h in zip(plain,red,redh):
        if r!=p: reducible+=1; saved+=syl(p)-syl(r)
        hy_saved+=syl(r)-syl(h) if False else 0
print(f"stanzas={tot} letters_same_whole_judge={letters_same} last_segment_judge_mislettered={last_bad}")
print(f"naive rewrites of 'going to the X': {naive_bad}, guarded: {guard_bad}")
print(f"reducible lines={reducible}, syllables saved per reduced line={saved/reducible:.2f}")
ok = order_diff==0 and letters_same==tot and guard_bad==0 and naive_bad>0 and last_bad>0 and abs(saved/reducible-1)<1e-9
print(("RESULT: PASS" if ok else "RESULT: FAIL")+f" whole-word judge kept {letters_same}/{tot}; last-segment judge broke {last_bad}/{tot}; guard 0 vs naive {naive_bad} bad rewrites; 1 syllable saved per reduced line; order-swapped differs in {order_diff}")
