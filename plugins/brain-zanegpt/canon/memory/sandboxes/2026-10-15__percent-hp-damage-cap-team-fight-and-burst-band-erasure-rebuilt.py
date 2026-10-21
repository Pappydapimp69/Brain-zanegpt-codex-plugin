# Deterministic (no RNG) model of a percent-of-defender-max-HP per-hit damage cap.
# Part 1: 3 attackers vs 1 boss. Part 2: band-level vs aggregate view of a burst skill's niche.
from fractions import Fraction as F
ROLLS=[F(x,10) for x in (5,8,10,12,15,7,13,9,11,14)]   # fixed damage-roll cycle, mean 10.4/10
def fight(boss_hp, cap_frac, cap_div, boss_actions, players=3, p_hp=100, atk=150, boss_atk=60, maxr=60):
    bhp=F(boss_hp); php=[F(p_hp)]*players; i=0
    for rnd in range(1,maxr+1):
        alive=[k for k in range(players) if php[k]>0]
        cap_b=F(boss_hp)*cap_frac/(cap_div if cap_div=="x" else cap_div) if cap_div!="x" else F(boss_hp)*cap_frac/len(alive)
        for k in alive:
            d=min(atk*ROLLS[i%10], cap_b); i+=1; bhp-=d
            if bhp<=0: return "boss_dies", rnd
        for a in range(boss_actions):
            alive=[k for k in range(players) if php[k]>0]
            if not alive: break
            tgt=alive[0]; d=min(boss_atk*ROLLS[i%10], F(p_hp)*cap_frac); i+=1; php[tgt]-=d
        if all(h<=0 for h in php): return "team_dies", rnd
    return "timeout", maxr
print("PART 1  3v1, boss HP 600, players 100 HP")
res={}
for name,args in {
 "uniform cap 0.20":(600,F(1,5),1,1),
 "cap/living attackers":(600,F(1,5),"x",1),
 "boss 3 actions":(600,F(1,5),1,3),
 "cap 0.20 boss HP 300":(300,F(1,5),1,1),
 "cap 0.20 boss HP 1200":(1200,F(1,5),1,1),
 "cap 0.05 boss 3 actions":(600,F(1,20),1,3),
 "cap 0.50 boss 3 actions":(600,F(1,2),1,3)}.items():
    res[name]=fight(*args); print(f"  {name:26} -> {res[name]}")
print("  absolute cap on boss vs on a 100-HP player at 0.20: boss", 600*0.2, "player", 100*0.2, "ratio", 600*0.2/(100*0.2))
# PART 2: skills are damage-fraction-of-defender-HP distributions on a fixed grid
steady=[F(1,4)]*10
burst=[F(1,2) if k%2 else F(0) for k in range(10)]          # same mean 0.25
lowfix=[F(1,10)]*10                                         # third skill: reliably small hits
def clear(skill,t,cap): return F(sum(1 for d in skill if min(d,cap)>=t),len(skill))
skills={"steady":steady,"burst":burst,"lowfix":lowfix}
bands=[F(k,20) for k in range(1,11)]    # thresholds 0.05..0.50
def winners(cap):
    out={}
    for t in bands:
        c={n:clear(s,t,cap) for n,s in skills.items()}; m=max(c.values())
        out[t]=sorted(n for n,v in c.items() if m>0 and v==m)
    return out
unc=winners(F(10)); cap=winners(F(1,5))
ever=lambda w: sorted({n for v in w.values() for n in v})
print("PART 2  ever-optimal uncapped:",ever(unc),"capped 0.20:",ever(cap))
lost=[float(t) for t in bands if "burst" in unc[t] and "burst" not in cap[t]]
dead=[float(t) for t in bands if unc[t] and not cap[t]]
print("  burst-winning bands lost to the cap:",lost,"| bands where NOBODY can win after cap:",dead)
# profile B: burst also ties for best in an unaffected low band (hits of 0.2 or more half the time, 0.5 the rest)
steady2=[F(1,5)]*10; burstB=[F(1,2)]*5+[F(1,5)]*5
skills={"steady":steady2,"burst":burstB,"lowfix":lowfix}
uncB=winners(F(10)); capB=winners(F(1,5))
lostB=[float(t) for t in bands if "burst" in uncB[t] and "burst" not in capB[t]]
print("PART 2b (burst keeps a tie-win in the low band) ever-optimal uncapped:",ever(uncB),"capped:",ever(capB),"| burst bands lost:",lostB)
cap_hi=winners(F(3,5)); print("  control cap 0.60 changes nothing:", cap_hi==uncB)
claim1 = res["uniform cap 0.20"][0]=="boss_dies" and res["cap/living attackers"][0]=="boss_dies" and res["boss 3 actions"][0]=="boss_dies"
claimA = bool(lost) and ever(unc)!=ever(cap)          # bare burst: aggregate DOES move, niche gone
claimB = bool(lostB) and ever(uncB)==ever(capB) and cap_hi==uncB   # aggregate flat while niche gone
print("RESULT:","PASS" if (claim1 and claimA and claimB) else "FAIL",
 f"3v1 fixes all still lose {claim1}; bare burst: aggregate {len(ever(unc))}->{len(ever(cap))} changes ({claimA}); burst with low-band tie: aggregate {len(ever(uncB))}->{len(ever(capB))} flat while bands {lostB} lost ({claimB})")
