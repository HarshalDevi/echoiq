"use client";

import { useState } from "react";

const API =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/+$/, "") ?? "http://localhost:10000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [sentiment, setSentiment] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

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

      // 1) /transcribe
      const fd = new FormData();
      fd.append("file", file, file.name || "audio.wav");

      const transcribeRes = await fetch(`${API}/transcribe`, {
        method: "POST",
        body: fd,
      });
      if (!transcribeRes.ok) throw new Error(`/transcribe failed`);
      const transcribeJson = await transcribeRes.json();
      const text: string = transcribeJson?.transcript || "";
      setTranscript(text);

      // 2) /summarize
      const summarizeRes = await fetch(`${API}/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!summarizeRes.ok) throw new Error(`/summarize failed`);
      const summarizeJson = await summarizeRes.json();
      setSummary(summarizeJson?.summary || "");

      // 3) /sentiment
      const sentimentRes = await fetch(`${API}/sentiment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!sentimentRes.ok) throw new Error(`/sentiment failed`);
      const sentimentJson = await sentimentRes.json();
      setSentiment(sentimentJson?.sentiment || "");
    } catch (e: any) {
      setErr(e?.message ?? "Something went wrong.");
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

        <p style={{ opacity: 0.7, fontSize: 12, marginBottom: 8 }}>
          API: {API}
        </p>

        <input
          type="file"
          accept=".wav,audio/wav"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />

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
