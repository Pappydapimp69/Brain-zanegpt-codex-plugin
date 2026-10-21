"""Apology composer sandbox. Inputs are the means quoted in the kernel (Lewicki et al 2016);
Study 2 only has four quoted means, so claims about it use only those four."""
S1 = {"ack":3.49,"repair":3.34,"expl":3.17,"regret":3.03,"repent":3.00,"forgive":2.68}
S2 = {"repair":3.62,"repent":3.62,"ack":3.30,"expl":2.74}   # partial, as quoted
ok = []
def chk(name, cond, note):
    ok.append(cond); print(("PASS " if cond else "FAIL ")+name+": "+note)

# Scenario 1: S1 ranking, forgiveness request is weakest
rank1 = sorted(S1, key=S1.get, reverse=True)
chk("s1-weakest", rank1[-1]=="forgive", "rank="+">".join(rank1))
# Scenario 2: S2 -- forgiveness request not measured in quote; only claim: every quoted S2 mean > S1 forgive (2.68)
chk("s2-quoted-above-forgive", all(v>S1["forgive"] for v in S2.values()), "min quoted S2=%.2f vs S1 forgive 2.68"%min(S2.values()))
# Scenario 3 (BREAK): top-3 SET chosen from S1 is not the top-3 set in S2
top1 = set(rank1[:3]); rank2 = sorted(S2,key=S2.get,reverse=True); top2=set(rank2[:3])
m_s1set = sum(S2[c] for c in top1)/3; m_s2set = sum(S2[c] for c in top2)/3
chk("top-set-unstable", top1!=top2 and m_s2set>m_s1set, "S1 set=%s S2 set=%s meanS2 %.2f<%.2f"%(sorted(top1),sorted(top2),m_s1set,m_s2set))
# Scenario 4: a build rule 'own it + concrete repair, never lead with forgiveness request' is safe in both studies
def compose(m): 
    keep=[c for c in sorted(m,key=m.get,reverse=True) if c!="forgive"][:3]; return keep
c1=compose(S1); c2=compose(S2)
chk("rule-robust-core", "ack" in c1 and "repair" in c1 and "ack" in c2 and "repair" in c2, "S1=%s S2=%s"%(c1,c2))

# Scenario 5: repair gate. Repair only has value if a deal zone exists (BATNA floor) and the
# relationship is still repairable (opportunity principle). Value of repair offer = gate * w.
def apology_value(parts, ours_ceiling, their_batna, repairable, m=S1):
    zone = ours_ceiling - their_batna            # deal zone width; <=0 => no deal exists
    gate = 1.0 if (zone>0 and repairable) else 0.0
    return sum(m[p]*(gate if p in ("repair",) else 1.0) for p in parts)
good=["ack","repair"]
v_open = apology_value(good,10,6,True); v_nozone=apology_value(good,10,12,True); v_closed=apology_value(good,10,6,False)
chk("repair-gated", v_open>v_nozone and v_open>v_closed and abs(v_nozone-v_closed)<1e-9,
    "open=%.2f no-zone=%.2f closed=%.2f"%(v_open,v_nozone,v_closed))
# Scenario 6 (BREAK the gate): ack still carries value with no zone, so the gate removes repair only, never the whole apology
chk("ack-survives-gate", v_nozone==S1["ack"], "no-zone value=%.2f == ack mean"%v_nozone)
print("RESULT: %s apology: forgive weakest S1, top-set differs S1 vs S2 (%.2f<%.2f), ack+repair core robust, repair worth 0 without deal zone or repairability (open %.2f vs %.2f)"%("PASS" if all(ok) else "FAIL", m_s1set,m_s2set,v_open,v_nozone))
