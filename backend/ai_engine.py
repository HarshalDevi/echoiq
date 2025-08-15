# backend/ai_engine.py
from __future__ import annotations
from typing import List, Optional
import re

from faster_whisper import WhisperModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def _split_sentences(text: str) -> List[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s]


def _simple_summary(text: str, max_sents: int = 2, max_chars: int = 300) -> str:
    """Dependency-free summary: first 1–2 sentences or first ~300 chars."""
    sents = _split_sentences(text)
    if sents:
        out = " ".join(sents[:max_sents]).strip()
        if out:
            return out[: max_chars].strip()
    return text[: max_chars].strip()


class AIEngine:
    def __init__(self):
        self._stt: Optional[WhisperModel] = None
        self._sent = SentimentIntensityAnalyzer()
        self._last_summary_source = "fallback"  # we only use fallback in this minimal build

    # ---------- ASR ----------
    def _load_stt(self) -> None:
        if self._stt is None:
            # smaller model -> much lower RAM and faster cold start
            self._stt = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    def transcribe(self, audio_file: str) -> str:
        self._load_stt()
        segments, _ = self._stt.transcribe(audio_file, beam_size=1, vad_filter=True)
        return " ".join(seg.text for seg in segments).strip()

    # ---------- Summarize (fallback-only) ----------
    def summarize(self, text: str) -> str:
        self._last_summary_source = "fallback"
        txt = (text or "").strip()
        if not txt:
            return ""
        return _simple_summary(txt)

    def summary_source(self) -> str:
        return self._last_summary_source

    # ---------- Sentiment ----------
    def get_sentiment(self, text: str) -> str:
        score = self._sent.polarity_scores(text or "")["compound"]
        if score >= 0.2:
            return "POSITIVE"
        if score <= -0.2:
            return "NEGATIVE"
        return "NEUTRAL"
