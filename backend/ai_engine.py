from __future__ import annotations
import os
import re
import requests
from typing import Optional, List

from faster_whisper import WhisperModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Hugging Face Inference API config ---
HF_MODEL = os.getenv("HF_SUMMARY_MODEL", "t5-small")          # e.g. "t5-small" or "google/flan-t5-small"
HF_TOKEN = os.getenv("HF_API_TOKEN", "").strip()               # set in Render env

def _split_sentences(text: str) -> List[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+', (text or "").strip()) if s]

def _fallback_summary(text: str, max_sents: int = 2, max_chars: int = 300) -> str:
    sents = _split_sentences(text)
    if sents:
        out = " ".join(sents[:max_sents]).strip()
        return out[:max_chars] if out else (text or "")[:max_chars]
    return (text or "")[:max_chars]

class AIEngine:
    def __init__(self):
        self._asr: Optional[WhisperModel] = None
        self._vader = SentimentIntensityAnalyzer()
        self._last_summary_source = "fallback"

    # ---------- Speech-to-text ----------
    def _asr_model(self) -> WhisperModel:
        if self._asr is None:
            # very small model for 512MiB instances
            self._asr = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        return self._asr

    def transcribe(self, audio_file: str) -> str:
        segments, _ = self._asr_model().transcribe(audio_file, beam_size=1, vad_filter=True)
        return " ".join(s.text for s in segments).strip()

    # ---------- Summarize via HF Inference (with safe fallback) ----------
    def summarize(self, text: str) -> str:
        txt = (text or "").strip()
        if not txt:
            self._last_summary_source = "huggingface" if HF_TOKEN else "fallback"
            return ""

        if HF_TOKEN:
            try:
                # T5-style “summarize:” prefix helps
                payload = {
                    "inputs": f"summarize: {txt[:2000]}",   # cap very long input
                    "parameters": {"max_length": 60, "min_length": 20, "do_sample": False},
                    "options": {"wait_for_model": True},     # handle cold starts on HF
                }
                r = requests.post(
                    f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                    headers={"Authorization": f"Bearer {HF_TOKEN}"},
                    json=payload,
                    timeout=40,
                )
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list) and data and "summary_text" in data[0]:
                        self._last_summary_source = "huggingface"
                        return (data[0]["summary_text"] or "").strip()
                # any non-200 or unexpected body → fallback
            except Exception:
                pass

        self._last_summary_source = "fallback"
        return _fallback_summary(txt)

    def summary_source(self) -> str:
        return self._last_summary_source

    # ---------- Sentiment ----------
    def get_sentiment(self, text: str) -> str:
        c = self._vader.polarity_scores(text or "")["compound"]
        if c >= 0.2:
            return "POSITIVE"
        if c <= -0.2:
            return "NEGATIVE"
        return "NEUTRAL"
