# Deterministic sandbox (stdlib only). Hand-written model of: an automated linter (alt, labels, empty controls, contrast)
# versus a keyboard focus simulation (Tab / Escape) over small HTML fixtures.
# PREDICTION (before run 1): fixture B (modal with no Escape and no close control) scores 0 linter errors but fails the
# focus simulation (trapped); fixture C trips >= 4 linter errors; the best-known "light grey" #767676 passes AA 4.5 on
# white and fails AAA 7.0; a positive tabindex reorders focus vs DOM order, with 0 linter errors.
from html.parser import HTMLParser
def lum(h):
    h=h.lstrip("#"); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def ratio(a,b):
    la,lb=sorted((lum(a),lum(b)),reverse=True); return (la+0.05)/(lb+0.05)
class P(HTMLParser):
    def __init__(s): super().__init__(); s.el=[]; s.stack=[]
    def handle_starttag(s,t,a):
        d=dict(a); d["_t"]=t; d["_text"]=""; s.el.append(d); s.stack.append(d)
    def handle_endtag(s,t):
        while s.stack:
            e=s.stack.pop()
            if e["_t"]==t: break
    def handle_data(s,x):
        for e in s.stack: e["_text"]+=x.strip()
def lint(html):
    p=P(); p.feed(html); errs=[]
    labels={e.get("for") for e in p.el if e["_t"]=="label"}
    for e in p.el:
        if e["_t"]=="img" and "alt" not in e: errs.append("img-alt")
        if e["_t"]=="input" and e.get("type","text")!="hidden" and not (e.get("id") in labels or e.get("aria-label")): errs.append("input-label")
        if e["_t"] in("button","a") and not (e["_text"] or e.get("aria-label")): errs.append("empty-"+e["_t"])
        st=e.get("style","")
        if "color:" in st and "background:" in st:
            fg=st.split("color:")[1].split(";")[0].strip(); bg=st.split("background:")[1].split(";")[0].strip()
            if ratio(fg,bg)<4.5: errs.append("contrast")
    return errs
def focus_sim(html):
    p=P(); p.feed(html)
    foc=[e for e in p.el if e["_t"] in("button","a","input") or "tabindex" in e]
    foc=[e for e in foc if int(e.get("tabindex","0"))>=0]
    pos=sorted([e for e in foc if int(e.get("tabindex","0"))>0],key=lambda e:int(e["tabindex"]))
    order=pos+[e for e in foc if int(e.get("tabindex","0"))==0]
    modal=[e for e in p.el if e.get("role")=="dialog"]
    trapped=False
    if modal:
        m=modal[0]; inside=[e for e in foc if e.get("data-in")=="modal"]
        can_escape=m.get("data-esc")=="yes" or any(e.get("data-close")=="yes" for e in inside)
        trapped=not can_escape      # Tab cycles inside; no Escape handler and no close control => cannot leave
    dom=[e for e in foc]
    reordered=[e.get("id") for e in order]!=[e.get("id") for e in dom]
    return trapped,reordered
A='<label for=n>Name</label><input id=n><button id=b1>Save</button><img src=x alt="logo">'
B=('<button id=open>Open</button><div role=dialog data-esc=no><button id=ok data-in=modal>OK</button>'
   '<input id=q aria-label="Search" data-in=modal></div>')
C='<img src=x><input id=z><button></button><a href=#></a><p style="color:#bbbbbb;background:#ffffff">hi</p>'
D='<button id=a tabindex=3>Third</button><button id=b tabindex=1>First</button><button id=c>Plain</button>'
res={k:(lint(v),focus_sim(v)) for k,v in dict(A=A,B=B,C=C,D=D).items()}
for k,(l,f) in res.items(): print(k,"lint errors",len(l),l,"trapped/reordered",f)
g=ratio("#767676","#ffffff"); g7=ratio("#595959","#ffffff"); print("contrast #767676 %.2f  #595959 %.2f"%(g,g7))
brand=[("#767676","#ffffff"),("#1a73e8","#ffffff"),("#6c757d","#f8f9fa")]
tab=[(c,round(ratio(*c),2),ratio(*c)>=4.5,ratio(*c)>=7) for c in brand]; print("brand pairs (ratio, AA, AAA):",tab)
okB=len(res["B"][0])==0 and res["B"][1][0]
okC=len(res["C"][0])>=4
okD=len(res["D"][0])==0 and res["D"][1][1]
okAA=g>=4.5 and g<7 and any(r[2] and not r[3] for r in tab)
print("RESULT: %s linter blind to trap (B lint=0 trapped=%s) and to positive-tabindex reorder (D lint=0); C trips %d errors; #767676 is AA %.2f but not AAA"%("PASS" if okB and okC and okD and okAA else "FAIL",res["B"][1][0],len(res["C"][0]),g))
