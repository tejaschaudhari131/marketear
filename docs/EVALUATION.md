# Evaluation — measured results only

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
| fp32 | 967 MB (923 MB as safetensors on the Hub) | 25.0% / 9.9% | 11/12 |
| fp16 | 484 MB | 25.0% / 9.9% | 11/12 |
| int8 dynamic (Linear layers) | 413 MB | 25.7% / 10.8% | 11/12 |

Reading: both smaller copies lose at most 0.7 WER points on 30 clips (inside noise at this size). Neither is small by the standard of a basic phone: 413 MB is a laptop-class model. INFERENCE: the 40M-parameter token embedding (shared with the output layer) is stored in full precision in the int8 copy and is the main reason it is not smaller; quantizing it too would shrink it further, but this was NOT tested. UNKNOWN: latency on a phone-class CPU; on this heavily shared 8-core box, free decoding of one clip with one thread took about 5-10 s (fp32 4.8 s, int8 6.6 s, fp16 10.5 s in the logs; these timings reflect load and the fp16 upcast, not phone speed).

## E3. Closed-grammar decoder versus free transcript on synthetic bulletins through the SIMULATED channel (FACT; `eval/run_eval.py`, `results/synth48_w*.jsonl`)
SYNTHETIC speech (facebook/mms-tts-swh, one voice, random speed and pitch). Sentences come from the same grammar as the decoder, so this is optimistic. n per row is 6 to 9 (the run was stopped early).
Cell = crop and exact price both correct, out of n clips.

| channel (SIMULATED FM, CNR) | n | free ASR + fuzzy parser: crop | price exact | crop AND price | closed-grammar decoder: crop | price exact | crop AND price |
|---|---|---|---|---|---|---|---|
| clean audio, no channel | 9 | 9/9 (100%) | 6/9 (67%) | 6/9 (67%) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| 20 dB | 8 | 8/8 (100%) | 6/8 (75%) | 6/8 (75%) | 8/8 (100%) | 8/8 (100%) | 8/8 (100%) |
| 12 dB | 7 | 7/7 (100%) | 5/7 (71%) | 5/7 (71%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) |
| 8 dB | 6 | 6/6 (100%) | 5/6 (83%) | 5/6 (83%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |
| 5 dB | 6 | 6/6 (100%) | 4/6 (67%) | 4/6 (67%) | 6/6 (100%) | 6/6 (100%) | 6/6 (100%) |

## E4. Real human broadcast speech: number recovery (FACT; `eval/real_number_test.py`, `results/real_numbers.jsonl`)
OpenSLR SLR25 RFI Swahili news, test split. 40 sentences, each with exactly one number phrase that our grammar can parse. Closed-number decoder: the words around the number are GIVEN (oracle), the number slot is open to any value below 1,000,000. This is not the full product and not a market bulletin.
| class | channel | n | free recogniser exact | closed-number decoder exact |
|---|---|---|---|---|
| all | clean | 40 | 35 (88%) | 39 (98%) |
| all | SIMULATED FM 12 dB | 40 | 37 (92%) | 39 (98%) |
| single-word numbers (e.g. 'nane') | clean | 23 | 22 (96%) | 23 (100%) |
| single-word numbers (e.g. 'nane') | SIMULATED FM 12 dB | 23 | 23 (100%) | 23 (100%) |
| multi-word numbers (e.g. 'ishirini na saba') | clean | 17 | 13 (76%) | 16 (94%) |
| multi-word numbers (e.g. 'ishirini na saba') | SIMULATED FM 12 dB | 17 | 14 (82%) | 16 (94%) |

## E5. Abstain behaviour (FACT but tuned and tested on the same data; `eval/abstain_eval.py`, `results/abstain_table.md`)
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
Rule used in the demo: margin >= 2.0 and gap >= -25.0 (row 4). It rejected all 6 out-of-vocabulary sentences (coffee and weather news: 2 sentences x 3 channel conditions = 6 clips) and abstained on 1 of 96 in-vocabulary clips, but still accepted 4 wrong in-vocabulary clips (crop confusions). Thresholds were chosen on the same clips, so true error rates are UNKNOWN.

## E6. Gate dry run (FACT; TTS stand-in, NOT the real gate; `results/gate_dryrun_report.md`)
Free transcript plus parser: 9/20 (20 dB), 8/20 (12 dB), 10/20 (8 dB). Closed-grammar decoder: 18/20, 19/20, 18/20. All misses were crop confusions on "maharage" (beans). The real gate on the user's recording is pending: UNKNOWN until `eval/gate_report.py` runs on it.

## E7. WFP reference coverage (FACT; `docs/WFP_COVERAGE.md`, `src/wfp.py`; 24-month window ending 2026-08-15, at least 6 observations)
98 of 144 place x crop x unit combinations in the grammar have no recent WFP reference and are shown as "No reference". Example with a reference: Kisumu maize, 90 kg bag, KES 3,900-5,600 (median 5,200, 19 monthly values, 2024-12 to 2026-07, Kibuye market). Example without: any Tanzanian per-kg price (WFP per-kg series end 2022-12).

## E8. Gate pipeline on a second, different SYNTHETIC VOICE (FACT; NOT the human gate; `eval/make_synth_recording.py`, `eval/gate_synthvoice2_summary.py`, `results/gate_synthvoice2/`)
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

## E9. Dropped-thousands investigation and flagged fix, evaluated on both SYNTHETIC voices and on REAL RFI numbers (FACT; `eval/decode_variants.py`, `eval/decode_variants_report.py`, `eval/elfu_diag.py`, `eval/elfu_fix_summary.py`, `results/elfu/`)
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

## What is NOT evaluated (UNKNOWN)
Real radio audio of any kind carrying a price; a real FM receiver chain; speakers other than two TTS voices, RFI anchors, FLEURS readers and the recorded user; effect on prices farmers receive; latency on phone hardware; the template/acoustic-word-embedding route of arXiv 2306.00410.
