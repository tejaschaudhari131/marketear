"""usage: quant_test.py MODE (fp32|fp16|int8dyn) NCLIPS
Size = bytes of torch.save(state_dict). fp16 = weights stored half, upcast to fp32 for compute on this CPU (so accuracy is that of fp16 weights; speed is not representative).
int8dyn = torch.ao.quantization.quantize_dynamic on nn.Linear (weights int8, activations quantized on the fly).
Accuracy: (a) free-decode WER/CER on the first N FLEURS sw_ke dev clips; (b) grammar-constrained crop+price on 12 synthetic clean sentences."""
import sys, os, io, csv, re, json, time, torch, jiwer, soundfile as sf
sys.path.insert(0, "src")
import asr
from grammar import parse_sentence
mode, N = sys.argv[1], int(sys.argv[2])
R = asr.Rec(); m = R.m
if mode == "fp16": m.half()
elif mode == "int8dyn": R.m = m = torch.ao.quantization.quantize_dynamic(m, {torch.nn.Linear}, dtype=torch.qint8)
buf = io.BytesIO(); torch.save(m.state_dict(), buf); size = buf.tell()
if mode == "fp16": m.float()   # compute in fp32 with fp16-rounded weights
print(mode, "size_MB %.0f" % (size/1e6), flush=True)
def norm(s): s = s.lower(); s = re.sub(r"[^\w\s]", "", s); return re.sub(r"\s+", " ", s).strip()
rows = list(csv.reader(open("data/fleurs_sw_dev.tsv"), delimiter="\t")); seen = set(); cl = []
for r in rows:
    if r[1] in seen: continue
    seen.add(r[1]); cl.append((r[1], norm(r[3])))
cl = cl[:N]; refs = []; hyps = []; t0 = time.time()
for f, ref in cl:
    a, _ = sf.read("data/fleurs_sw_dev_audio/dev/" + f, dtype="float32"); hyps.append(norm(R.free_decode(R.encode(R.feats(a))))); refs.append(ref)
print(mode, "FLEURS first %d: WER %.1f%% CER %.1f%% (%.1f s/clip)" % (len(cl), 100*jiwer.wer(refs, hyps), 100*jiwer.cer(refs, hyps), (time.time()-t0)/len(cl)), flush=True)
S = json.load(open("eval/synth48.json"))[:12]; ok = 0
for s in S:
    a, _ = sf.read("eval/audio_synth/%s.wav" % s["id"], dtype="float32"); eo = R.encode(R.feats(a)); c = R.constrained_decode(eo)
    p = parse_sentence(c[0][0].split()) if c else {}; ok += (p.get("crop") == s["truth"]["crop"] and p.get("price") == s["truth"]["price"])
print(mode, "SYNTHETIC clean, grammar-constrained crop+price: %d/%d" % (ok, len(S)), flush=True)
