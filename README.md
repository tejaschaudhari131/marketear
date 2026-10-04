# Market Ear v2 — a Swahili FM price listener that says "not sure" instead of guessing

Hack-Nation Ed.7 · World Bank "Small AI for Development" · track 4b Agriculture · built for Tejas Chaudhari (CMU). Referral code for the submission text: WBGSmallAIGADS.

**What it does.** A small offline speech model listens to a Swahili market-price bulletin and may only output sentences from a closed list: three crops (mahindi = maize, maharage = beans, mchele = rice), sixteen market names, six unit phrases, and Swahili numbers (moja ... tisini, mia, elfu, laki). It extracts crop, place, price and unit, puts the price next to the World Food Programme (WFP) reference range for that market, and shows the result to a person. If another crop or price fits the audio almost as well, or a field is missing, or WFP has no recent data, the screen says "not sure, ask a person" and nothing goes out. A person makes the final call. Output reaches the farmer as an SMS or short voice text.

**Honesty rules used everywhere in this repo.**
- FACT = measured here or read from the source. INFERENCE = reasoning. UNKNOWN = not verified.
- Everything with a radio channel in it is a SIMULATION: real or synthetic speech is pushed through a software FM modulator, noise at a stated carrier-to-noise ratio is added, and a software demodulator recovers the audio. The real RTL-SDR clips (0.5 s each) are used only to show that the demodulator runs on real FM IQ; no spoken bulletin exists in them.
- Synthetic (text-to-speech) test speech is labelled SYNTHETIC. The user's recording is labelled "one speaker, scripted".
- Swahili strings have NOT been checked by a native speaker (flag OPEN).

## Status in one paragraph (read this first)

The pipeline runs end to end and the numbers below are reproducible from the stored results, but **the human go/no-go gate has not been run**: no recording of a human speaker exists in this repository, and every test of price sentences used SYNTHETIC (text-to-speech) voices through a SIMULATED FM channel. On the first synthetic voice the closed-grammar decoder read crop and price correctly in 19-20 of 20 clips at 12 dB; on a second, different synthetic voice it managed 11 of 20 (the gate rule, at least 16 of 20, was NOT met: NO-GO on that voice), and a later decoder variant (`MARKETEAR_DECODER=fixed`, tuned on those same clips so the figure is in-sample) reached 16 of 20. Nothing was tested on a real market-price broadcast, a real radio, or a native Swahili speaker's judgement. See `STATUS.md` and `docs/EVALUATION.md` for every table.

## Verification done before publishing (2026-10-04, ET)

- **FACT (re-run):** `python src/swnum.py` (Swahili number grammar self-test): all multiples of 50 in [50, 400000) round-trip in three phrasing styles; 16 of 20,000 random numbers mismatch because of an inherent ambiguity.
- **FACT (re-run):** `python src/grammar.py` (token-level grammar automaton, 7,234 states) accepts and parses its three test sentences.
- **FACT (re-run):** the full pipeline on four SYNTHETIC clips (`MarketEar.listen`, fp32 `PaschalK/whisper-swahili-small`, CPU): Kisumu maize 5,200 per bag and Dar es Salaam rice 2,800 per kg were read and proposed (both match the sentences the clips were generated from), and the two out-of-vocabulary clips (coffee, weather news) were abstained. Four clips is a smoke test, not an evaluation.
- **FACT (re-run):** `python eval/fleurs_hf_wer.py 30` (fp32 recogniser, greedy, first 30 FLEURS `sw_ke` dev clips; needs the FLEURS audio, not included): WER 25.0%, CER 9.9%, matching `docs/EVALUATION.md` E1.
- **FACT (re-run):** `ui/server.py` starts and serves the page and `/samples`.
- **Not re-run:** the evaluation tables in `STATUS.md`/`docs/EVALUATION.md` (they are build-time outputs).

