# backend/ai_engine.py
from __future__ import annotations
from typing import List
import re

# Speech-to-text: tiny CPU footprint
from faster_whisper import WhisperModel

# Sentiment: tiny dependency, no NLTK download
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Try to import transformers summarizer; if it fails (OOM, etc.), we'll fallback
try:
    from transformers import pipeline  # type: ignore
    _TRANSFORMERS_OK = True
except Exception:
    _TRANSFORMERS_OK = False


def _split_sentences(text: str, max_chars: int = 300) -> List[str]:
    """Soft chunk by sentence-ish boundaries, keeping chunks small for T5-small."""
    # quick sentence split, then re-pack into ~max_chars
    parts = re.split(r'(?<=[\.\!\?])\s+', text.strip())
    chunks: List[str] = []
    cur = ""
    for p in parts:
        if not p:
            continue
        if len(cur) + 1 + len(p) <= max_chars:
            cur = (cur + " " + p).strip()
        else:
            if cur:
                chunks.append(cur)
            cur = p
    if cur:
        chunks.append(cur)
    return chunks or [text]


def _simple_summary(text: str, max_sents: int = 2) -> str:
    """Very small, dependency-free fallback summarizer."""
    sents = re.split(r'(?<=[\.\!\?])\s+', text.strip())
    out = " ".join(sents[:max_sents]).strip()
    return out or text[:200].strip()


class AIEngine:
    def __init__(self):
        # lazy-load everything to keep memory low
        self._stt: WhisperModel | None = None
        self._sum = None
        self._sent = SentimentIntensityAnalyzer()

    # ---------- ASR ----------
    def _load_stt(self):
        if self._stt is None:
            # base model, CPU int8 is light and accurate enough
            self._stt = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_file: str) -> str:
        self._load_stt()
        segments, _ = self._stt.transcribe(audio_file, beam_size=1, vad_filter=True)
        return " ".join(seg.text for seg in segments).strip()

    # ---------- Summarize ----------
    def _load_summarizer(self):
        if self._sum is None and _TRANSFORMERS_OK:
            # smallest reasonable model
            self._sum = pipeline(
                "summarization",
                model="t5-small",
                tokenizer="t5-small",
                device=-1,            # CPU
                framework="pt",
            )

    def summarize(self, text: str) -> str:
        txt = (text or "").strip()
        if not txt:
            return ""
        try:
            self._load_summarizer()
            if self._sum is None:
                # transformers unavailable or failed -> fallback
                return _simple_summary(txt)

            chunks = _split_sentences(txt, max_chars=300)
            outs: List[str] = []
            for ch in chunks:
                # small lengths to keep memory low
                out = self._sum(ch, max_length=60, min_length=12, do_sample=False)[0]["summary_text"]
                outs.append(out.strip())
            summary = " ".join(outs).strip()
            return summary or _simple_summary(txt)
        except Exception:
            # any runtime error (e.g., OOM) → safe fallback
            return _simple_summary(txt)

    # ---------- Sentiment ----------
    def get_sentiment(self, text: str) -> str:
        score = self._sent.polarity_scores(text or "")["compound"]
        if score >= 0.2:
            return "POSITIVE"
        if score <= -0.2:
            return "NEGATIVE"
        return "NEUTRAL"
