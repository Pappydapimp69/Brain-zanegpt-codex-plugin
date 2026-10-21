import hashlib, json, math, re
# Prediction (before run): (1) JS-order JSON hash differs for two logically equal states built in different insertion order, canonical hash equal;
# (2) raw-state restore costs 1 step vs count steps for replay, and both give same next roll; (3) a Math.<transcendental> regex lint flags 3 of 4 bad snippets
# (the destructured alias is missed = built to break "mechanically guard"), and flags a comment (false positive).
def js_order(keys):
    ints=sorted([k for k in keys if k.isdigit() and (k=="0" or not k.startswith("0"))], key=int)
    return ints+[k for k in keys if k not in ints]
def js_stringify(obj):
    if isinstance(obj,dict):
        return "{"+",".join(json.dumps(k)+":"+js_stringify(obj[k]) for k in js_order(list(obj)))+"}"
    if isinstance(obj,list): return "["+",".join(js_stringify(x) for x in obj)+"]"
    if isinstance(obj,float) and not math.isfinite(obj): return "null"   # JSON.stringify turns NaN/Infinity into null
    return json.dumps(obj)
def canon(obj):
    if isinstance(obj,dict): return "{"+",".join(json.dumps(k)+":"+canon(obj[k]) for k in sorted(obj))+"}"
    if isinstance(obj,list): return "["+",".join(canon(x) for x in obj)+"]"
    if isinstance(obj,float) and not math.isfinite(obj): raise ValueError("non-finite")
    return json.dumps(obj)
H=lambda s: hashlib.sha256(s.encode()).hexdigest()[:12]
A={"hp":10,"7":"x","name":"orc","3":"y"}; B={"3":"y","name":"orc","hp":10,"7":"x"}
C={"zeta":1,"alpha":2}; D={"alpha":2,"zeta":1}
r1 = (H(js_stringify(A))==H(js_stringify(B)), H(js_stringify(C))==H(js_stringify(D)), H(canon(A))==H(canon(B)), H(canon(C))==H(canon(D)))
print("1 js-hash equal int-keys/str-keys, canon equal int/str:", r1)
# NaN: two different broken states collapse to the same hash under stringify, canon rejects
n1={"x":float("nan")}; n2={"x":float("inf")}
collide = js_stringify(n1)==js_stringify(n2)
try: canon(n1); rej=False
except ValueError: rej=True
print("2 NaN vs Infinity collide:",collide,"canon rejects:",rej)
# RNG: LCG
M=2**32
step=lambda s:(1664525*s+1013904223)%M
def replay(seed,count):
    s=seed;n=0
    for _ in range(count): s=step(s);n+=1
    return s,n
cost={}
for count in (10,1000,100000):
    s,n=replay(12345,count); cost[count]=(n, 1, step(s)==step(s))
print("3 replay steps vs raw restore steps:",{c:(v[0],v[1]) for c,v in cost.items()})
# lint
bad=["x = Math.sin(t)","const y = Math.pow(a, 0.5)","let z = Math.cos(t) * 2","const {sin} = Math; w = sin(t)"]
ok_src=["x = Math.floor(t)","// Math.sin is banned here"]
rx=re.compile(r"Math\.(sin|cos|tan|pow|exp|log|atan2?|sqrt)\b")
flag_bad=[bool(rx.search(s)) for s in bad]; flag_ok=[bool(rx.search(s)) for s in ok_src]
print("4 lint flags bad:",flag_bad,"flags clean/comment:",flag_ok)
passed = r1==(False,False,True,True) and collide and rej and all(v[0]==c for c,v in cost.items()) and flag_bad==[True,True,True,False] and flag_ok==[False,True]
print("RESULT: %s stringify hash splits on both int-key and string-key insertion order (my prediction wrongly expected string-key order to be stable); NaN and Infinity collide; replay costs count steps vs 1; lint catches 3/4, misses destructured alias, false-flags a comment"%("PASS" if passed else "FAIL"))
