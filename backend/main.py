from fastapi import FastAPI, WebSocket, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from signaling import signaling_router
from ai_engine import AIEngine

app = FastAPI()

# Enable CORS so frontend (React) can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register WebSocket routes
app.include_router(signaling_router)

# Initialize the AI engine (loads Whisper, summarizer, etc.)
ai_engine = AIEngine()

@app.get("/")
def root():
    return {"message": "EchoIQ backend is live"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save the uploaded audio file
    with open("temp_audio.wav", "wb") as f:
        f.write(await file.read())

    # Transcribe the audio using Whisper
    transcript = ai_engine.transcribe("temp_audio.wav")
    return {"transcript": transcript}

@app.post("/summarize")
async def summarize_text(request: Request):
    body = await request.json()
    text = body.get("text", "")
    summary = ai_engine.summarize(text)
    return {"summary": summary}

@app.post("/sentiment")
async def sentiment_analysis(request: Request):
    body = await request.json()
    text = body.get("text", "")
    sentiment = ai_engine.get_sentiment(text)
    return {"sentiment": sentiment}
