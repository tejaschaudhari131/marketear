"""SYNTHETIC VOICE stand-in for the human gate recording. TTS: Mwau/waxal_swahili-tts-mms (VITS fine-tune of facebook/mms-tts-swh on the
WAXAL swa_tts single speaker; CC-BY-NC-4.0). Different weights/voice from the dry run, which used facebook/mms-tts-swh with random speed/pitch.
Reads recording/sentences.txt in order, ~3 s silence between sentences, one continuous 16 kHz mono wav."""
import sys, re, numpy as np, soundfile as sf, torch
from transformers import VitsModel, AutoTokenizer
torch.set_num_threads(2); torch.manual_seed(7)
R = "Mwau/waxal_swahili-tts-mms"
tok = AutoTokenizer.from_pretrained(R); m = VitsModel.from_pretrained(R).eval()
lines = [l.strip() for l in open("recording/sentences.txt", encoding="utf-8") if l.strip()]
lines = [re.sub(r"^\s*\d+[\.\)]\s*", "", l) for l in lines]
assert len(lines) == 22, len(lines)
sr = m.config.sampling_rate; sil = np.zeros(int(3.0 * sr), dtype=np.float32); out = [np.zeros(int(1.0*sr), dtype=np.float32)]
for k, t in enumerate(lines):
    with torch.no_grad(): w = m(**tok(t.lower(), return_tensors="pt")).waveform[0].numpy()
    w = w / (np.abs(w).max() + 1e-9) * 0.8; print(k+1, round(len(w)/sr, 1), "s", t[:70], flush=True)
    out += [w.astype(np.float32), sil]
a = np.concatenate(out); sf.write(sys.argv[1], a, sr); print("sr", sr, "total s", round(len(a)/sr, 1))
