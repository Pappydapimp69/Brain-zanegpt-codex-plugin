# Deterministic: valid lags = base 0..4 plus jitter amplitude J (max valid lag = 4+J). Invalid lags 3..24 (overlap).
# Validity+cutoff c loses valid presses with lag>c. Prediction: lost==0 iff c>=4+J; best fixed gate-alone never (0,0) for J>=1.
invalid=list(range(3,25))
def valid_lags(J): return [(i%5)+ (J if i%7==0 else 0) for i in range(70)]
rows=[]; ok=True
for J in (0,2,4,8):
    v=valid_lags(J); mx=max(v)
    lost_at_mx=sum(1 for l in v if l>mx); lost_below=sum(1 for l in v if l>mx-1)
    gate_best=min((sum(1 for l in invalid if l<=g)+sum(1 for l in v if l>g),g) for g in range(0,30))
    rows.append((J,mx,lost_at_mx,lost_below,gate_best))
    ok&= lost_at_mx==0 and lost_below>0 and gate_best[0]>0
    print("J",J,"maxvalid",mx,"lost@cutoff=max",lost_at_mx,"lost@max-1",lost_below,"best gate-alone (wrong+lost,gate)",gate_best)
print("RESULT: %s cutoff=max valid lag loses 0, one below loses >0, gate alone never zero for J in 0,2,4,8"%("PASS" if ok else "FAIL"))
