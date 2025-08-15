# backend/ai_engine.py
from __future__ import annotations
import os, re, requests
from typing import List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from faster_whisper import WhisperModel  # keep using faster-whisper for STT

HF_MODEL = os.getenv("HF_SUMMARY_MODEL", "google-t5/t5-small")
HF_TOKEN = os.getenv("HF_API_TOKEN", "").strip()

def _split_sentences(text: str) -> List[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+', (text or "").strip()) if s]

def _fallback_summary(text: str, max_sents: int = 2, max_chars: int = 300) -> str:
    sents = _split_sentences(text)
    if sents:
        out = " ".join(sents[:max_sents]).strip()
        return out[:max_chars].strip() if out else (text or "")[:max_chars].strip()
    return (text or "")[:max_chars].strip()

class AIEngine:
    def __init__(self):
        # small model to fit Render free CPU RAM
        self._stt: Optional[WhisperModel] = None
        self._sent = SentimentIntensityAnalyzer()
        self._last_summary_source = "fallback"

    # ---------- STT ----------
    def _load_stt(self):
        if self._stt is None:
            self._stt = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    def transcribe(self, audio_file: str) -> str:
        self._load_stt()
        segments, _ = self._stt.transcribe(audio_file, beam_size=1, vad_filter=True)
        return " ".join(seg.text for seg in segments).strip()

    # ---------- Summarize via HF Inference API (with fallback) ----------
    def summarize(self, text: str) -> str:
        txt = (text or "").strip()
        if not txt:
            self._last_summary_source = "huggingface" if HF_TOKEN else "fallback"
            return ""

        if HF_TOKEN:
            try:
                # T5 likes the "summarize:" prefix
                payload = {
                    "inputs": f"summarize: {txt[:2000]}",    # cap input length
                    "parameters": {"max_length": 60, "min_length": 20, "do_sample": False},
                    "options": {"wait_for_model": True},     # handle cold starts remotely
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
                # non-200 or unexpected body -> fallback
            except Exception:
                pass

        self._last_summary_source = "fallback"
        return _fallback_summary(txt)

    def summary_source(self) -> str:
        return self._last_summary_source

    # ---------- Sentiment ----------
    def get_sentiment(self, text: str) -> str:
        score = self._sent.polarity_scores(text or "")["compound"]
        if score >= 0.2: return "POSITIVE"
        if score <= -0.2: return "NEGATIVE"
        return "NEUTRAL"
