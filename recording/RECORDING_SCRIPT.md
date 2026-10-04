# Market Ear v2 — recording script for the go/no-go gate (22 sentences, about 3 minutes)

**Status of the Swahili text: NOT checked by a native speaker (native-speaker check flag = OPEN).** Every sentence was written by the build agent from the number grammar in `src/swnum.py`; the spelling and number words follow standard Swahili, but nobody fluent has confirmed them. If anyone at the hackathon speaks Swahili, ask them to glance at this page (2 minutes) or, better, to record the sentences instead of you.

## What you do (about 10 minutes)

1. Find a quiet room. Close the door, switch off fans and music. Hold the phone about a hand-span (15 cm) from your mouth.
2. Open the voice recorder app (iPhone: Voice Memos; Android: Recorder or Voice Recorder). Record **one single file** for all 22 sentences.
3. Read the sentences below **in order, one after another**, like a radio announcer: calm, clear, not rushed. **Leave a silent gap of about 3 seconds between sentences** (count 'one-two-three' in your head). Do not say the sentence number out loud.
4. If you stumble: stay silent for 5 seconds, then read that same sentence again from the start. Keep going. Do not stop the recording.
5. Say the numbers as words exactly as written (e.g. 'elfu tano na mia mbili'). Swahili is spelled the way it sounds: say every letter; stress the second-to-last syllable of a word; 'mb', 'nd', 'ng' at the start of a word are said as one quick sound.
6. Stop the recording. Save it. Name it `marketear_gate.m4a` (or leave the default name).

## How to send the file

Any one of these works; tell the agent which one you used:
- **Easiest:** drop the audio file straight into the chat as an attachment (it lands in `/workspace/uploads`).
- Or save it on your MSI laptop (for example in Downloads) and tell the agent the file name; the agent copies it from there.
- iPhone: Voice Memos → share → AirDrop/email to yourself → save on the laptop. Android: Recorder → share → Drive/email/USB.
Formats m4a, mp3, wav, ogg, and amr all work. Do not edit, trim, or filter it.

## Pronunciation hints (a non-native reader is fine; this is also a useful accent test and the report will say so)
- a = 'ah', e = 'eh', i = 'ee', o = 'oh', u = 'oo'. Every vowel is said separately.
- 'mahindi' = ma-HEEN-dee; 'maharage' = ma-ha-RA-geh; 'mchele' = m-CHEH-leh; 'shilingi' = shee-LEEN-gee; 'elfu' = EL-foo; 'mia' = MEE-ah; 'laki' = LAH-kee; 'gunia' = goo-NEE-ah; 'kilo' = KEE-lo.
- 'th' (as in 'thelathini', 'themanini') is a soft 'th' like in English 'think'.

## The sentences — read these in order

| # | Read this aloud | What the system should hear (answer key, hidden from the recognizer) |
|---|---|---|
| 1 | Bei ya mahindi Kisumu leo ni shilingi elfu tano na mia mbili kwa gunia. | maize, Kisumu, 5,200, unit BAG |
| 2 | Bei ya maharage Nakuru ni shilingi elfu kumi na mbili kwa gunia. | beans, Nakuru, 12,000, unit BAG |
| 3 | Bei ya mchele Nairobi ni shilingi mia moja na sitini kwa kilo. | rice, Nairobi, 160, unit KG |
| 4 | Mahindi Eldoret ni shilingi elfu nne na mia tano kwa gunia la kilo tisini. | maize, Eldoret, 4,500, unit 90 KG |
| 5 | Bei ya maharage Kitale leo ni shilingi mia mbili na ishirini kwa kilo. | beans, Kitale, 220, unit KG |
| 6 | Bei ya mahindi Dodoma ni shilingi elfu moja na mia mbili kwa kilo. | maize, Dodoma, 1,200, unit KG |
| 7 | Bei ya mchele Mwanza ni shilingi elfu mbili na mia tisa kwa kilo. | rice, Mwanza, 2,900, unit KG |
| 8 | Bei ya maharage Arusha ni shilingi elfu tatu na mia tano kwa kilo. | beans, Arusha, 3,500, unit KG |
| 9 | Mbeya leo bei ya mahindi ni shilingi elfu themanini na tano kwa gunia la kilo mia moja. | maize, Mbeya, 85,000, unit 100 KG |
| 10 | Bei ya mahindi Morogoro ni shilingi elfu sabini na nne kwa gunia la kilo mia moja. | maize, Morogoro, 74,000, unit 100 KG |
| 11 | Bei ya mahindi Kakamega ni shilingi elfu tatu na mia nane kwa gunia. | maize, Kakamega, 3,800, unit BAG |
| 12 | Bei ya mchele Mombasa ni shilingi mia moja na tisini kwa kilo. | rice, Mombasa, 190, unit KG |
| 13 | Bei ya maharage Kisii ni shilingi elfu tisa na mia tano kwa gunia. | beans, Kisii, 9,500, unit BAG |
| 14 | Kisumu bei ya mahindi ni shilingi elfu tano na mia tatu kwa gunia. | maize, Kisumu, 5,300, unit BAG |
| 15 | Bei ya mahindi Gulu ni shilingi elfu moja na mia tano kwa kilo. | maize, Gulu, 1,500, unit KG |
| 16 | Bei ya mchele Dar es Salaam ni shilingi elfu mbili na mia nane kwa kilo. | rice, Dar es Salaam, 2,800, unit KG |
| 17 | Bei ya maharage Dodoma ni shilingi elfu tatu kwa kilo. | beans, Dodoma, 3,000, unit KG |
| 18 | Bei ya mahindi Kampala ni shilingi elfu moja na mia nane kwa kilo. | maize, Kampala, 1,800, unit KG |
| 19 | Bei ya maharage Mwanza ni shilingi laki mbili na elfu hamsini kwa gunia la kilo mia moja. | beans, Mwanza, 250,000, unit 100 KG |
| 20 | Bei ya mahindi Nakuru ni shilingi elfu sita na mia saba na hamsini kwa gunia. | maize, Nakuru, 6,750, unit BAG |
| 21 | Bei ya kahawa Nakuru ni shilingi elfu mbili kwa kilo. | ABSTAIN TEST — coffee is outside the closed vocabulary -> must abstain |
| 22 | Habari za leo, mvua kubwa imenyesha Kisumu usiku wa jana. | ABSTAIN TEST — weather news, no price -> must abstain |

Sentences 1-20 count for the go/no-go gate. Sentences 21 and 22 are on purpose outside the system's vocabulary: they test that it says 'not sure, ask a person' instead of guessing. Read them in the same calm voice.

## What happens to your recording
It stays on the build box. The agent cuts it into the 22 sentences at the silences, pushes each one through a **simulated** FM radio channel at three signal strengths (20, 12 and 8 dB carrier-to-noise), and checks whether the crop and the exact price come back right. Gate rule: GO if at least 16 of the 20 sentences give the right crop AND the exact price at 12 dB. The recording is your voice, read from a script, in a quiet room: it is a controlled test, not proof that the system works on a real radio station. The report will say so.
