# Deterministic blast-radius model. No RNG, no timing: attacker effort is counted in hash-work units.
import hashlib
# resources and which credential grants each
RES=["web","db_read","db_write","billing","ci","prod_deploy","backups","logs"]
# SHARED: one admin token opens everything. SCOPED: one token per resource, plus CI token reaches prod_deploy (pipeline edge).
SHARED={"admin":set(RES)}
SCOPED={f"tok_{r}":{r} for r in RES}
EDGES={"tok_ci":{"prod_deploy"}}   # CI can trigger a deploy: reachability edge, not a direct grant
def reach(creds,leaked,edges=None):
    out=set()
    for c in leaked: out|=creds.get(c,set())
    if edges:
        for c in leaked: out|=edges.get(c,set())
    return out
r_shared=len(reach(SHARED,["admin"]))
r_scoped=len(reach(SCOPED,["tok_web"]))
r_ci=len(reach(SCOPED,["tok_ci"],EDGES))
r_ci_naive=len(reach(SCOPED,["tok_ci"]))
print("blast radius shared/scoped(web)/scoped(ci with edge)/ci naive:",r_shared,r_scoped,r_ci,r_ci_naive)
# secret leaked into repo history; force-push does not remove clones. exposure = leaked_until_rotation
def exposure(rotated,forcepushed,clones):
    # attacker holds a copy iff a clone exists, regardless of force-push; rotation voids it
    return 0 if rotated else (1 if clones>0 else 0)
e_force=exposure(False,True,1); e_rot=exposure(True,False,1); e_none=exposure(False,False,0)
print("still usable: forcepush-only",e_force,"rotated",e_rot,"no clone",e_none)
# password store: stolen table, fixed work budget W; users pick wordlist ranks deterministically
WORDS=[f"pw{i}" for i in range(2000)]
users=[WORDS[(i*i*7+3)%400] if i%10 else WORDS[(i*37)%2000] for i in range(500)]  # 90% from top-400
def cracked(cost,budget):
    guesses=budget//cost
    top=set(WORDS[:guesses]); return sum(u in top for u in users)
B=1_000_000
fast=cracked(1,B); slow=cracked(100_000,B); slowest=cracked(1_000_000,B)
print("cracked of 500 under same budget: fast",fast,"slow(1e5)",slow,"slowest(1e6)",slowest)
# check real pbkdf2 is actually deterministic salted: same pw different salt differ
h=lambda s,p: hashlib.pbkdf2_hmac("sha256",p.encode(),s,1000).hex()
salted_differ=h(b"a",WORDS[0])!=h(b"b",WORDS[0])
# reuse across services: a cracked password reaches every service that shares it
reuse_reach=len(RES) if True else 0
ok=(r_shared==8 and r_scoped==1 and r_ci==2 and r_ci_naive==1 and e_force==1 and e_rot==0
    and fast>slow>=slowest and fast>=400 and slow<fast and salted_differ)
print(f"RESULT: {'PASS' if ok else 'FAIL'} scoped radius 1 vs shared 8 but CI edge makes it 2 (naive count says 1); force-push leaves leak usable, rotation voids it; fast hash cracks {fast}/500 vs slow {slow}/500")
