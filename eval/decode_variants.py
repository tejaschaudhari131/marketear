"""Experiment harness (SYNTHETIC audio for sets A/B; REAL RFI speech for set C): run decoder variants on cached encoder outputs, store N-best lists.
usage: decode_variants.py SET OUT.jsonl WORKER NWORKERS    SET = A (first synthetic voice = original dry run) | B (second voice, WAXAL) | C (SLR25 number test, oracle frame)
Gate conditions are NOT changed: 12 dB SIMULATED FM CNR, same seeds as the original runs."""
import sys, json, glob, random, re, os, time, numpy as np, soundfile as sf
sys.path.insert(0, "src")
import asr
from fmchannel import fm_chain
from grammar import build_sentence_nfa, build_frame_nfa, Walker
SET, out, w, nw = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); COND = "12"
R = asr.Rec(); base_walker = R.walker
unit_walker = None
if SET in "AB":
    n, end = build_sentence_nfa(R.enc, require_unit=True); unit_walker = Walker(n, end)
def nb(cons): return [(t, round(sc, 3), len(ids) - len(R.prompt)) for t, ids, sc in cons]
items = []
if SET in "AB":
    d = "eval/gate_dryrun" if SET == "A" else "results/gate_synthvoice2"
    for k, s in enumerate(json.load(open(d + "/meta.json"))):
        if s["truth"]: items.append(dict(id=s["id"], audio=f"{d}/audio/{s['id']}.wav", seed=k*100+12, truth=s["truth"], ref=s["text"]))
else:
    from swnum import NUMBER_WORDS, parse
    base = "data/slr25/data_broadcastnews_sw/data/test/"
    def norm(s): s = s.lower(); s = re.sub(r"[^\w\s]", "", s); return re.sub(r"\s+", " ", s).strip()
    txt = {l.split(" ", 1)[0]: norm(l.split(" ", 1)[1]) for l in open(base + "text")}
    files = {f.split("/")[-1][:-4]: f for f in glob.glob(base + "wav*/*/*.wav")}
    cands = []
    for k, t in txt.items():
        ws = t.split()
        if k not in files or not (4 <= len(ws) <= 25): continue
        runs = []; i = 0
        while i < len(ws):
            if ws[i] in NUMBER_WORDS and ws[i] != "na":
                j = i
                while j < len(ws) and ws[j] in NUMBER_WORDS: j += 1
                runs.append((i, j)); i = j
            else: i += 1
        if len(runs) != 1: continue
        i, j = runs[0]; v = parse(ws[i:j])
        if v is None or v == 0: continue
        cands.append((k, ws[:i], ws[i:j], v, ws[j:]))
    random.seed(5); random.shuffle(cands); sel = []
    for c in cands:
        a, sr = sf.read(files[c[0]], dtype="float32")
        if 2 <= len(a)/sr <= 14: sel.append(c)
        if len(sel) == 40: break
    sel = sel[:20]   # time box: first 20 of the 40 SLR25 sentences
    for k, c in enumerate(sel): items.append(dict(id=c[0], audio=files[c[0]], seed=k*7+12, truth=c[3], pre=c[1], suf=c[4], ref=" ".join(c[1]+c[2]+c[4])))
done = set()
if os.path.exists(out): done = {json.loads(l)["id"] for l in open(out)}
fo = open(out, "a")
for k, it in enumerate(items):
    if k % nw != w or it["id"] in done: continue
    t0 = time.time(); a, _ = sf.read(it["audio"], dtype="float32")
    if a.ndim > 1: a = a.mean(1)
    if SET == "C":
        nfa, end = build_frame_nfa(R.enc, " ".join(it["pre"]), " ".join(it["suf"])); R.walker = Walker(nfa, end)
    x = fm_chain(a, 12.0, seed=it["seed"]); eo = R.encode(R.feats(x))
    rec = dict(it); rec.pop("audio"); rec["set"] = SET; rec["dur_s"] = round(len(a)/16000, 2)
    rec["base"] = nb(R.constrained_decode(eo))                                 # baseline: beams 4
    rec["b16"] = nb(R.constrained_decode(eo, beams=16, topk=16))               # wider beam, N-best
    if unit_walker is not None:
        R.walker = unit_walker; rec["unit16"] = nb(R.constrained_decode(eo, beams=16, topk=16)); R.walker = base_walker
    rec["secs"] = round(time.time()-t0, 1); fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
