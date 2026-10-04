"""Experiment: padding / energy normalisation before the (SIMULATED) channel. Baseline decoder (beams 4). usage: pad_test.py SET(A|B) OUT.jsonl. 12 dB, same seeds as original runs."""
import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, "src")
import asr; from fmchannel import fm_chain; from grammar import parse_sentence
S, out = sys.argv[1], sys.argv[2]
d = "eval/gate_dryrun" if S == "A" else "results/gate_synthvoice2"
R = asr.Rec(); fo = open(out, "a")
def rmsnorm(a, db=-20.0):
    r = np.sqrt((a**2).mean()) + 1e-9; return np.clip(a * (10**(db/20) / r), -1, 1)
def pad(a, s): z = np.zeros(int(s*16000), dtype=np.float32); return np.concatenate([z, a, z])
V = {"none": lambda a: a, "pad1.0": lambda a: pad(a, 1.0), "pad0.5": lambda a: pad(a, 0.5), "norm": rmsnorm, "pad1.0+norm": lambda a: pad(rmsnorm(a), 1.0)}
for k, s in enumerate(json.load(open(d + "/meta.json"))):
    if not s["truth"]: continue
    a, _ = sf.read(f"{d}/audio/{s['id']}.wav", dtype="float32"); rec = {"id": s["id"], "set": S, "truth": s["truth"]}
    for name, f in V.items():
        x = fm_chain(f(a).astype(np.float32), 12.0, seed=k*100+12); eo = R.encode(R.feats(x))
        c = R.constrained_decode(eo); rec[name] = [(t, round(sc, 3), len(ids)-len(R.prompt)) for t, ids, sc in c]
    fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
