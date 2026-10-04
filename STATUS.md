# STATUS — Market Ear v2 (phase 1 notes, written Sat Oct 3 2026, ET)

## Done in phase 1
- Repo, README, data pulls (sizes and licences in `docs/DATA_TABLE.md`), WFP coverage table for every place x crop x unit in the grammar (`docs/WFP_COVERAGE.md`).
- Closed vocabulary + Swahili number grammar (`src/swnum.py`, `src/grammar.py`); all multiples of 50 below 400,000 round-trip in three phrasing styles. FACT.
- Recogniser: PaschalK/whisper-swahili-small (HF fp32) with decoding restricted to the grammar by a token-level automaton (own beam search, KV cache).
- SIMULATED FM channel (`src/fmchannel.py`), evaluation runner, analysis, gate scripts (`eval/gate_prepare.py`, `eval/gate_report.py`), recording script (`recording/`).
- Pipeline core with receipt and abstain (`src/marketear.py`), WFP lookup (`src/wfp.py`).

## Measured numbers (FACT unless marked)

### 1. Synthetic bulletins through the SIMULATED FM channel (36 clips; first sentences of a seeded set of 48; the run was stopped early to free CPU)
SYNTHETIC speech: facebook/mms-tts-swh (one voice; random speed 0.85-1.15, noise scale, +-10% pitch/speed resample). The sentences are drawn from the same grammar the decoder is restricted to, so this is an easy, optimistic test. Sample sizes per row are small (5-9).

