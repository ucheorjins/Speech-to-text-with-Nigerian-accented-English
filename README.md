# Speech-to-text with Nigerian-accented English: a pilot

This pilot is a first step towards a larger study of speech input for generative AI. It asks how accurately two widely available automatic speech recognition (ASR) systems transcribe Nigerian-accented English when people speak short instructions for editing a web page.

## Method

**Participants.** Three speakers of Nigerian English, from two ethnic groups (Igbo and Ukwani), took part. Each is identified by a code name only (S1-Potato, S2-Prime, S3-Zenin).

**Materials.** Every participant read the same 10 short instructions, of the kind a user might give a generative AI system to modify a web page (listed below). This produced 30 recordings with 234 reference words in total.

**Systems.**

- The Web Speech API built into Google Chrome, with the recognition language set to `en-NG`. It transcribed each utterance live as it was spoken.
- OpenAI Whisper (`small.en`), run locally. It transcribed the saved recording of each utterance afterwards.

**Measure.** I scored both systems by word error rate (WER): substitutions, deletions and insertions divided by the number of words in the reference. Lower values indicate better performance. Before scoring, I converted all text to lower case and removed punctuation.

## Results

| Speaker | Chrome WER | Whisper WER |
|---|---:|---:|
| S1-Potato | 5.1% | 7.7% |
| S2-Prime | 3.8% | 12.8% |
| S3-Zenin | 6.4% | 28.2% |
| **All (30 recordings)** | **5.1%** | **16.2%** |

Chrome produced a perfect transcript for 18 of the 30 recordings and Whisper for 16.

- **Overall accuracy.** Chrome was more accurate overall, with about one word in 20 transcribed incorrectly, compared with about one in 6 for Whisper.
- **Variation between speakers.** Whisper's accuracy varied considerably by speaker, from 7.7% to 28.2% WER. Chrome's stayed between 3.8% and 6.4%.
- **Severity of errors.** WER alone does not show which errors matter. Some do not affect the meaning of the instruction ("accent" for "accents"). Others change the requested edit entirely. For example, Chrome transcribed "bolder" as "border" or "boulder" for all three speakers, and "border" is itself a valid design instruction.

### Examples

| Spoken | Chrome transcribed | Whisper transcribed |
|---|---|---|
| …something **bolder** | "something border" (S2-Prime, S3-Zenin); "something boulder" (S1-Potato) | correct (S1-Potato, S2-Prime); "buddha" (S3-Zenin) |
| Move the **sign-up** button… | correct for all three | "side knob button" (S1-Potato, S2-Prime) |
| Put the **leaderboard** table… | correct for all three | "little ball table" (S1-Potato); "lid above the wind" (S3-Zenin) |
| …join the **league** | correct for all three | "join the leak" (S1-Potato); "join delete" (S2-Prime) |
| …background **dark blue** | "black blue" (S3-Zenin) | "but I blew" (S3-Zenin) |

Full transcripts for every recording are in `results/summary.md`.

## Limitations

- The sample of three speakers from two ethnic groups (Igbo and Ukwani) is very small, and it has no comparison accent. These results are exploratory and should not be read as a finding.
- Participants read a script in a quiet room. Real prompting is spontaneous and likely to be less fluent.
- The two systems did not receive identical input: Chrome transcribed live audio, while Whisper transcribed the saved recordings. I also tested only one Whisper model size, and larger models may perform better.
- Chrome's recogniser is a cloud service, so its behaviour may change without notice.

## Implications and future work

These results suggest that speech input is viable for Nigerian-accented English, but accuracy depends on both the recognition system and the speaker. They also show that the error count alone is not enough. What matters is whether an error changes the action the AI system takes.

Next, I will extend the pilot to about 12 speakers from Yoruba, Igbo and Hausa backgrounds, and classify which errors change the meaning of an instruction. Longer term, I plan to:

- compare Nigerian and North American English on real generative AI prompts
- examine how recognition errors change the way people prompt
- evaluate interface interventions, such as asking users to confirm uncertain words before the AI acts

## The 10 instructions

1. Make the header background dark blue.
2. Move the sign-up button to the top right corner.
3. Change the font of the title to something bolder.
4. Add a search bar under the navigation menu.
5. Make the profile picture round and a bit smaller.
6. Replace Submit with Join the league.
7. Add more space between the three cards.
8. Change the green accents to orange.
9. Put the leaderboard table in a card with a shadow.
10. Make the whole layout work on mobile.

## Ethics and data

All participants gave consent to take part and to share their recordings. They are identified by code names only. This repository includes the audio recordings, the browser transcripts and the scored results.

## Repository contents

- `recorder.html`: presents each instruction, records the audio and captures Chrome's transcript
- `analyze.py`: transcribes the recordings with Whisper and scores both systems
- `data/`: the browser transcripts (`browser_*.json`) and audio recordings (`audio/*.webm`)
- `results/per_utterance.csv`, `results/summary.md`: WER for each recording and summary tables

## Contact

uchechukwuekpendu@gmail.com

---

## Reproducing the analysis

**Setup (once).** Install Python 3.10+ and ffmpeg, then run:

```
pip install -U openai-whisper jiwer
```

**Recording** (Chrome, with an internet connection). Start a local server:

```
python -m http.server 8000
```

Open http://localhost:8000/recorder.html and set the Speaker ID. For each instruction, select **Record** and then **Stop**. When you have finished, select **Download results (JSON)**.

**File layout.** Place the files as follows:

```
data/browser_*.json
data/audio/*.webm
```

**Analysis.** Run:

```
python analyze.py
```

On a less powerful computer, use a smaller Whisper model:

```
WHISPER_MODEL=base.en python analyze.py
```

On Windows PowerShell:

```
$env:WHISPER_MODEL="base.en"; python analyze.py
```
