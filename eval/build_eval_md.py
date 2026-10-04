import subprocess
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
synth = sh("/workspace/wb2/v/bin/python eval/analyze.py 'results/synth48_w*.jsonl' | sed -n 1,7p")
real = sh("/workspace/wb2/v/bin/python eval/real_number_report.py")
q32 = sh("grep 'SYNTHETIC clean' logs/quant_fp32.log")
SV2 = open("results/gate_synthvoice2_summary.md").read()
ELFU = open("results/elfu/summary.md").read() + open("results/elfu/notes.md").read()
open("docs/EVALUATION.md", "w").write(f"""# Evaluation — measured results only

Label key: FACT = measured in this repo on the stated data (script and raw file given). INFERENCE = reasoning. UNKNOWN = not measured.
Everything involving a radio channel is SIMULATED (`src/fmchannel.py`: pre-/de-emphasis 50 us, FM at 75 kHz deviation, complex Gaussian noise at a nominal CNR in a 200 kHz channel, channel filter, discriminator; mono; no multipath, fading, stereo or RDS). Real reception is harder (INFERENCE).
Sample sizes are small. Intervals are not computed; treat differences of one or two clips as noise.

## E1. Recogniser accuracy and the correction to earlier numbers (FACT; `eval/fleurs_hf_wer.py`, `eval/quant_test.py`)
| model copy | size on disk | FLEURS sw_ke dev, first 30 clips, free greedy decoding: WER / CER |
|---|---|---|
| PaschalK/whisper-swahili-small, fp32 (used for all results below) | 923 MB | 25.0% / 9.9% |
| CTranslate2 int8 copy built earlier on this box (`/workspace/wb2/ct2_sw_small`) | 240 MB | 58.4% and 67.7% in two earlier runs on the first 40 clips (earlier STATUS/ideation notes) |

Correction: the 58-68% WER quoted in the earlier notes was measured on the CT2 int8 copy, not on the fp32 model. The same model at fp32 gets 25.0% on 30 of the same clips (the first-40 and first-30 subsets differ slightly). The CT2 copy also returned unrelated text on a synthetic clip. INFERENCE: the conversion or the way it was fed lost most of the accuracy; we did not diagnose which. Consequence: the statement "the recogniser is the bottleneck" from the earlier notes is largely an artefact; the CT2 copy is not used anywhere in this repo.

## E2. Model size versus accuracy (FACT; `eval/quant_test.py`, logs in `logs/quant_*.log`)
fp16 = weights stored as half precision and upcast to fp32 for compute on this CPU (accuracy is that of fp16 weights; speed on this box is not representative). int8 = `torch.ao.quantization.quantize_dynamic` on all Linear layers. Size = bytes of `torch.save(state_dict)` (shared tensors counted once).
| copy | size | FLEURS first 30: WER / CER | synthetic clean, closed-grammar crop and price (first 12 sentences) |
|---|---|---|---|
| fp32 | 967 MB (923 MB as safetensors on the Hub) | 25.0% / 9.9% | {q32.split(': ')[-1] if q32 else 'not run'} |
| fp16 | 484 MB | 25.0% / 9.9% | 11/12 |
| int8 dynamic (Linear layers) | 413 MB | 25.7% / 10.8% | 11/12 |

Reading: both smaller copies lose at most 0.7 WER points on 30 clips (inside noise at this size). Neither is small by the standard of a basic phone: 413 MB is a laptop-class model. INFERENCE: the 40M-parameter token embedding (shared with the output layer) is stored in full precision in the int8 copy and is the main reason it is not smaller; quantizing it too would shrink it further, but this was NOT tested. UNKNOWN: latency on a phone-class CPU; on this heavily shared 8-core box, free decoding of one clip with one thread took about 5-10 s (fp32 4.8 s, int8 6.6 s, fp16 10.5 s in the logs; these timings reflect load and the fp16 upcast, not phone speed).

## E3. Closed-grammar decoder versus free transcript on synthetic bulletins through the SIMULATED channel (FACT; `eval/run_eval.py`, `results/synth48_w*.jsonl`)
SYNTHETIC speech (facebook/mms-tts-swh, one voice, random speed and pitch). Sentences come from the same grammar as the decoder, so this is optimistic. n per row is 6 to 9 (the run was stopped early).
Cell = crop and exact price both correct, out of n clips.

{synth}

## E4. Real human broadcast speech: number recovery (FACT; `eval/real_number_test.py`, `results/real_numbers.jsonl`)
OpenSLR SLR25 RFI Swahili news, test split. 40 sentences, each with exactly one number phrase that our grammar can parse. Closed-number decoder: the words around the number are GIVEN (oracle), the number slot is open to any value below 1,000,000. This is not the full product and not a market bulletin.
| class | channel | n | free recogniser exact | closed-number decoder exact |
|---|---|---|---|---|
{real}

## E5. Abstain behaviour (FACT but tuned and tested on the same data; `eval/abstain_eval.py`, `results/abstain_table.md`)
{open('results/abstain_table.md').read().strip()}
Rule used in the demo: margin >= 2.0 and gap >= -25.0 (row 4). It rejected all 6 out-of-vocabulary sentences (coffee and weather news: 2 sentences x 3 channel conditions = 6 clips) and abstained on 1 of 96 in-vocabulary clips, but still accepted 4 wrong in-vocabulary clips (crop confusions). Thresholds were chosen on the same clips, so true error rates are UNKNOWN.

## E6. Gate dry run (FACT; TTS stand-in, NOT the real gate; `results/gate_dryrun_report.md`)
Free transcript plus parser: 9/20 (20 dB), 8/20 (12 dB), 10/20 (8 dB). Closed-grammar decoder: 18/20, 19/20, 18/20. All misses were crop confusions on "maharage" (beans). The real gate on the user's recording is pending: UNKNOWN until `eval/gate_report.py` runs on it.

## E7. WFP reference coverage (FACT; `docs/WFP_COVERAGE.md`, `src/wfp.py`; 24-month window ending 2026-08-15, at least 6 observations)
{sh("grep -c 'NO REFERENCE' docs/WFP_COVERAGE.md")} of {sh("grep -c '^| [A-Z]' docs/WFP_COVERAGE.md")} place x crop x unit combinations in the grammar have no recent WFP reference and are shown as "No reference". Example with a reference: Kisumu maize, 90 kg bag, KES 3,900-5,600 (median 5,200, 19 monthly values, 2024-12 to 2026-07, Kibuye market). Example without: any Tanzanian per-kg price (WFP per-kg series end 2022-12).

## E8. Gate pipeline on a second, different SYNTHETIC VOICE (FACT; NOT the human gate; `eval/make_synth_recording.py`, `eval/gate_synthvoice2_summary.py`, `results/gate_synthvoice2/`)
{SV2}
## E9. Dropped-thousands investigation and flagged fix, evaluated on both SYNTHETIC voices and on REAL RFI numbers (FACT; `eval/decode_variants.py`, `eval/decode_variants_report.py`, `eval/elfu_diag.py`, `eval/elfu_fix_summary.py`, `results/elfu/`)
{ELFU}
## What is NOT evaluated (UNKNOWN)
Real radio audio of any kind carrying a price; a real FM receiver chain; speakers other than two TTS voices, RFI anchors, FLEURS readers and the recorded user; effect on prices farmers receive; latency on phone hardware; the template/acoustic-word-embedding route of arXiv 2306.00410.
""")
