import json
rows=[json.loads(l) for l in open('results/real_numbers.jsonl')]
def nw(r):  # number of words in the number phrase = words of ref minus context unknown -> use truth words via swnum.say length of ref run
    import sys; sys.path.insert(0,'src'); from swnum import NUMBER_WORDS
    ws=r['ref'].split(); run=[w for w in ws if w in NUMBER_WORDS]; return len(run)
for label,flt in (("all",lambda r:True),("single-word numbers (e.g. 'nane')",lambda r:nw(r)==1),("multi-word numbers (e.g. 'ishirini na saba')",lambda r:nw(r)>=2)):
    for c in ['clean','12']:
        R=[r for r in rows if r['cond']==c and flt(r)]
        if not R: continue
        n=len(R); f=sum(r['free_value']==r['truth'] for r in R); k=sum(r['con_value']==r['truth'] for r in R)
        print("| %s | %s | %d | %d (%.0f%%) | %d (%.0f%%) |"%(label,"clean" if c=="clean" else "SIMULATED FM 12 dB",n,f,100*f/n,k,100*k/n))
