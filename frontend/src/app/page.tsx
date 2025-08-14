"use client";

import { useState, type ChangeEvent } from "react";

const API_LABEL =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/+$/, "") ?? "http://localhost:10000";

type TranscribeResponse = { transcript?: string };
type SummarizeResponse = { summary?: string };
type SentimentResponse = { sentiment?: string };

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [sentiment, setSentiment] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
  };

  const handleUpload = async () => {
    setErr(null);
    setTranscript("");
    setSummary("");
    setSentiment("");

    if (!file) {
      setErr("Please upload a .wav file.");
      return;
    }

    try {
      setLoading(true);

      // 1) /transcribe (proxy)
      const fd = new FormData();
      fd.append("file", file, file.name || "audio.wav");

      const transcribeRes = await fetch("/api/transcribe", {
        method: "POST",
        body: fd,
      });
      if (!transcribeRes.ok) throw new Error(`/transcribe failed`);
      const transcribeJson = (await transcribeRes.json()) as TranscribeResponse;
      const text = transcribeJson.transcript ?? "";
      setTranscript(text);

      // 2) /summarize (proxy)
      const summarizeRes = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!summarizeRes.ok) throw new Error(`/summarize failed`);
      const summarizeJson = (await summarizeRes.json()) as SummarizeResponse;
      setSummary(summarizeJson.summary ?? "");

      // 3) /sentiment (proxy)
      const sentimentRes = await fetch("/api/sentiment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!sentimentRes.ok) throw new Error(`/sentiment failed`);
      const sentimentJson = (await sentimentRes.json()) as SentimentResponse;
      setSentiment(sentimentJson.sentiment ?? "");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="grid-background" />
      <div className="container">
        <h1 className="title">EchoIQ</h1>
        <p className="subtitle">Transcribe. Summarize. Understand.</p>

        {/* Just a label for debugging; calls now go through /api/* */}
        <p style={{ opacity: 0.7, fontSize: 12, marginBottom: 8 }}>API: {API_LABEL}</p>

        <input type="file" accept=".wav,audio/wav" onChange={onFileChange} />

        <button onClick={handleUpload} disabled={loading} style={{ marginTop: 12 }}>
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>

        {err && (
          <div className="result-box" style={{ borderColor: "#f87171", color: "#fecaca" }}>
            <h3>Error</h3>
            <p>{err}</p>
          </div>
        )}

        {transcript && (
          <div className="result-box">
            <h3>Transcript:</h3>
            <p>{transcript}</p>
          </div>
        )}
        {summary && (
          <div className="result-box">
            <h3>Summary:</h3>
            <p>{summary}</p>
          </div>
        )}
        {sentiment && (
          <div className="result-box">
            <h3>Sentiment:</h3>
            <p>{sentiment}</p>
          </div>
        )}
      </div>
    </>
  );
}
