"""Rebuild of: a spelling-suffix rhyme judge corrupts stanza LETTERING far more
often than it changes the open/resolved VERDICT.

PREDICTION (written before first run):
  Of 8 trap stanzas (4-6 lines, own end-words), the suffix-3 spelling judge
  letters >= 6 differently from a phonetic ground truth, but flips the
  'last line resolves onto an earlier rhyme' verdict in <= 3.
  Clean controls (spelling matches sound) differ in 0.
  A stanza built to force a verdict flip must flip (harness is not blind).
Pass iff all four hold. (Thresholds fixed before run 1; run 1 had a control-fixture bug,
  2-letter endings cannot match at k=3, fixed by rewriting controls only.) Lettering = canonical first-appearance letters.
"""
# phonetic rhyme key by hand (vowel+coda sound, ASCII respelling)
SOUND = {
 'love':'uv','dove':'uv','glove':'uv','above':'uv','shove':'uv',
 'move':'oov','prove':'oov','groove':'oov','approve':'oov',
 'cough':'off','trough':'off','though':'oh','dough':'oh','row':'oh','slow':'oh',
 'bough':'ow','plough':'ow','now':'ow','cow':'ow','rough':'uff','tough':'uff','enough':'uff','stuff':'uff',
 'blue':'oo','through':'oo','view':'oo','new':'oo','true':'oo','shoe':'oo',
 'said':'ed','bed':'ed','head':'ed','red':'ed','made':'ade','shade':'ade','fade':'ade',
 'great':'ate','straight':'ate','late':'ate','fate':'ate','wait':'ate','eight':'ate',
 'wind':'ind1','thinned':'ind1','pinned':'ind1','mind':'ined','find':'ined','kind':'ined','blind':'ined',
 'bear':'air','there':'air','air':'air','fair':'air','hear':'eer','near':'eer','tear':'eer','here':'eer',
 'word':'urd','heard':'urd','bird':'urd','lord':'ord','ward':'ord','sword':'ord',
 'water':'otter','otter':'otter','daughter':'otter','potter':'otter','matter':'atter','latter':'atter',
 'bone':'ohn','stone':'ohn','done':'un','one':'un','son':'un','gone':'on','none':'un',
 'tune':'oon','moon':'oon','soon':'oon','spoon':'oon',
 'break':'ake','take':'ake','lake':'ake','steak':'ake','speak':'eek','week':'eek','weak':'eek','cheek':'eek',
 'sea':'ee','key':'ee','me':'ee','tree':'ee','be':'ee',
 'day':'ay','say':'ay','grey':'ay','way':'ay','they':'ay',
 'sun':'un','fun':'un','run':'un','lone':'ohn',
 'lead':'eed','read':'eed','need':'eed','bead':'eed','lead_m':'ed',
 'bomb':'om','tomb':'oom','comb':'ohm','home':'ohm','foam':'ohm','dome':'ohm',
}
def spell_rhyme(a,b,k):
    n=0
    while n<min(len(a),len(b)) and a[-1-n]==b[-1-n]: n+=1
    return n>=k
def sound_rhyme(a,b): return SOUND[a]==SOUND[b]

def letter(words, rel):
    reps=[]; out=[]
    for w in words:
        for i,r in enumerate(reps):
            if rel(r,w): out.append(i); break
        else:
            reps.append(w); out.append(len(reps)-1)
    return ''.join('ABCDEFGHIJ'[i] for i in out)
def resolves(lt): return lt[-1] in lt[:-1]

TRAPS = {
 't1_love_move':   'love prove dove move'.split(),            # eye rhymes only
 't2_ough_zoo':    'cough though bough rough'.split(),         # ough soup, all different
 't3_missed_oo':   'blue day through say'.split(),             # missed true rhyme
 't4_ate_spread':  'great day straight say late'.split(),      # ate spelled 3 ways
 't5_ind':         'wind mind thinned find'.split(),           # wind/thinned vs mind/find
 't6_ter':         'water daughter matter latter'.split(),     # water~daughter true, matter~latter true
 't7_mixed6':      'bear hear there near air fair'.split(),    # ear splits air/eer
 't8_one_done':    'done bone one stone son gone'.split(),     # one/done/son vs bone/stone
}
CONTROLS = {   # spelling-consistent AND phonetically consistent (>=3-letter shared endings)
 'c1_abab_clean':  'lake moon take soon'.split(),
 'c2_aabb_clean':  'made shade moon soon'.split(),
 'c3_abba_clean':  'lake moon soon take'.split(),
}
# built to force a verdict flip: last line only eye-rhymes with an earlier one
FORCE = {'f1_final_eye': 'sun wind love mind'.split(),   # truth: wind/mind? no -> check
         'f2_final_eye': 'bone sea move key done'.split()}
# f2: truth done~? bone,done diff; last 'done' stray? spelling merges done/bone (one: 'one' suffix 3 'one')

def run(group,k):
    rows=[]
    for name,ws in group.items():
        t=letter(ws,sound_rhyme); s=letter(ws,lambda a,b:spell_rhyme(a,b,k))
        rows.append((name,t,s,t!=s,resolves(t)!=resolves(s)))
    return rows

if __name__=='__main__':
    res={}
    for k in (3,2):
        tr=run(TRAPS,k); co=run(CONTROLS,k); fo=run(FORCE,k)
        res[k]=(tr,co,fo)
        print(f'--- suffix k={k}')
        for grp,rows in (('trap',tr),('control',co),('force',fo)):
            for n,t,s,d,f in rows: print(f'{grp:7} {n:15} truth={t:7} spell={s:7} differ={int(d)} verdict_flip={int(f)}')
    tr,co,fo=res[3]
    nd=sum(r[3] for r in tr); nf=sum(r[4] for r in tr)
    cd=sum(r[3] for r in co); ff=sum(r[4] for r in fo)
    tr2=res[2][0]; nd2=sum(r[3] for r in tr2); nf2=sum(r[4] for r in tr2)
    print(f'k3: traps differ {nd}/8 flip {nf}/8; controls differ {cd}/3; forced flips {ff}/2')
    print(f'k2 sensitivity: traps differ {nd2}/8 flip {nf2}/8')
    ok = nd>=6 and nf<=3 and cd==0 and ff>=1
    print(f"RESULT: {'PASS' if ok else 'FAIL'} letters differ {nd}/8 vs verdict flips {nf}/8 (k=3); controls differ {cd}/3; forced flips {ff}/2; k=2 {nd2}/{nf2}")
