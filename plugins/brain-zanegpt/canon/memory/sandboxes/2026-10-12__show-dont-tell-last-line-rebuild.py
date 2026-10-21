# Rebuild of local__sandbox-show-dont-tell-linter-needs-the-last-line-check#E1
# Own fixture: 11 new verses, own word lists, own stating phrases. Stdlib only.
import re
EMO = {"sad","lonely","blue","bitter","cold","hollow","heartbroken","grief","angry","afraid","empty","hopeless","lost","sorrow"}
SENS = {"porch","screen","door","ashtray","radio","gravel","kettle","lamp","coat","hook","boots","mud","sink","dishes",
        "window","frost","truck","rain","coffee","stove","engine","dust","fence","wire","tire","sheet","bed","mug","glass","road"}
STATE = ["i realize","i realized","that's when i knew","now i know","it means","i understand","i see now"]
FEEL = re.compile(r"\b(i|i'm|i am|i feel|i felt|i was|we were|we're)\b")
def toks(s): return re.findall(r"[a-z']+", s.lower())
def ratio_flag(v):
    w=[t for l in v for t in toks(l)]
    return sum(t in EMO for t in w) > sum(t in SENS for t in w)
def last_naive(v):
    l=v[-1].lower(); w=toks(l)
    return any(t in EMO for t in w) or any(p in l for p in STATE)
def last_fixed(v):
    l=v[-1].lower(); w=toks(l)
    if any(p in l for p in STATE): return True
    for i,t in enumerate(w):
        if t in EMO:
            if i+1<len(w) and w[i+1] in SENS: continue  # modifier of a concrete noun
            return True  # emotion word not modifying a noun
    return False
V=[ # (label, verse) label: show / tell / explain / showblue
 ("show",["gravel in the tire tread","a kettle nobody lifts","his coat still on the hook","the radio on low"]),
 ("show",["frost on the window","two mugs in the sink","one boot by the door","dust on the stove"]),
 ("show",["the blue truck by the fence","rain on the wire","mud dried on the sheet","the engine ticking cool"]),
 ("tell",["i am so lonely","heartbroken and afraid","the grief is hollow","everything is empty"]),
 ("tell",["bitter and lost","sorrow in me","i'm sad and angry","hopeless now"]),
 ("explain",["gravel in the tire tread","a kettle nobody lifts","his coat still on the hook","that's when i knew i was alone"]),
 ("explain",["frost on the window","two mugs in the sink","one boot by the door","i realize i'm lonely"]),
 ("explain",["dust on the porch screen","an ashtray full of rain","a lamp left on all day","and i felt so hollow"]),
 ("explain",["the road past the fence","his glass on the bed","the coffee gone cold","now i know it means goodbye"]),
 ("showblue",["rain on the porch screen","the radio on low","dust on the dishes","the blue truck in the rain"]),
 ("showblue",["boots by the stove","frost on the wire","a lamp in the window","cold coffee in his mug"]),
]
want=lambda lab: lab in ("tell","explain")
def score(fn): return [(lab, fn(v)) for lab,v in V]
r_only=score(ratio_flag)
r_naive=score(lambda v: ratio_flag(v) or last_naive(v))
r_fix=score(lambda v: ratio_flag(v) or last_fixed(v))
def acc(r): return sum(f==want(l) for l,f in r)
def cnt(r,lab,val): return sum(1 for l,f in r if l==lab and f==val)
print("ratio only:", acc(r_only),"/",len(V), "explain passed:", cnt(r_only,"explain",False),"/4")
print("ratio+naive:", acc(r_naive),"/",len(V), "explain caught:", cnt(r_naive,"explain",True),"/4",
      "show FP:", cnt(r_naive,"show",True),"/3", "showblue FP:", cnt(r_naive,"showblue",True),"/2")
print("ratio+fixed:", acc(r_fix),"/",len(V), "explain caught:", cnt(r_fix,"explain",True),"/4",
      "show FP:", cnt(r_fix,"show",True),"/3", "showblue FP:", cnt(r_fix,"showblue",True),"/2")
# mid-verse blue truck should not flip verse 3 under naive
mid_ok = cnt(r_naive,"show",True)==0
# push: predicative colour word in last line must still flag under fix
pred = last_fixed(["rain on the wire","the lamp on low","i felt blue"])
print("predicative 'i felt blue' flagged by fix:", pred)
ok = (cnt(r_only,"explain",False)==4 and cnt(r_naive,"explain",True)==4 and mid_ok
      and cnt(r_naive,"showblue",True)==2 and acc(r_fix)==len(V) and pred)
print(("RESULT: PASS" if ok else "RESULT: FAIL"),
      f"ratio alone passes {cnt(r_only,'explain',False)}/4 show-then-explain; +naive last-line catches {cnt(r_naive,'explain',True)}/4, 0/3 show FP, but {cnt(r_naive,'showblue',True)}/2 colour/temp-modifier endings falsely flagged; noun-modifier skip gives {acc(r_fix)}/{len(V)} and still flags 'i felt blue'")
