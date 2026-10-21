"""Rebuild: a migration that merges x,y into position:{x,y} given a save lacking y.
Python driving real Node (the real JSON engine). PREDICTION (before run): for fixtures lacking y, in-memory
'y' in position is true and position.y===undefined, JSON round-trip drops the key (1 of 1 such fixtures);
null y survives as null; NaN becomes null (changes type); nested arrays turn undefined into null (not dropped)."""
import json, subprocess
JS = r'''
const migrate = s => ({ position: { x: s.x, y: s.y } });
const fx = { onlyX: {x: 7}, both: {x: 1, y: 2}, nullY: {x: 3, y: null}, nanY: {x: 4, y: NaN} };
const out = {};
for (const [k, v] of Object.entries(fx)) {
  const m = migrate(v);
  const rt = JSON.parse(JSON.stringify(m));
  out[k] = { inMem: 'y' in m.position, rtHasY: 'y' in rt.position, rtY: rt.position.y === undefined ? 'UNDEF' : String(rt.position.y) };
}
const arr = JSON.parse(JSON.stringify([undefined, 1]));
out.arrayUndef = String(arr[0]);
console.log(JSON.stringify(out));
'''
r = subprocess.run(["node", "-e", JS], capture_output=True, text=True, check=True)
o = json.loads(r.stdout)
for k, v in o.items(): print(k, v)
ok = (o['onlyX']['inMem'] and not o['onlyX']['rtHasY'] and o['both']['rtHasY'] and o['nullY']['rtHasY']
      and o['nullY']['rtY'] == 'null' and o['nanY']['rtY'] == 'null' and o['arrayUndef'] == 'null')
print("RESULT: %s onlyX inMem y=%s but roundtrip has y=%s; null kept, NaN->null, array undefined->null" % (
    "PASS" if ok else "FAIL", o['onlyX']['inMem'], o['onlyX']['rtHasY']))
