import subprocess, re
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
synth = sh("/workspace/wb2/v/bin/python eval/analyze.py 'results/synth48_w*.jsonl' | sed -n 1,9p")
nsyn = sh("cat results/synth48_w*.jsonl | wc -l")
real = sh("/workspace/wb2/v/bin/python eval/real_number_report.py")
ab = open("results/abstain_table.md").read().strip()
SV2 = open("results/gate_synthvoice2_summary.md").read()
ELFU = open("results/elfu/summary.md").read() + open("results/elfu/notes.md").read()
dry = sh("sed -n 5,10p eval/gate_dryrun/report.md")
fl = sh("grep 'HF fp32' logs/fleurs_hf.log")
open("STATUS.md", "w").write(f"""# STATUS — Market Ear v2 (phase 1 notes, written Sat Oct 3 2026, ET)

## Done in phase 1
- Repo, README, data pulls (sizes and licences in `docs/DATA_TABLE.md`), WFP coverage table for every place x crop x unit in the grammar (`docs/WFP_COVERAGE.md`).
- Closed vocabulary + Swahili number grammar (`src/swnum.py`, `src/grammar.py`); all multiples of 50 below 400,000 round-trip in three phrasing styles. FACT.
- Recogniser: PaschalK/whisper-swahili-small (HF fp32) with decoding restricted to the grammar by a token-level automaton (own beam search, KV cache).
- SIMULATED FM channel (`src/fmchannel.py`), evaluation runner, analysis, gate scripts (`eval/gate_prepare.py`, `eval/gate_report.py`), recording script (`recording/`).
- Pipeline core with receipt and abstain (`src/marketear.py`), WFP lookup (`src/wfp.py`).

## Measured numbers (FACT unless marked)

### 1. Synthetic bulletins through the SIMULATED FM channel ({nsyn} clips; first sentences of a seeded set of 48; the run was stopped early to free CPU)
SYNTHETIC speech: facebook/mms-tts-swh (one voice; random speed 0.85-1.15, noise scale, +-10% pitch/speed resample). The sentences are drawn from the same grammar the decoder is restricted to, so this is an easy, optimistic test. Sample sizes per row are small (5-9).

{synth}

Reading: free transcript + fuzzy parser gets the crop right but loses the exact price in about a quarter to a third of clips; the closed-grammar decoder got crop and price in every clip (CNR 5-clean). INFERENCE: synthetic single-voice speech does not predict human speech; the real-speech test below and the user's recording are the evidence that matters.

### 2. Real human broadcast speech, number recovery (OpenSLR SLR25, RFI Swahili news, test split; one number phrase per sentence)
Columns: number-phrase class | channel | n | free ASR exact number | closed-number decoder, number slot open (any value below 1,000,000), surrounding words GIVEN from the reference (oracle frame).
| class | channel | n | free ASR exact | closed-number decoder exact |
|---|---|---|---|---|
{real}

Caveats: oracle frame (the words around the number are given), so this is NOT the full product; n = 40 sentences; many phrases are single words like 'moja' or 'nane' used as ordinary words. The multi-word row is the relevant one for prices and has n = 17 per condition. INFERENCE: constraining the number slot cuts the free recogniser's multi-word number errors on real speech (13 to 16 of 17 clean), but this needs the frame to be right; in a real bulletin the frame is the grammar above.

### 3. Recogniser check (correction of an earlier number)
{fl}
Earlier run in `/workspace/wb2` used a CTranslate2 int8 conversion (`ct2_sw_small`) and reported 58-68% WER on FLEURS. FACT: the fp32 model gets the first 30 of the same FLEURS clips at the WER above (first-40 vs first-30 subsets differ slightly), roughly 2.5x lower than the int8 copy; on a synthetic clip the int8 copy returned unrelated text. INFERENCE: the int8 conversion (or the way it was fed) lost most of the accuracy, so the earlier 'recogniser is the bottleneck' finding is largely an artefact of that copy; fp32 is 923 MB, not small. All numbers in this repo use fp32. The 240 MB int8 CT2 copy is NOT validated; the fp16 / int8 measurements are in Phase 2 below.

### 4. Dry run of the gate harness (TTS stand-in, NOT the real gate)
22 TTS sentences were concatenated with 2.5-4 s gaps, split at silences (22 of 22 found), and run at 20/12/8 dB.
{dry}
GO threshold would be met (19/20 at 12 dB), but this is synthetic speech from the grammar itself. Failures were crop confusions on 'maharage' (decoded as mahindi or mchele). The real gate needs the user's recording.

### 5. Abstain rules (tuned and tested on the SAME 96 in-vocabulary + 6 out-of-vocabulary dry-run/synthetic clips, so optimistic)
margin = log-prob gap between the best decoding and the best alternative with a different crop or price. gap = log-likelihood of the grammar-constrained best minus log-likelihood of the free transcript.
{ab}
Reading: the margin alone never caught a wrong crop (wrong clips had margins 2.0-16.6) and let coffee/weather sentences through; the likelihood gap (>= -25) rejected all six out-of-vocabulary tests with no in-vocabulary clip lost. 6 out-of-vocabulary clips is too few to trust the threshold. Wrong-crop errors still need the human confirm step.

## Not done / open
- Real recordings from the user (gate) pending. Gate rule: GO if either route has crop AND exact price right in >=16/20 at 12 dB.
- No real Swahili market-price bulletin audio exists in open data (UNKNOWN beyond that). Nothing here was tested on real radio.
- Swahili text (script, SMS, 'not sure' phrase) not checked by a native speaker. OPEN.
- The acoustic-word-embedding/template route of arXiv 2306.00410 was NOT implemented; ours is grammar-constrained decoding of a fine-tuned recogniser. That paper (hate-speech keywords) reports in-the-wild Swahili radio keyword precision of 45% (top-100, AWE with one minute of templates) vs 52% for a 30-hour ASR, so even good keyword spotting is far from perfect on real radio. FACT, from the abstract/Table 4.
- Contention: the box is shared (load ~20 on 8 cores); 1 thread per process was 3x faster than 4. A gate run of 22 segments at 3 channel conditions (66 decodes) over 3 workers took roughly 10 min in the dry run.
- Correction to the brief: Eldoret has maize (white, dry) 90 KG rows to 2025-06-15 and rosecoco beans to 2025-06; none since Sep 2025. Tanzania has full recent coverage (30 markets) but only per-100 KG wholesale; per-KG series stop 2022-12.

## Phase 2 (written Sat Oct 3 2026, ET)

### Demo UI (built, tested end-to-end through the server on synthetic clips)
- Run: `cd ui && /workspace/wb2/v/bin/python server.py 8765` then open http://localhost:8765 (the model, 923 MB, downloads on first use). There is no browser on the build box, so recording the demo video needs a machine with a browser and the model, or a tunnel to the box.
- One screen: record or upload audio (or press a SYNTHETIC example), pick channel (none or SIMULATED FM 20/12/8/5 dB; a yellow SIMULATION banner shows when used), see decoded text, free transcript, crop/market/price/unit, WFP range and verdict, margin and gap, and the draft message in Swahili and English. When the system abstains, extracted fields are withheld and the reason is shown. Confirm/Reject buttons only; nothing is sent anywhere. Uploaded audio is deleted after each request.
- Tested at 12 dB: g01 Kisumu maize 5,200 -> proposed, within range; x1 7,200 -> above range; g16 Dar rice per kg -> proposed with "No reference"; g21 coffee -> abstained (gap -34.0). Raw receipts: `results/ui_test_*.json`.

### Model size vs accuracy (FACT, `docs/EVALUATION.md` E2)
| copy | size (torch.save) | FLEURS first 30 WER / CER | synthetic clean crop+price, 12 sentences |
|---|---|---|---|
| fp32 | 967 MB (923 MB safetensors) | 25.0% / 9.9% | 11/12 |
| fp16 weights | 484 MB | 25.0% / 9.9% | 11/12 |
| int8 dynamic (Linear) | 413 MB | 25.7% / 10.8% | 11/12 |
Accuracy loss at this sample size is within noise. 413 MB is not phone-small; phone latency is UNKNOWN. Quantising the token embedding too is untested.

### Documents
`docs/EVALUATION.md` (generated by `eval/build_eval_md.py`, measured results only), `docs/RESPONSIBLE_AI.md` (14 pass/fail items), `docs/DATA_TABLE.md`, `docs/VIDEO_SCRIPT.md`, `docs/SUBMISSION_CHECKLIST.md` (includes paste-ready text with WBGSmallAIGADS).

### Still open after phase 2
- The real gate has NOT been run; it waits for the user's recording. Commands: `eval/gate_prepare.py <file> <workdir>`, then `eval/run_eval.py <workdir>/meta.json <workdir>/audio <workdir>/results_wN.jsonl N 3 20,12,8` for N = 0,1,2 in parallel, then `eval/gate_report.py`.
- Abstain statement: the demo rule rejected 6/6 out-of-vocabulary clips but still accepts some wrong crops (4 of 96 in-vocabulary clips); human confirm is required.
- Repo link, video link, HackOS and Google Form links: UNKNOWN / to be added by the user; the repo must be pushed without the model weights.

### Phase 2b: gate pipeline on a second SYNTHETIC VOICE (written Sat Oct 3 2026, ET; NOT the human gate)
{SV2}

### Phase 2c: dropped-thousands investigation (written Sat Oct 3 2026, ET; SYNTHETIC audio for A/B, REAL RFI for C)
{ELFU}
""")
