# Own fixture: words as (vowel, coda) pairs from a different lexicon than the claim's.
# Prediction (before run): closure distance (gap to most recent same-group line, vowel-only grouping)
# is equal for perfect-rhyme AABB and assonance-only AABB (2 pairs, mean 1.0); two-pass letters differ
# (AABB vs aabb); ABBA gives gaps 1 and 3; a break stanza where vowels match but intended pairs share
# no coda family gives the same distance too (so distance cannot see rhyme quality at all).
LEX = {"moon":("u","n"),"tune":("u","n"),"cool":("u","l"),"pool":("u","l"),"boot":("u","t"),
       "stone":("o","n"),"bone":("o","n"),"road":("o","d"),"toad":("o","d"),"gold":("o","ld"),
       "tune2":("u","m"),"loom":("u","m"),"hope":("o","p"),"rope":("o","p"),"soak":("o","k")}
def last(line): return line.split()[-1]
def groups(stanza, perfect):
    key = (lambda w: LEX[w]) if perfect else (lambda w: LEX[w][0])
    return [key(last(l)) for l in stanza]
def closure(stanza):
    g = groups(stanza, False); gaps=[]
    for i,x in enumerate(g):
        for j in range(i-1,-1,-1):
            if g[j]==x: gaps.append(i-j); break
    return len(gaps), (sum(gaps)/len(gaps) if gaps else 0.0), gaps
def two_pass(stanza):
    v = groups(stanza, False); p = groups(stanza, True)
    letters={}; out=[]
    for i,x in enumerate(v):
        if x not in letters: letters[x]=chr(65+len(letters))
        L=letters[x]
        partner = sum(1 for k in range(len(p)) if k!=i and p[k]==p[i])>0
        out.append(L if partner else L.lower())
    return "".join(out)
S = {
 "perfect AABB":   ["a moon","b tune","c stone","d bone"],
 "assonance AABB": ["a moon","b cool","c stone","d road"],
 "perfect ABBA":   ["a moon","b stone","c bone","d tune"],
 "assonance ABBA": ["a moon","b stone","c road","d cool"],
}
R={}
for k,s in S.items():
    R[k]=(closure(s), two_pass(s)); print(k, R[k])
ok = (R["perfect AABB"][0][:2]==R["assonance AABB"][0][:2]==(2,1.0)
      and R["perfect AABB"][1]=="AABB" and R["assonance AABB"][1]=="aabb"
      and sorted(R["perfect ABBA"][0][2])==[1,3] and R["perfect ABBA"][0][2]==R["assonance ABBA"][0][2])
print("RESULT: %s distance equal for perfect/assonance AABB %s; letters %s vs %s; ABBA gaps %s" % (
 "PASS" if ok else "FAIL", R["perfect AABB"][0][:2], R["perfect AABB"][1], R["assonance AABB"][1], R["perfect ABBA"][0][2]))
