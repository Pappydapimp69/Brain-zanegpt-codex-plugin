"""Toy deterministic model: salt-timing window -> surface water -> sear delay -> carryover overshoot.
Minutes as integer ticks. No RNG. Parameters are assumptions; the output is the SHAPE, not real constants."""
DRAW=1.0      # osmotic draw per min, fades as brine saturates
FADE=0.03     # draw fade rate
REABS=0.055   # fraction of surface brine reabsorbed per min
def surface_water(t_salt):
    s=0.0; salt_gradient=1.0
    for _ in range(t_salt):
        s+=DRAW*salt_gradient
        salt_gradient=max(0.0,salt_gradient-FADE*salt_gradient)  # gradient decays as meat takes up salt
        s-=REABS*s
    return s
def sear(water, pat_dry=False):
    if pat_dry: water*=0.1
    evap_minutes=water*0.35      # heat spent on phase change before Maillard (cap ~100C)
    brown_start=evap_minutes
    interior_gain=evap_minutes*0.6   # extra pan time pushes interior temp (carryover kernel)
    return brown_start, interior_gain
rows=[]
for t in [0,5,10,20,25,30,40,60,120,480]:
    w=surface_water(t); b,g=sear(w); bp,gp=sear(w,True)
    rows.append((t,w,b,g,bp,gp)); print(f"salt {t:>3}m before: surface_water={w:5.2f} browning_delay={b:4.2f}min interior_overshoot={g:4.2f}C | pat-dry delay={bp:4.2f}")
ws={t:r[1] for t,r in zip([r[0] for r in rows],rows)}
peak=max(rows,key=lambda r:r[1])[0]
print("peak surface water at",peak,"min")
ok1 = ws[0]==0 and ws[120]<ws[peak] and ws[480]<ws[120]*0.9+1e-9 or ws[480]<=ws[peak]
ok_mid = all(ws[peak]>ws[t] for t in (0,5,120,480))          # bad window is a middle hump, not monotone
ok_pat = max(r[4] for r in rows)<0.25*max(r[2] for r in rows) # pat-dry rescues even the worst timing (break attempt)
ok_late = ws[40]<ws[25] or ws[40]<ws[peak]                    # 40 min is past the hump
print("hump:",ok_mid,"pat-dry rescue:",ok_pat,"40m past hump:",ok_late)
print("RESULT: %s peak=%dm worst_delay=%.2fmin patdry_worst=%.2fmin"%("PASS" if ok_mid and ok_pat and ok_late else "FAIL",peak,max(r[2] for r in rows),max(r[4] for r in rows)))
