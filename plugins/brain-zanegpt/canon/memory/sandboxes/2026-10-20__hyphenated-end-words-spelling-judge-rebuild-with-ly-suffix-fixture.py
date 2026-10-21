import itertools
# own fixture: 12 end words (plain, hyphenated, truth rhyme key); judge = last 3 letters of the token
W=[("slowly","slow-ly","EE"),("madly","mad-ly","EE"),("quickly","quick-ly","EE"),("gladly","glad-ly","EE"),
   ("happy","hap-py","EE"),("puppy","pup-py","EE"),("rely","re-ly","AY"),("reply","re-ply","AY"),
   ("apply","ap-ply","AY"),("supply","sup-ply","AY"),("deny","de-ny","AY"),("defy","de-fy","AY")]
def part(keys):
    g={}
    for i,k in enumerate(keys): g.setdefault(k,[]).append(i)
    return frozenset(tuple(v) for v in g.values())
broke=repaired=wrong_p=wrong_h=changed=n=0
for st in itertools.product(range(12),repeat=4):
    n+=1
    t=part([W[i][2] for i in st])
    p=part([W[i][0][-3:] for i in st]); h=part([W[i][1][-3:] for i in st])
    wp=p!=t; wh=h!=t
    wrong_p+=wp; wrong_h+=wh; changed+=(p!=h)
    broke+=(not wp and wh); repaired+=(wp and not wh)
print(f"stanzas={n} wrong_plain={wrong_p/n:.1%} wrong_hyph={wrong_h/n:.1%} partition_changed={changed/n:.1%} broke={broke} repaired={repaired}")
ok = changed/n>=0.05 and broke>repaired and repaired==0
print(("RESULT: PASS" if ok else "RESULT: FAIL"),f"wrong {wrong_p/n:.1%} -> {wrong_h/n:.1%}, partition changed {changed/n:.1%}, broke {broke}, repaired {repaired} (claim: repaired none)")
