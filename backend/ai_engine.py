from faster_whisper import WhisperModel
from transformers import pipeline

class AIEngine:
    def __init__(self):
        # Use small CPU-friendly models
        self.asr = WhisperModel("tiny", device="cpu", compute_type="int8")  # ~75MB
        self.summarizer = pipeline(
            "summarization", model="sshleifer/distilbart-cnn-12-6"
        )
        self.sentiment = pipeline(
            "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    def transcribe(self, audio_file: str) -> str:
        segments, _ = self.asr.transcribe(audio_file)
        return " ".join([s.text for s in segments]).strip()

    def summarize(self, text: str) -> str:
        return self.summarizer(
            text, max_length=60, min_length=20, do_sample=False
        )[0]["summary_text"]

    def get_sentiment(self, text: str) -> str:
        return self.sentiment(text)[0]["label"]
