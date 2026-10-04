# Example clips

The five SYNTHETIC example clips used in the original demo (g01, x1, g16, g21, g22) were generated with Meta MMS-TTS Swahili
(`facebook/mms-tts-swh`, CC BY-NC 4.0) and are NOT included here because of that non-commercial licence.
`samples.json` is therefore an empty list and the UI shows no example buttons: record or upload your own clip.
To regenerate them for non-commercial testing: `python src/tts_synth.py <sentences.json> <outdir>` (see the header of that script), then list the files in `samples.json`.
