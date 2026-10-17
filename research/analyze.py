"""
ASR pilot: compare the browser's speech-to-text with Whisper
on the same recordings, using word error rate (WER).

Folder layout expected:
  data/
    browser_S1.json, browser_S2.json, ...   (from recorder.html)
    audio/S1_01_take1.webm, ...             (from recorder.html)

Setup (once):
  pip install -U openai-whisper jiwer
  and install ffmpeg (see https://github.com/openai/whisper#setup)

Run:
  python analyze.py                 # uses Whisper "small.en"
  WHISPER_MODEL=base.en python analyze.py   # faster on a weak laptop

Outputs:
  results/per_utterance.csv   every recording, both engines, WER each
  results/summary.md          tables you can paste into your write-up
"""

import csv
import glob
import json
import os
import re
from collections import defaultdict

import jiwer
import whisper

DATA_DIR = "data"
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
OUT_DIR = "results"
MODEL_NAME = os.environ.get("WHISPER_MODEL", "small.en")


def normalise(text: str) -> str:
    """Lowercase, drop punctuation, collapse spaces so formatting
    differences (e.g. 'Sign-up' vs 'sign up') don't count as errors."""
    text = (text or "").lower().replace("-", " ")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return " ".join(text.split())


def corpus_wer(refs, hyps):
    """WER over a group of utterances (total errors / total reference words)."""
    return jiwer.wer(refs, hyps) if refs else float("nan")


def main():
    entries = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "browser_*.json"))):
        with open(path, encoding="utf-8") as f:
            entries.extend(json.load(f))
    if not entries:
        raise SystemExit("No data/browser_*.json files found.")

    # If the same speaker+instruction appears more than once (e.g. you
    # downloaded the JSON twice, or redid a take), keep only the latest.
    latest = {}
    for e in entries:
        k = (e["speaker"], e["index"])
        if k not in latest or e.get("recorded_at", "") > latest[k].get("recorded_at", ""):
            latest[k] = e
    entries = sorted(latest.values(), key=lambda e: (e["speaker"], e["index"]))

    print(f"Loaded {len(entries)} recordings. Loading Whisper '{MODEL_NAME}'...")
    model = whisper.load_model(MODEL_NAME)

    rows = []
    for e in entries:
        audio_path = os.path.join(AUDIO_DIR, e["audio_file"])
        if not os.path.exists(audio_path):
            print(f"  missing audio: {audio_path} (skipped)")
            continue
        # fp16=False avoids a warning/slowdown on CPU-only machines
        w = model.transcribe(audio_path, language="en", fp16=False)
        ref = normalise(e["reference"])
        hyp_browser = normalise(e.get("browser_transcript", ""))
        hyp_whisper = normalise(w["text"])
        rows.append({
            "speaker": e["speaker"],
            "index": e["index"],
            "reference": ref,
            "browser": hyp_browser,
            "whisper": hyp_whisper,
            "wer_browser": round(jiwer.wer(ref, hyp_browser), 3),
            "wer_whisper": round(jiwer.wer(ref, hyp_whisper), 3),
            "lang": e.get("lang", ""),
        })
        print(f"  {e['speaker']}-{e['index']:>2}: browser={rows[-1]['wer_browser']:.2f}  whisper={rows[-1]['wer_whisper']:.2f}")

    if not rows:
        raise SystemExit("No audio files matched. Check data/audio/.")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "per_utterance.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Group by speaker and overall
    groups = defaultdict(list)
    for r in rows:
        groups[r["speaker"]].append(r)
    groups["ALL"] = rows

    lines = [
        "# ASR pilot: results",
        "",
        f"Whisper model: `{MODEL_NAME}`. Browser engine: Chrome Web Speech API "
        f"(language setting: {', '.join(sorted({r['lang'] for r in rows}))}).",
        "",
        "WER = (substitutions + deletions + insertions) / words in the reference. Lower is better.",
        "",
        "| Speaker | Utterances | Browser WER | Whisper WER |",
        "|---|---|---|---|",
    ]
    for spk in sorted(k for k in groups if k != "ALL") + ["ALL"]:
        g = groups[spk]
        b = corpus_wer([r["reference"] for r in g], [r["browser"] for r in g])
        w = corpus_wer([r["reference"] for r in g], [r["whisper"] for r in g])
        lines.append(f"| {spk} | {len(g)} | {b:.1%} | {w:.1%} |")

    lines += ["", "## Every utterance", "",
              "| ID | Reference | Browser heard | Whisper heard |", "|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['speaker']}-{r['index']} | {r['reference']} | {r['browser'] or '(none)'} | {r['whisper'] or '(none)'} |")

    with open(os.path.join(OUT_DIR, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nDone. See {OUT_DIR}/summary.md and {OUT_DIR}/per_utterance.csv")


if __name__ == "__main__":
    main()
