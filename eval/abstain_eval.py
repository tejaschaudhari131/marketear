import json,glob,numpy as np,sys
sys.path.insert(0,'eval')
rows=[json.loads(l) for f in glob.glob('eval/gate_dryrun/results_w*.jsonl') for l in open(f)]
rows+= [json.loads(l) for f in glob.glob('results/synth48_w*.jsonl') for l in open(f)]
def margin(r):
    a=r['con_alts']; t=a[0]; o=[x[2] for x in a[1:] if x[1].get('price')!=t[1].get('price') or x[1].get('crop')!=t[1].get('crop')]
    return t[2]-max(o) if o else 10.0
def ok(r):
    p=r['con_parse'];t=r['truth']; return bool(t and p and p['crop']==t['crop'] and p['price']==t['price'])
print("| rule | clips accepted | accepted and correct | accepted and WRONG (in-vocab) | abstain-test sentences accepted (of 6) | in-vocab clips abstained |\n|---|---|---|---|---|---|")
inv=[r for r in rows if r['truth']]; oov=[r for r in rows if not r['truth']]
for m,g in [(-99,-999),(2,-999),(-99,-25),(2,-25),(4,-25),(2,-20),(2,-30)]:
    acc=lambda r: margin(r)>=m and (r['lp_con']-r['lp_free'])>=g
    A=[r for r in inv if acc(r)]
    print("| margin>=%s and gap>=%s | %d/%d | %d | %d | %d | %d |"%(m if m>-99 else 'off',g if g>-999 else 'off',len(A),len(inv),sum(ok(r) for r in A),sum(not ok(r) for r in A),sum(acc(r) for r in oov),len(inv)-len(A)))
print("\nmargins of wrong in-vocab clips:",[round(margin(r),1) for r in inv if not ok(r)])
