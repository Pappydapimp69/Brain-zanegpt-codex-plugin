import sys,types
SRC='''
def price(qty, unit, member):
    total = qty * unit
    if qty >= 10:
        total = total * 0.9
    if member:
        total = total - 5
    if total < 0:
        total = 0
    return round(total, 2)
'''
MUT=[("qty >= 10","qty > 10"),("total * 0.9","total * 0.8"),("total - 5","total + 5"),("if member","if not member"),("total < 0","total <= 0"),("qty * unit","qty + unit"),("round(total, 2)","round(total, 1)")]
def load(src):
    m=types.ModuleType("m");exec(src,m.__dict__);return m
def coverage(tests,src):
    lines=set()
    code=compile(src,"<s>","exec")
    def tr(f,e,a):
        if f.f_code.co_filename=="<s>" and e=="line": lines.add(f.f_lineno)
        return tr
    m=types.ModuleType("m");exec(code,m.__dict__)
    sys.settrace(tr)
    try:
        for t in tests: t(m)
    finally: sys.settrace(None)
    body={i for i,l in enumerate(src.split("\n"),1) if l.startswith("    ")}
    return len(lines&body)/len(body)
def passes(tests,src):
    m=load(src)
    try:
        for t in tests: t(m)
        return True
    except AssertionError: return False
def kill(tests):
    k=0
    for a,b in MUT:
        if not passes(tests,SRC.replace(a,b)): k+=1
    return k
def t_noassert(m):
    for args in [(1,10,False),(12,10,True),(1,1,True),(0,0,True)]: m.price(*args)
def t_weak(m):
    for args in [(1,10,False),(12,10,True),(1,1,True)]: assert m.price(*args) is not None
def t_strong(m):
    assert m.price(1,10,False)==10; assert m.price(10,10,False)==90.0; assert m.price(12,10,True)==103.0; assert m.price(9,10,False)==90; assert m.price(1,1,True)==0; assert m.price(3,1.25,False)==3.75
def t_mock(m):
    calls=[]
    orig=m.round if hasattr(m,"round") else None
    fake=lambda x,n:(calls.append((x,n)) or 0)
    m.__dict__["round"]=fake
    m.price(12,10,True); assert calls==[(103.0,2)]   # asserts internal call, passes 
    del m.__dict__["round"]
def t_mock_real(m): m.price(12,10,True)  # needed only for coverage count
tests={"A no-assert":[t_noassert],"B weak assert":[t_weak],"C exact":[t_strong],"D mock-internal":[t_mock]}
out={}
for n,t in tests.items():
    out[n]=(round(coverage(t,SRC),2),kill(t)); print(n,"coverage",out[n][0],"killed",out[n][1],"of",len(MUT))
# refactor: behaviour-preserving rewrite using int-cents instead of round() call
REF=SRC.replace("return round(total, 2)","return float(f'{total:.2f}')")
print("behaviour-preserving refactor: exact passes",passes(tests["C exact"],REF),"mock-internal passes",passes(tests["D mock-internal"],REF))
ok=(out["A no-assert"][0]==1.0 and out["A no-assert"][1]==0 and out["B weak assert"][1]<=1 and out["C exact"][1]>=6 and passes(tests["C exact"],REF) and not passes(tests["D mock-internal"],REF))
print("RESULT:","PASS" if ok else "FAIL",f"full coverage {out['A no-assert'][0]} killed {out['A no-assert'][1]}/7 with no asserts, weak asserts killed {out['B weak assert'][1]}, exact asserts killed {out['C exact'][1]}; mock-internal test failed a behaviour-preserving refactor")
