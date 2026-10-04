"""usage: gate_prepare.py RECORDING_FILE WORKDIR   -> splits at silences, writes WORKDIR/audio/gNN.wav and WORKDIR/meta.json (gate truth from recording/script.json)
If the number of segments differs from 22, writes WORKDIR/NEEDS_MANUAL_MAPPING.txt and still saves the segments in order."""
import sys, json, os
sys.path.insert(0, "src")
import numpy as np, soundfile as sf
from gate_split import load16k, split
rec, wd = sys.argv[1], sys.argv[2]; os.makedirs(wd + "/audio", exist_ok=True)
script = json.load(open("recording/script.json")); a = load16k(rec); segs = split(a)
meta = []
for k, (s, e) in enumerate(segs):
    n = k + 1; row = script[k] if k < len(script) else None
    sf.write(f"{wd}/audio/g{n:02d}.wav", a[s:e], 16000)
    meta.append({"id": "g%02d" % n, "text": row["text"].lower() if row else None, "truth": row["truth"] if row else None, "kind": row["kind"] if row else "extra", "start_s": round(s/16000, 2), "dur_s": round((e-s)/16000, 2)})
json.dump(meta, open(wd + "/meta.json", "w"), indent=1, ensure_ascii=False)
print(len(segs), "segments found; expected", len(script))
if len(segs) != len(script): open(wd + "/NEEDS_MANUAL_MAPPING.txt", "w").write("segment count %d != %d: listen / check meta.json durations, then fix the mapping by hand\n" % (len(segs), len(script)))
for m in meta: print(m["id"], m["dur_s"], "s", (m["text"] or "")[:60])