| channel (SIMULATED FM, CNR) | n | free ASR + fuzzy parser: crop | price exact | crop AND price | closed-grammar decoder: crop | price exact | crop AND price |
|---|---|---|---|---|---|---|---|
| clean audio, no channel | 9 | 9/9 (100%) | 6/9 (67%) | 6/9 (67%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| 20 dB | 8 | 8/8 (100%) | 6/8 (75%) | 6/8 (75%) | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) |
| 12 dB | 7 | 7/7 (100%) | 5/7 (71%) | 5/7 (71%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| 8 dB | 6 | 6/6 (100%) | 5/6 (83%) | 5/6 (83%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |
| 5 dB | 6 | 6/6 (100%) | 4/6 (67%) | 4/6 (67%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |

Closed-grammar decoder, place correct, all conditions pooled: 35/36 (97%)

Reading: free transcript + fuzzy parser gets the crop right but loses the exact price in about a quarter to a third of clips; the closed-grammar decoder got crop and price in every clip (CNR 5-clean). INFERENCE: synthetic single-voice speech does not predict human speech; the real-speech test below and the user's recording are the evidence that matters.

### 2. Real human broadcast speech, number recovery (OpenSLR SLR25, RFI Swahili news, test split; one number phrase per sentence)
Columns: number-phrase class | channel | n | free ASR exact number | closed-number decoder, number slot open (any value below 1,000,000), surrounding words GIVEN from the reference (oracle frame).
| class | channel | n | free ASR exact | closed-number decoder exact |
|---|---|---|---|---|
| all | clean | 40 | 35 (88%) | 39 (98%) |
| all | SIMULATED FM 12 dB | 40 | 37 (92%) | 39 (98%) |
| single-word numbers (e.g. 'nane') | clean | 23 | 22 (96%) | 23 (100%) |
| single-word numbers (e.g. 'nane') | SIMULATED FM 12 dB | 23 | 23 (100%) | 23 (100%) |
| multi-word numbers (e.g. 'ishirini na saba') | clean | 17 | 13 (76%) | 16 (94%) |
| multi-word numbers (e.g. 'ishirini na saba') | SIMULATED FM 12 dB | 17 | 14 (82%) | 16 (94%) |

Caveats: oracle frame (the words around the number are given), so this is NOT the full product; n = 40 sentences; many phrases are single words like 'moja' or 'nane' used as ordinary words. The multi-word row is the relevant one for prices and has n = 17 per condition. INFERENCE: constraining the number slot cuts the free recogniser's multi-word number errors on real speech (13 to 16 of 17 clean), but this needs the frame to be right; in a real bulletin the frame is the grammar above.

### 3. Recogniser check (correction of an earlier number)
HF fp32 greedy, FLEURS sw_ke dev, first 30 clips: WER 25.0% CER 9.9%
Earlier run in `/workspace/wb2` used a CTranslate2 int8 conversion (`ct2_sw_small`) and reported 58-68% WER on FLEURS. FACT: the fp32 model gets the first 30 of the same FLEURS clips at the WER above (first-40 vs first-30 subsets differ slightly), roughly 2.5x lower than the int8 copy; on a synthetic clip the int8 copy returned unrelated text. INFERENCE: the int8 conversion (or the way it was fed) lost most of the accuracy, so the earlier 'recogniser is the bottleneck' finding is largely an artefact of that copy; fp32 is 923 MB, not small. All numbers in this repo use fp32. The 240 MB int8 CT2 copy is NOT validated; the fp16 / int8 measurements are in Phase 2 below.

### 4. Dry run of the gate harness (TTS stand-in, NOT the real gate)
22 TTS sentences were concatenated with 2.5-4 s gaps, split at silences (22 of 22 found), and run at 20/12/8 dB.
| condition | free ASR + fuzzy parser | closed-grammar decoder | closed-grammar decoder with abstain (margin >= n/a) |
|---|---|---|---|
| 20 dB | 9/20 | 18/20 | n/a |
| 12 dB | 8/20 | 19/20 | n/a |
| 8 dB | 10/20 | 18/20 | n/a |
GO threshold would be met (19/20 at 12 dB), but this is synthetic speech from the grammar itself. Failures were crop confusions on 'maharage' (decoded as mahindi or mchele). The real gate needs the user's recording.

### 5. Abstain rules (tuned and tested on the SAME 96 in-vocabulary + 6 out-of-vocabulary dry-run/synthetic clips, so optimistic)
margin = log-prob gap between the best decoding and the best alternative with a different crop or price. gap = log-likelihood of the grammar-constrained best minus log-likelihood of the free transcript.
| rule | clips accepted | accepted and correct | accepted and WRONG (in-vocab) | abstain-test sentences accepted (of 6) | in-vocab clips abstained |
|---|---|---|---|---|---|
| margin>=off and gap>=off | 96/96 | 91 | 5 | 6 | 0 |
| margin>=2 and gap>=off | 95/96 | 91 | 4 | 3 | 1 |
| margin>=off and gap>=-25 | 96/96 | 91 | 5 | 0 | 0 |
| margin>=2 and gap>=-25 | 95/96 | 91 | 4 | 0 | 1 |
| margin>=4 and gap>=-25 | 92/96 | 88 | 4 | 0 | 4 |
| margin>=2 and gap>=-20 | 93/96 | 91 | 2 | 0 | 3 |
| margin>=2 and gap>=-30 | 95/96 | 91 | 4 | 1 | 1 |

margins of wrong in-vocab clips: [2.0, 7.3, 12.9, 13.7, 16.6]
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
**SYNTHETIC VOICE stand-in. This is NOT the human gate.** The human gate (Tejas's own recording) has not been run.

Audio: `recording/synthetic_recording.wav`, 22 sentences from `recording/sentences.txt` in order, about 3 s silence between, one continuous 16 kHz mono file (229 s), generated by `eval/make_synth_recording.py`. TTS: `Mwau/waxal_swahili-tts-mms` (VITS, single speaker, fine-tuned from `facebook/mms-tts-swh` on the WAXAL `swa_tts` data; licence CC-BY-NC-4.0, inherited from the MMS base; non-commercial use for test material only). The earlier dry run used `facebook/mms-tts-swh` with random speed/pitch; this run uses different weights and a different voice at default speed. Exact gate pipeline: `eval/gate_prepare.py` (22 of 22 segments found, no manual mapping) -> `eval/run_eval.py` at 20, 12 and 8 dB SIMULATED FM CNR -> `eval/gate_report.py` (`results/gate_synthvoice2/report.md`). The clean-audio row was run afterwards as a diagnostic with the same script (`diag_clean_w*.jsonl`).

Gate rule (set before the run): GO if either route gets crop AND exact price right in at least 16 of 20 at 12 dB. **Result on this synthetic voice: NO-GO** (closed-grammar 11/20, free + parser 0/20 at 12 dB).

| condition | free ASR + fuzzy parser: crop AND price | closed-grammar decoder: crop AND price | closed-grammar, crop AND price AND place | demo abstain rule: accepted / correct / wrong accepted |
|---|---|---|---|---|
| no channel (supplementary diagnostic, not part of the gate) | 2/20 | 13/20 | 12/20 | 14 / 10 / 4 |
| SIMULATED FM 20 dB | 1/20 | 13/20 | 12/20 | 15 / 11 / 4 |
| SIMULATED FM 12 dB (gate condition) | 0/20 | 11/20 | 10/20 | 13 / 8 / 5 |
| SIMULATED FM 8 dB | 1/20 | 10/20 | 10/20 | 13 / 8 / 5 |

The gate counts crop and price only. Place is also shown because the product reports it; g18 (Kampala) came out as Mbeya in all three conditions, which the gate counts as correct.

Abstain tests, sentences 21 (coffee) and 22 (weather news), which are outside the vocabulary: the demo rule (margin >= 2.0 and gap >= -25.0) abstained on 6 of 6 clips.

| sentence | condition | margin | gap | demo rule decision |
|---|---|---|---|---|
| g21 (coffee) | 20 dB | 0.8 | -16.9 | ABSTAIN |
| g21 (coffee) | 12 dB | 1.1 | -27.6 | ABSTAIN |
| g21 (coffee) | 8 dB | 0.2 | -28.0 | ABSTAIN |
| g22 (weather news) | 20 dB | 1.0 | -42.7 | ABSTAIN |
| g22 (weather news) | 12 dB | 3.5 | -45.9 | ABSTAIN |
| g22 (weather news) | 8 dB | 1.6 | -52.1 | ABSTAIN |

Note the margin alone would have accepted g22 at 12 dB (3.5); the likelihood gap is what rejected it. g21 at 20 dB was rejected by the margin (0.8) although its gap (-16.9) was within the threshold.

Failures of the closed-grammar decoder over all 60 gate decodes (26 wrong): 17 where the price came out far smaller than the truth (the thousand word 'elfu' and what precedes it were lost, e.g. 'elfu tatu na mia tano' -> 'ishirini na tatu'; 5 at 20 dB, 6 at 12 dB, 6 at 8 dB), 6 other number-word swaps (e.g. mbili <-> nne in g01), 3 wrong crop (g17 at 12 and 8 dB, g13 at 8 dB). The clean-audio diagnostic also scores only 13/20, so the simulated channel is not the main cause here; the 8 dB row is 3 clips lower than clean.

Sentences that failed in at least one condition (closed-grammar route):

| sentence | truth | closed-grammar output at 20 / 12 / 8 dB | right at 20/12/8 |
|---|---|---|---|
| g01 | maize Kisumu 5200 | maize Kisumu 5400 / maize Kisumu 5400 / maize Kisumu 30 | nnn |
| g08 | beans Arusha 3500 | beans Arusha 23 / beans Arusha 23 / beans Arusha 23 | nnn |
| g10 | maize Morogoro 74000 | maize Morogoro 84 / maize Morogoro 84 / maize Morogoro 34000 | nnn |
| g11 | maize Kakamega 3800 | maize Kakamega 3800 / maize Kakamega 32 / maize Kakamega 23 | Ynn |
| g13 | beans Kisii 9500 | beans Kisii 309 / beans Kisii 309 / maize Mbeya 4 | nnn |
| g15 | maize Gulu 1500 | maize Gulu 1100 / maize Gulu 1100 / maize Mbeya 1100 | nnn |
| g16 | rice Dar es Salaam 2800 | rice Dar es Salaam 80 / rice Dar es Salaam 80 / rice Dar es Salaam 34 | nnn |
| g17 | beans Dodoma 3000 | beans Dodoma 3000 / maize Mbeya 4 / rice Mbeya 2 | Ynn |
| g18 | maize Kampala 1800 | maize Mbeya 1800 / maize Mbeya 1800 / maize Mbeya 32 | YYn |
| g19 | beans Mwanza 250000 | beans Mwanza 23 / beans Mwanza 2 / beans Mwanza 2 | nnn |

Reading (INFERENCE, not verified by listening to the file or testing another model): the free transcripts of this voice are poor even on clean audio (2/20 correct), e.g. g08 'elfu tatu na mia tano' was heard as 'kwa watatu na ni antano', so this voice is much harder for the recogniser than the earlier synthetic voice (18-19/20 closed-grammar). Candidate causes (UNKNOWN which): how this voice pronounces the number words, and the recogniser being fine-tuned on Common Voice read speech; in the failures the decoder chose a shorter number that drops 'elfu'. What this does show (FACT): the 36/36 and 19/20 results on the first synthetic voice do not transfer to a different synthetic voice, so they must not be read as evidence about human speakers. With the demo abstain rule, 5 of the 13 accepted clips at 12 dB still carried a wrong crop or price, so abstaining did not protect against these errors; the human confirm step is what would. The human gate is still required, and the same weakness (lost thousands) is the first thing to check on it.


### Phase 2c: dropped-thousands investigation (written Sat Oct 3 2026, ET; SYNTHETIC audio for A/B, REAL RFI for C)
### Diagnosis (FACT)
Teacher-forced log-likelihood of the TRUTH sentence versus the sentence the baseline beam search returned, voice 2 (WAXAL, SYNTHETIC), 12 dB SIMULATED FM, the 9 clips with a wrong crop or price: the truth scored higher in 3 (g11, g13, g17; these are search errors) and LOWER in 6 (the recogniser itself prefers the wrong, usually shorter, hypothesis; the dropped-thousands cases are in this group). Typical gap: g16 truth -45.1 over 26 tokens vs decoded -33.3 over 18 tokens.

### Variants on cached encoder outputs, all at 12 dB SIMULATED FM (FACT; time-boxed; settings chosen after looking at these same clips, so in-sample)
| variant | A: voice 1 (SYNTHETIC) /20 | B: voice 2 WAXAL (SYNTHETIC) /20 | C: REAL RFI numbers /20 | A+B+C of 60 |
|---|---|---|---|---|
| baseline: beams 4, raw log-lik (what the gate used) | 19/20 | 11/20 | 20/20 | 50 |
| beams 16 (wider beam only) | 19/20 | 11/20 | 20/20 | 50 |
| beams 16 N-best, rerank raw + 0.25 per token | 19/20 | 13/20 | 20/20 | 52 |
| beams 16 N-best, rerank raw + 0.5 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 0.75 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 1.0 per token | 19/20 | 14/20 | 20/20 | 53 |
| beams 16 N-best, rerank raw + 1.5 per token | 19/20 | 16/20 | 20/20 | 55 |
| beams 16 N-best, rerank by log-lik / tokens | 19/20 | 15/20 | 20/20 | 54 |
| grammar REQUIRES a unit, beams 16 | 19/20 | 16/20 | 20/20 | 55 |
| grammar requires unit + rerank +0.25 per token | 19/20 | 16/20 | 20/20 | 55 |
| grammar requires unit + rerank +0.5 per token | 20/20 | 16/20 | 20/20 | 56 |
| grammar requires unit + rerank +0.75 per token | 20/20 | 16/20 | 20/20 | 56 |
| grammar requires unit + rerank +1.0 per token | 20/20 | 16/20 | 20/20 | 56 |

set A: correct hypothesis present in the 16-best list for 20/20 clips
set B: correct hypothesis present in the 16-best list for 18/20 clips

| set | none | pad0.5 | pad1.0 | norm | pad1.0+norm |
|---|---|---|---|---|---|
| B (8 clips, baseline decoder) | 6 | 5 | 6 | 6 | 6 |

- End-to-end re-run of the gate pipeline with the flagged decoder (`MARKETEAR_DECODER=fixed`, `eval/run_eval.py`, 12 dB only), A voice 1 (SYNTHETIC): crop AND exact price 20/20; demo abstain rule: abstained on 2/2 out-of-vocabulary clip(s) (g21/g22); accepted 19 gate clips of which 0 wrong.
- End-to-end re-run of the gate pipeline with the flagged decoder (`MARKETEAR_DECODER=fixed`, `eval/run_eval.py`, 12 dB only), B voice 2 WAXAL (SYNTHETIC): crop AND exact price 16/20; demo abstain rule: abstained on 2/2 out-of-vocabulary clip(s) (g21/g22); accepted 11 gate clips of which 1 wrong.

**Honesty notes for this section.** (1) Set A and B audio are SYNTHETIC speech through a SIMULATED channel; only set C is real human speech and it has an oracle frame and no unit slot, so it only shows the changes do not hurt number recovery (20/20 before and after; there was no room to improve). (2) The per-token weights and the "require a unit" rule were picked after looking at set B (and A), so the after-numbers are in-sample, not a held-out estimate; the human gate is the held-out test. (3) "Require a unit" is a design choice: every gate sentence has a unit, so a bulletin that omits it would be forced into a wrong unit or rejected by the abstain rule; the product would need to treat a missing unit as "ask a person" either way. (4) Only 12 dB was re-run; 20 dB and 8 dB were not. (5) The gate definition (crop AND exact price, at least 16/20 at 12 dB) and the baseline code path are unchanged; the new decoder is behind `MARKETEAR_DECODER=fixed` (`Rec.constrained_decode_fixed`, grammar flag `require_unit`) and the baseline numbers in E3-E8 are still reproducible with the default. (6) Padding (0.5 or 1.0 s of silence) and RMS normalisation before the channel did not help on the clips tested (see table); a beam width of 16 instead of 4 alone changed nothing. (7) What remains wrong on voice 2 after the fix: see the end-to-end line above; the residual errors are mostly number-word swaps (e.g. mbili heard as nne), which no length prior can fix.

