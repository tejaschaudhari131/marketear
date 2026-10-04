"""usage: run_eval.py META.json AUDIO_DIR OUT.jsonl WORKER NWORKERS COND[,COND..]   (COND = clean or CNR dB)
Pipeline per clip and condition: audio -> [SIMULATED FM channel at CNR] -> Whisper-sw-small encoder -> (a) free greedy decode + fuzzy parser, (b) grammar-constrained beam search."""
import sys, json, time, os, numpy as np, soundfile as sf
sys.path.insert(0, "src")
import asr
from fmchannel import fm_chain
from grammar import parse_sentence
from baseline import free_parse
meta, adir, out, w, nw, conds = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6].split(",")
S = json.load(open(meta))
done = set()
if os.path.exists(out):
    for l in open(out): r = json.loads(l); done.add((r["id"], r["cond"]))
R = asr.Rec(); fo = open(out, "a")
for k, s in enumerate(S):
    if k % nw != w: continue
    a, sr = sf.read(f"{adir}/{s['id']}.wav", dtype="float32")
    if a.ndim > 1: a = a.mean(1)
    for c in conds:
        if (s["id"], c) in done: continue
        t0 = time.time()
        x = a if c == "clean" else fm_chain(a, float(c), seed=k*100+int(float(c)))
        eo = R.encode(R.feats(x)); fr = R.free_decode(eo)
        cons = R.constrained_decode_fixed(eo) if os.environ.get('MARKETEAR_DECODER') == 'fixed' else R.constrained_decode(eo)  # fixed = experimental flag; default is the baseline used by the gate
        lf = R.loglik(eo, R.prompt + R.tok.encode(" " + fr, add_special_tokens=False))[0] if fr else None
        top = cons[0] if cons else None
        alts = [parse_sentence(t.split()) for t, _, _ in cons]
        rec = {"id": s["id"], "cond": c, "ref": s.get("text"), "truth": s.get("truth"), "free_text": fr, "free_parse": free_parse(fr), "lp_free": lf,
               "con_text": top[0] if top else None, "con_parse": alts[0] if alts else None, "lp_con": top[2] if top else None,
               "con_alts": [(t, p, round(sc, 3)) for (t, _, sc), p in zip(cons, alts)], "secs": round(time.time()-t0, 1)}
        fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
