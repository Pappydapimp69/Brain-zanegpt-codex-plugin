# Encodes three LEGAL kernels' stated tests as predicates and enumerates a scenario grid (deterministic).
# NOT legal advice: tests whether the kernels' structures compose without contradiction and where the owner flips.
import itertools, datetime
NINE={'collective','motion-picture','translation','supplementary','compilation','instructional','test','answer-material','atlas'}
def wfh(category, written, express, signed_all):          # kernel work-for-hire: all four at once (contractor case)
    return category in NINE and written and express and signed_all
def owner(category, written, express, signed_all, assignment):
    if wfh(category, written, express, signed_all): return 'client'
    return 'client' if assignment else 'freelancer'     # default: creator keeps it unless transferred in writing
def public_use_rights(license_file, owner_):             # kernel no-license-file: public != permitted
    return 'granted-by-owner' if license_file else 'none'
cats=['software','translation','logo']
grid=list(itertools.product(cats,[0,1],[0,1],[0,1],[0,1]))
client=0;free=0;sw_wfh=0;wfh_only_by_all4=True
for c,w,e,s,a in grid:
    o=owner(c,w,e,s,a); client+=o=='client'; free+=o=='freelancer'
    if c=='software' and wfh(c,w,e,s): sw_wfh+=1
    if wfh(c,w,e,s) and not (w and e and s and c in NINE): wfh_only_by_all4=False
# composition: client publishes the repo with MIT license; who can grant that?
bad=0;n=0
for c,w,e,s,a in grid:
    if c!='software': continue
    n+=1
    # client's MIT grant is valid only if client owns (or holds a licence with right to sublicense)
    valid = owner(c,w,e,s,a)=='client'
    bad += (not valid)
# SoL kernel: claim-type deadline; breach of the assignment promise is a written-contract claim (4y) vs a 2y PI-style rule
def deadline(d,years):
    try: return d.replace(year=d.year+years)
    except ValueError: return d.replace(year=d.year+years,day=28)   # Feb 29 edge
broken=datetime.date(2024,2,29)
d4,d2=deadline(broken,4),deadline(broken,2)
wrong_barred = (datetime.date(2027,6,1)>d2) and (datetime.date(2027,6,1)<=d4)   # filing 2027-06-01
print('grid',len(grid),'client-owns',client,'freelancer-owns',free)
print('software+all4 WFH holds in',sw_wfh,'scenarios (nine-category bar)')
print('software scenarios',n,'where a client MIT licence would be granted by a non-owner',bad)
print('contract breach 2024-02-29: 4y deadline',d4,'2y',d2,'filing 2027-06-01 barred under wrong 2y rule only:',wrong_barred)
ok = sw_wfh==0 and wfh_only_by_all4 and bad==n//2 and wrong_barred and public_use_rights(False,'x')=='none'
print('RESULT: %s software never WFH (0/%d), only assignment moves ownership; non-owner MIT grants in %d/%d software scenarios; wrong-type deadline bars a live claim'%('PASS' if ok else 'FAIL',len([g for g in grid if g[0]=='software']),bad,n))
