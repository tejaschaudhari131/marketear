"""Synthetic speech for TEST MATERIAL ONLY: facebook/mms-tts-swh (VITS, CC-BY-NC-4.0 => never shipped in the product).
One voice; 'pseudo-speakers' = random speaking rate, noise scale and resampling (pitch+speed) so the recognizer does not see 200 identical clips."""
import json, sys, random, numpy as np, soundfile as sf, torch, scipy.signal as sg
from transformers import VitsModel, AutoTokenizer
torch.set_num_threads(1)
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-swh"); m = VitsModel.from_pretrained("facebook/mms-tts-swh").eval()
src, outdir = sys.argv[1], sys.argv[2]
import os; os.makedirs(outdir, exist_ok=True)
for k, s in enumerate(json.load(open(src))):
    r = random.Random(1000+k); torch.manual_seed(1000+k)
    m.speaking_rate = r.uniform(0.85, 1.15); m.noise_scale = r.uniform(0.4, 0.8)
    with torch.no_grad(): w = m(**tok(s["text"], return_tensors="pt")).waveform[0].numpy()
    f = r.uniform(0.9, 1.1)                       # pitch/speed factor via resampling
    w = sg.resample_poly(w, int(round(1000*f)), 1000) if abs(f-1) > 1e-3 else w
    w = w / (np.abs(w).max()+1e-9) * 0.8
    sf.write(f"{outdir}/{s['id']}.wav", w.astype(np.float32), 16000)
    s["tts"] = {"speaking_rate": round(m.speaking_rate,3), "noise_scale": round(m.noise_scale,3), "resample_factor": round(f,3), "seconds": round(len(w)/16000,2)}
