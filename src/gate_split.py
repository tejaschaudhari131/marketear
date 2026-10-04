"""Split one long phone recording into sentences at silences. usage: gate_split.py INPUT_AUDIO OUTDIR [expected_count]"""
import sys, subprocess, numpy as np, soundfile as sf, os, json
def load16k(path):
    tmp = "/tmp/_gate_in.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", tmp], check=True)
    a, _ = sf.read(tmp, dtype="float32"); return a
def split(a, sr=16000, min_gap=1.2, min_len=0.8, pad=0.25):
    fr = int(0.02*sr); n = len(a)//fr
    rms = np.sqrt((a[:n*fr].reshape(n, fr)**2).mean(1)) + 1e-9
    db = 20*np.log10(rms); floor = np.percentile(db, 10); peak = np.percentile(db, 95)
    thr = max(peak - 28.0, np.percentile(db, 20) + 6.0)
    act = db > thr; segs = []; i = 0
    while i < n:
        if act[i]:
            j = i
            while j < n and (act[j] or (j + int(min_gap/0.02) < n and act[j:j+int(min_gap/0.02)].any())): j += 1
            segs.append((i*fr, j*fr)); i = j
        else: i += 1
    out = []
    for s, e in segs:
        if (e - s)/sr >= min_len: out.append((max(0, s - int(pad*sr)), min(len(a), e + int(pad*sr))))
    return out
if __name__ == "__main__":
    a = load16k(sys.argv[1]); outd = sys.argv[2]; os.makedirs(outd, exist_ok=True)
    segs = split(a); exp = int(sys.argv[3]) if len(sys.argv) > 3 else None
    info = []
    for k, (s, e) in enumerate(segs, 1):
        sf.write(f"{outd}/seg{k:02d}.wav", a[s:e], 16000); info.append({"seg": k, "start_s": round(s/16000, 2), "dur_s": round((e-s)/16000, 2)})
    json.dump(info, open(f"{outd}/segments.json", "w"), indent=1)
    print(len(segs), "segments", "(expected %s)" % exp if exp else ""); 
    for x in info: print(x)
