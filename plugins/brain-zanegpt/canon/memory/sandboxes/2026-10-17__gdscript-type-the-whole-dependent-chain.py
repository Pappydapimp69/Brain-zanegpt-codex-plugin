"""Typed vs untyped ops in a toy bytecode interpreter, after Godot's documented rule that typed
GDScript uses optimized opcodes when operand types are known at compile time. Deterministic, stdlib.
A generic op costs a runtime type check + dispatch (cost 3); a typed op costs 1. An expression is
typed only if every operand is typed; an untyped result makes everything computed from it untyped.
The hot loop: 10 statements in a chain, each using the previous result plus a constant."""
def loop_cost(untyped_at=None, chain=True, n=10, iters=1000):
    known=[True]*n
    cost=0
    for i in range(n):
        typed = (i!=untyped_at) and (not chain or i==0 or known[i-1]) if untyped_at is not None else True
        if chain and i>0 and not known[i-1]: typed=False
        if i==untyped_at: typed=False
        known[i]=typed
        cost+= 1 if typed else 3
    return cost*iters, sum(not k for k in known)
full,_=loop_cost(); none,_=loop_cost(untyped_at=-1)
none=3*10*1000
first,u1=loop_cost(untyped_at=0); last,u9=loop_cost(untyped_at=9); mid,u5=loop_cost(untyped_at=5)
indep,ui=loop_cost(untyped_at=0,chain=False)
print(f"all typed {full}; all untyped {none}; untyped at start of chain {first} ({u1} generic ops); at 5: {mid} ({u5}); at end: {last} ({u9}); independent statements, one untyped: {indep} ({ui})")
gain_first=(none-first)/(none-full); gain_indep=(none-indep)/(none-full)
ok=u1==10 and first==none and u9==1 and ui==1 and gain_indep>0.85
print(("RESULT: PASS " if ok else "RESULT: FAIL ")+f"one untyped value at the head of a dependent chain makes all 10 ops generic (keeps {gain_first:.0%} of the typed gain); "
      f"at the tail it costs 1 op; in independent statements one untyped op keeps {gain_indep:.0%} of the gain")
