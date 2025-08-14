'use client'

import { useState } from 'react'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [transcript, setTranscript] = useState('')
  const [summary, setSummary] = useState('')
  const [sentiment, setSentiment] = useState('')
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) {
      alert('Please upload a .wav file.')
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://127.0.0.1:8000/transcribe', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      setTranscript(data.transcript)

      const sumRes = await fetch('http://127.0.0.1:8000/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.transcript }),
      })
      const sumData = await sumRes.json()
      setSummary(sumData.summary)

      const sentiRes = await fetch('http://127.0.0.1:8000/sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.transcript }),
      })
      const sentiData = await sentiRes.json()
      setSentiment(sentiData.sentiment)

      alert('Analysis complete!')
    } catch (err) {
      alert('Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="grid-background" />
      <div className="container">
        <h1 className="title">EchoIQ</h1>
        <p className="subtitle">Transcribe. Summarize. Understand.</p>

        <input type="file" accept=".wav" onChange={(e) => setFile(e.target.files?.[0] || null)} />

        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'Analyzing...' : 'Upload & Analyze'}
        </button>

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
  )
}