## Layout
| path | what |
|---|---|
| `src/swnum.py` | Swahili number grammar (parse words to integer; say integer as words), round-trip tested |
| `src/grammar.py` | closed vocabulary, sentence grammar, token-level automaton used to constrain the decoder |
| `src/asr.py` | Whisper-small (Swahili fine-tune) + grammar-constrained beam search with KV cache |
| `src/baseline.py` | comparison route: free transcript + fuzzy snapping + parser |
| `src/fmchannel.py` | SIMULATED FM channel (pre-emphasis, FM, noise at a stated CNR, filter, discriminator, de-emphasis) |
| `src/wfp.py` | WFP reference band lookup per market/crop/unit; says "no reference" when data are old or absent |
| `src/marketear.py` | the pipeline: audio to fields to WFP comparison to accept or abstain, with a receipt |
| `src/gate_split.py` | cuts one long phone recording into sentences at the silences |
| `eval/` | sentence generator, synthetic audio, evaluation runner, analysis, gate scripts |
| `recording/` | the 22-sentence script for a human speaker, with instructions (no recordings are included) |
| `docs/DATA_TABLE.md`, `docs/WFP_COVERAGE.md` | datasets and their gaps; WFP coverage for every place x crop x unit in the grammar |
| `results/` | raw per-clip results (jsonl) and generated tables |
| `ui/` | one-screen demo (FastAPI + one HTML page); example clips are not shipped (licence), see `ui/samples/README.md` |
| `docs/EVALUATION.md`, `docs/RESPONSIBLE_AI.md`, `docs/VIDEO_SCRIPT.md` | measured results only; pass/fail Responsible AI items; 2-5 minute video script |
| `STATUS.md` | progress notes with the measured numbers |

## Run the demo
1. Python 3.10+ (built and run on 3.13), `pip install -r requirements.txt`, and `ffmpeg` on the PATH.
2. `cd ui && python server.py 8765`, then open http://localhost:8765 (binds to 127.0.0.1; set `HOST=0.0.0.0` to expose it). The recogniser `PaschalK/whisper-swahili-small` (Apache-2.0, 923 MB) downloads from Hugging Face on first use; it is not stored in this repo.
3. Record or upload a short Swahili bulletin sentence, (the SYNTHETIC example-clip buttons are empty in this repo, see `ui/samples/README.md`). Choose "none" for the audio as given, or a SIMULATED FM channel (a yellow banner then says so). The screen shows the transcript, the extracted crop, market, price and unit, the WFP range, and either a draft Swahili/English message to confirm or "not sure, ask a person". Nothing is sent anywhere.

Model size (measured, `docs/EVALUATION.md` E2): fp32 967 MB, fp16 weights 484 MB, torch dynamic int8 413 MB; on 30 FLEURS clips WER 25.0%, 25.0%, 25.7%. Phone latency is UNKNOWN.

## Licences and attribution

- Code and original text in this repository: MIT (`LICENSE`).
- `data/wfp_*.csv`: WFP Food Prices for Kenya, Tanzania and Uganda via the Humanitarian Data Exchange, **CC BY-IGO** (attribution: World Food Programme, https://data.humdata.org). Retrieved 2026-10-03.
- `data/fleurs_sw_dev.tsv`: transcripts from Google FLEURS (`sw_ke`, dev), **CC BY 4.0**. The audio is not included.
- Recogniser (not included, downloaded on first use): `PaschalK/whisper-swahili-small`, Apache-2.0.
- Not included on purpose: all WAV files (they are synthetic speech from `facebook/mms-tts-swh` / `Mwau/waxal_swahili-tts-mms`, both CC BY-NC 4.0, plus any human recording), OpenSLR SLR25 audio (MIT), FLEURS audio, RTL-ML FM captures (MIT). `eval/` scripts that need them say where to download them from `docs/DATA_TABLE.md`.
- Some scripts in `eval/` and `src/` were written for the original build box and mention `/workspace/...` paths (`eval/build_status.py`, `eval/build_eval_md.py`); adjust them before use.
