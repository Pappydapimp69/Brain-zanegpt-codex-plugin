# Two devices share a seeded sim via a base64 share code. Compare import modes.
import json, base64
def rng_next(s): s=(s*1103515245+12345)&0x7fffffff; return s
def new(): return {"rng":42,"hp":10,"cooldown":0,"log":[]}
def step(st):
    # rng draw is gated by a cooldown timer -> timer is save state
    if st["cooldown"]>0: st["cooldown"]-=1
    else:
        st["rng"]=rng_next(st["rng"]); st["hp"]+= (st["rng"]%5)-2; st["cooldown"]=3
    st["log"].append(st["hp"])
def export(st): return base64.b64encode(json.dumps(st).encode()).decode()
def imp_replace(code): return json.loads(base64.b64decode(code))
def imp_merge(local, code, fields=("rng","hp","log")):
    rem=json.loads(base64.b64decode(code)); out=dict(local)
    for k in fields: out[k]=rem[k]
    return out          # cooldown stays local
def run(st,n):
    for _ in range(n): step(st)
    return st
A=new(); run(A,7); code=export(A)
ref=json.loads(json.dumps(A)); run(ref,20)
# S1: replace import
B=imp_replace(code); run(B,20); s1=(B==ref)
# S2: merge import, local device has a different cooldown (it idled)
Bm=imp_merge({"rng":0,"hp":0,"cooldown":0,"log":[]},code); run(Bm,20); s2=(Bm==ref)
# S3: merge with matching cooldown by luck (cooldown happens equal)
loc={"rng":0,"hp":0,"cooldown":A["cooldown"],"log":[]}
Bl=imp_merge(loc,code); run(Bl,20); s3=(Bl==ref)
# S4 BREAK: exporter holds the dict by reference (no encode) -> payload moves
live=new(); run(live,7); payload=live  # aliasing, no snapshot
before=json.dumps(payload); run(live,2); moved=(json.dumps(payload)!=before)
# S5: JSON-encoded code hides aliasing
code2=export(live); run(live,2); hidden=(imp_replace(code2)["log"]==live["log"][:-2])
print("replace==ref",s1,"| merge(cooldown local, wrong)==ref",s2,"| merge(cooldown matches by luck)==ref",s3,"| aliased payload moved",moved,"| encoded payload stable",hidden)
ok = s1 and not s2 and s3 and moved and hidden
print("RESULT: %s replace import matches reference 1/1, merge with a stale gate timer diverges, merge only works when timer coincides, unencoded alias moves, encoded copy is stable" % ("PASS" if ok else "FAIL"))
