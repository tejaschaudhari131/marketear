"""Free-decode WER of the HF fp32 model on the first 30 unique FLEURS sw_ke dev clips (same clips/order as /workspace/wb2/asr_fleurs.py)."""
import sys, csv, re, jiwer, soundfile as sf
sys.path.insert(0, "src")
import asr
def norm(s): s = s.lower(); s = re.sub(r"[^\w\s]", "", s); return re.sub(r"\s+", " ", s).strip()
rows = list(csv.reader(open("data/fleurs_sw_dev.tsv"), delimiter="\t")); seen = set(); cl = []
for r in rows:
    if r[1] in seen: continue
    seen.add(r[1]); cl.append((r[1], norm(r[3])))
cl = cl[:int(sys.argv[1])]; R = asr.Rec(); refs = []; hyps = []
for f, ref in cl:
    a, _ = sf.read("data/fleurs_sw_dev_audio/dev/" + f, dtype="float32")
    hyps.append(norm(R.free_decode(R.encode(R.feats(a))))); refs.append(ref)
print("HF fp32 greedy, FLEURS sw_ke dev, first %d clips: WER %.1f%% CER %.1f%%" % (len(cl), 100*jiwer.wer(refs, hyps), 100*jiwer.cer(refs, hyps)))
