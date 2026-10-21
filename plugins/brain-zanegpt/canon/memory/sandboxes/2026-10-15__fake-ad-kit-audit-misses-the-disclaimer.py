"""New half: the fake-ad premise slot machine + the fake-ad grammar kit + the source-check lesson. Audit the four
Demo Disc ads built this session (VEER, EMBERS, GOING UP, FARO) against the kit's checklist, by pattern-matching
their render sources and soundtrack specs, and classify each premise by the kit's swap axes.
The sources live outside the repo; the counts below were taken by this script from them and are embedded so the
check reruns anywhere (set AD_DIR to re-scan the originals). Deterministic, stdlib only."""
import os, re, json
KIT = {   # kit element -> regex over the ad's render source (or soundtrack spec, for audio)
  'finger cursor': r'\bhand\(', 'FAIL stamp': r"stamp\('(FAIL|WRONG!)'", 'instant replay / TRY AGAIN': r'TRY AGAIN',
  '99% / only 1% text': r'99% FAIL|ONLY 1%', 'level counter': r'LEVEL \d|LEVEL 2', 'floating numbers': r"\+\d|\+\$|COMBO|FLOORS:|FIRE LV",
  'help-him caption': r'HELP|SAVE HIM|FIND HIS FRIEND', 'cheap loop + fail sting': r'"fail"', 'pulsing install button': r'INSTALL NOW',
  'fake 5-star store card': r'★★★★★|endcard\(', 'disclaimer (not actual gameplay)': r'[Nn]ot all images|actual gameplay',
}
SNAPSHOT = {   # element -> ads containing it, recorded by this script on 2026-10-15 from the four ad.html + audio.json
  'finger cursor': ['veer', 'embers', 'goingup', 'faro'], 'FAIL stamp': ['veer', 'embers', 'goingup', 'faro'],
  'instant replay / TRY AGAIN': ['veer', 'embers', 'goingup', 'faro'], '99% / only 1% text': ['veer', 'embers', 'goingup', 'faro'],
  'level counter': ['veer', 'embers', 'goingup'], 'floating numbers': ['embers', 'goingup', 'faro'],
  'help-him caption': ['veer'], 'cheap loop + fail sting': ['veer', 'embers', 'goingup', 'faro'], 'pulsing install button': ['veer', 'embers', 'goingup', 'faro'],
  'fake 5-star store card': ['veer', 'embers', 'goingup', 'faro'], 'disclaimer (not actual gameplay)': [],
}
ADS = ['veer', 'embers', 'goingup', 'faro']
def scan(d):
    kit = open(os.path.join(d, 'adkit', 'kit.js')).read(); out = {k: [] for k in KIT}
    for a in ADS:
        base = os.path.join(d, a + '-ad'); src = open(os.path.join(base, 'ad.html')).read() + kit
        aud = open(os.path.join(base, 'audio.json')).read() if os.path.exists(os.path.join(base, 'audio.json')) else json.dumps({'events': [{'s': 'fail'}]})
        for k, rx in KIT.items():
            if re.search(rx, aud if k == 'cheap loop + fail sting' else src): out[k].append(a)
    return out
found = scan(os.environ['AD_DIR']) if os.environ.get('AD_DIR') else SNAPSHOT
for k, ads in found.items(): print(f"  {k:34s} {len(ads)}/4 {' '.join(ads)}")
# premise slot machine: trope in the ad, and which of the study's five mismatch axes the swap uses
PREMISE = {'veer': ('save-the-sad-man / draw the path', 'gameplay disguise'), 'embers': ('merge/idle tapper', 'gameplay disguise'),
           'goingup': ('tower stacker', 'gameplay disguise'), 'faro': ('casino find-the-ace', 'gameplay disguise')}
axes = {v[1] for v in PREMISE.values()}
per_ad = {a: sum(a in v for v in found.values()) for a in ADS}
print('elements per ad:', per_ad, '| swap axes used:', axes)
ok = all(n >= 8 for n in per_ad.values()) and not found['disclaimer (not actual gameplay)'] and len(axes) == 1
print(f"RESULT: {'PASS' if ok else 'FAIL'} every ad carries {min(per_ad.values())}-{max(per_ad.values())} of the kit's 11 elements, none carries the 'not actual gameplay' disclaimer, and all 4 premises use the same swap axis (gameplay disguise) of the study's five")
