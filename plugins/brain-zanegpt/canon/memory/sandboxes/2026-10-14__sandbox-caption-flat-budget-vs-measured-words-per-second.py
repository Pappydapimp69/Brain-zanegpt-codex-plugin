# 16 short on-screen captions (English, my Spanish translation). Duration fixed per caption (seconds).
PAIRS = [
 ("Shop now", "Compra ya", 1.0), ("Link in bio", "Enlace en la bio", 1.0),
 ("Free shipping", "Envio gratis", 1.0), ("Wait for it", "Espera el final", 1.0),
 ("Only 3 left", "Solo quedan 3", 1.0), ("Try it today", "Pruebalo hoy", 1.0),
 ("Best gift ever", "El mejor regalo de todos", 1.5), ("I tried it for 30 days", "Lo probe durante 30 dias", 2.5),
 ("No more tangled cables", "Se acabaron los cables enredados", 2.5), ("Wow", "Que barbaridad", 0.5),
 ("It works", "Funciona de verdad", 0.8), ("Watch this", "Mira esto", 1.0),
 ("Ready in two minutes", "Listo en solo dos minutos", 2.0), ("Wash, dry, repeat", "Lava, seca y repite", 1.5),
 ("Do not skip this", "No te saltes esto", 1.2), ("Day one", "Dia uno", 0.7)]
LIMIT = 10.0   # words per second ceiling from the captions kernel (5-10)
wc = lambda s: len(s.replace(",", "").split())
ratios = [wc(es) / wc(en) for en, es, d in PAIRS]
mean = sum(ratios) / len(ratios)
print(f"mean word ratio {mean:.3f}  min {min(ratios):.2f}  max {max(ratios):.2f}")
ES = {en: es for en, es, d in PAIRS}
def over(en, d, words): return words / d > LIMIT
rows = {}
for f in (1.0, 0.6, 0.45, 0.35, 0.25):          # duration scale: smaller = tighter captions
    real = miss8 = fa30 = miss_m = 0
    for en, es, d in PAIRS:
        d = d * f
        r = over(en, d, wc(es))
        real += r
        miss8 += r and not over(en, d, wc(en) * 1.08)
        fa30 += (not r) and over(en, d, wc(en) * 1.30)
        miss_m += r and not over(en, d, wc(ES[en]))
    rows[f] = (real, miss8, fa30, miss_m)
    print(f"duration x{f}: real overruns {real}, flat +8% misses {miss8}, flat +30% false alarms {fa30}, measured misses {miss_m}")
first = max((f for f, v in rows.items() if v[0] > 0), default=None)
ok = (abs(mean - 1.08) < 0.25 and max(ratios) >= 1.5 and rows[1.0][0] == 0
      and any(v[1] > 0 for v in rows.values()) and any(v[2] > 0 for v in rows.values()) and all(v[3] == 0 for v in rows.values()))
worst = max(rows.values(), key=lambda v: v[1])
print("RESULT: %s mean ratio %.2f but range %.2f-%.2f; no overruns at x1.0 (%d), first appear at x%s; flat +8%% budget misses up to %d, flat +30%% raises up to %d false alarms, measured strings 0 misses"
      % ("PASS" if ok else "FAIL", mean, min(ratios), max(ratios), rows[1.0][0], first, worst[1], max(v[2] for v in rows.values())))
