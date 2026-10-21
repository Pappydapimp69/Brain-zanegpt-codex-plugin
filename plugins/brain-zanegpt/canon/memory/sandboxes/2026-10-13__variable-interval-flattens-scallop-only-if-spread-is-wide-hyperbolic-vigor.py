# Agent whose response vigor at time t since last reward = E[ 1/(1+K*D) ] where D = remaining wait
# to the next availability given no reward yet (hyperbolic value of the pending reward; goal-gradient shape).
# Prediction (written first): fixed interval -> scallop index (vigor last fifth / first fifth) >= 3;
# exponential (memoryless) variable interval -> index 1.00 exactly; a narrow uniform "variable" interval
# (+-20% of mean) still scallops with index >= 2; the index falls under 1.5 only when the spread is >= ~100% of the mean.
K=0.1; MEAN=50
def dist_fixed(): return {MEAN:1.0}
def dist_uniform(spread):
    lo=max(1,round(MEAN*(1-spread))); hi=round(MEAN*(1+spread)); n=hi-lo+1
    return {x:1.0/n for x in range(lo,hi+1)}
def dist_exp():  # geometric with mean MEAN, truncated at 10*MEAN (memoryless up to truncation)
    q=1-1.0/MEAN; return {x:(q**(x-1))*(1-q) for x in range(1,10*MEAN)}
def vigor(dist,t):
    num=den=0.0
    for x,p in dist.items():
        if x>t: den+=p; num+=p/(1+K*(x-t))
    return num/den if den else 0.0
def index(dist):
    hi=max(dist); T=hi if len(dist)==1 else MEAN
    early=sum(vigor(dist,t) for t in range(0,10))/10
    late=sum(vigor(dist,t) for t in range(int(.8*T),int(.8*T)+10))/10
    return late/early
fi=index(dist_fixed()); ex=index(dist_exp())
sp={s:index(dist_uniform(s)) for s in (0.2,0.5,0.8,0.99)}
print("S1 fixed interval index %.2f"%fi)
print("S2 exponential VI index %.2f"%ex)
print("S3 BREAK narrow-spread 'variable' uniform VI index:",{s:round(v,2) for s,v in sp.items()})
c1=fi>=3; c2=abs(ex-1)<0.1; c3=sp[0.2]>=2; c4=sp[0.99]<1.5
print("RESULT: %s FI index %.2f; exponential VI %.2f; uniform VI spread20%% %.2f, spread99%% %.2f (narrow-VI-still-scallops=%s, wide-flattens=%s)"%("PASS" if c1 and c2 and c3 and c4 else "FAIL",fi,ex,sp[0.2],sp[0.99],c3,c4))
