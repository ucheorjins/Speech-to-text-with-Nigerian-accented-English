# Speech-to-text with Nigerian-accented English: a quick sanity check

**Question:** Before running a study on speaking vs typing prompts to generative AI, how well do two common speech recognisers handle Nigerian-accented English on short UI-editing instructions?

**Engines compared**
- Chrome's built-in Web Speech API (language setting: `[en-US / en-NG]`)
- OpenAI Whisper `[small.en]`, run locally

**What I did**
- [N] speakers (Nigerian English, [ages / mix of regions or first languages, if they're OK sharing that]) each read the same 10 short instructions, the kind you'd give an AI to edit a web page (list below).
- Each reading was recorded once. Chrome transcribed it live; Whisper transcribed the saved audio afterwards.
- I scored both with word error rate (WER) against the script, after lowercasing and removing punctuation.

## Results

[paste the table from results/summary.md here]

**What stood out**
- [e.g. "Chrome got 'header' as 'had a' for 3 of 4 speakers"]
- [e.g. "Whisper was better on product words like 'leaderboard' but added words on short clips"]
- [one line on what this means for the bigger study]

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

## Limitations
- Small sample, read speech in a quiet room. Real prompting is spontaneous and messier.
- Speakers read a script, so this measures recognition, not how people naturally phrase requests.
- Chrome's recogniser is a cloud service that can change without notice.

## Privacy
Speakers agreed to take part and are labelled S1, S2… only. Audio is not published; only text transcripts are.

## Files
- `recorder.html`: records each instruction and captures Chrome's transcript
- `analyze.py`: runs Whisper and scores both engines
- `results/per_utterance.csv`, `results/summary.md`: the output

---

## How to run it yourself

**Once:** install Python 3.10+ and ffmpeg, then:
```
pip install -U openai-whisper jiwer
```

**Record** (Chrome, with internet):
```
python -m http.server 8000
```
Open http://localhost:8000/recorder.html, set the Speaker ID, then Record and Stop for each instruction. Click **Download results (JSON)** at the end.

**Arrange the files:**
```
data/browser_*.json
data/audio/*.webm
```

**Analyse:**
```
python analyze.py
```
On a slow laptop:
```
WHISPER_MODEL=base.en python analyze.py
```
On Windows PowerShell:
```
$env:WHISPER_MODEL="base.en"; python analyze.py
```
