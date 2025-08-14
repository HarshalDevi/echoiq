from typing import Optional
from faster_whisper import WhisperModel
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class AIEngine:
    def __init__(self):
        self._asr: Optional[WhisperModel] = None
        self._summarizer = None
        self._vader = SentimentIntensityAnalyzer()

    def _asr_model(self) -> WhisperModel:
        if self._asr is None:
            # tiny model, CPU int8 = very light
            self._asr = WhisperModel("tiny", device="cpu", compute_type="int8")
        return self._asr

    def _summarizer_pipe(self):
        if self._summarizer is None:
            # small summarizer to fit 512MiB
            self._summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
        return self._summarizer

    def transcribe(self, audio_file: str) -> str:
        segments, _ = self._asr_model().transcribe(audio_file)
        return " ".join(s.text for s in segments).strip()

    def summarize(self, text: str) -> str:
        # t5-small works better with a "summarize:" prompt
        inp = text if text.lower().startswith("summarize:") else f"summarize: {text}"
        return self._summarizer_pipe()(inp, max_length=60, min_length=15, do_sample=False)[0]["summary_text"]

    def get_sentiment(self, text: str) -> str:
        # lightweight sentiment with VADER (no transformer loaded)
        score = self._vader.polarity_scores(text)["compound"]
        if score >= 0.05: return "POSITIVE"
        if score <= -0.05: return "NEGATIVE"
        return "NEUTRAL"
