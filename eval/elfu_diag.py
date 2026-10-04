"""Diagnose dropped-thousands: teacher-forced log-lik of TRUTH sentence vs the sentence the constrained beam search returned."""
import sys, json, glob, soundfile as sf
sys.path.insert(0,"src")
import asr; from fmchannel import fm_chain
meta, adir, resf, cond = sys.argv[1:5]
S=json.load(open(meta)); R=asr.Rec()
res={(r["id"],r["cond"]):r for f in glob.glob(resf) for l in open(f) for r in [json.loads(l)]}
for k,s in enumerate(S):
    if not s["truth"] or (s["id"],cond) not in res: continue
    r=res[(s["id"],cond)]
    a,_=sf.read(f"{adir}/{s['id']}.wav",dtype="float32")
    x=fm_chain(a,float(cond),seed=k*100+int(float(cond))); eo=R.encode(R.feats(x))
    ids=lambda t:[i for w in t.split() for i in R.enc(w)]
    lt,nt=R.loglik(eo,R.prompt+ids(s["text"].strip().lower())); ld,nd=R.loglik(eo,R.prompt+ids(r["con_text"]))
    print(json.dumps({"id":s["id"],"truth_ll":round(lt,1),"ntok_truth":nt,"dec_ll":round(ld,1),"ntok_dec":nd,"beam_ll":round(r["lp_con"],1),"truth_better":lt>ld,"dec":r["con_text"]}),flush=True)
