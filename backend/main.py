from fastapi import FastAPI, WebSocket, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from signaling import signaling_router          # keep your websocket router
from ai_engine import AIEngine                  # uses faster-whisper + t5-small + VADER

app = FastAPI()

# Allow your frontend; tighten later to your exact Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # later: ["https://<your-frontend>.vercel.app", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket routes
app.include_router(signaling_router)

# ---- Lazy init so models load only on first use ----
_engine: AIEngine | None = None
def get_engine() -> AIEngine:
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine

@app.get("/")
def root():
    return {"message": "EchoIQ backend is live"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    tmp_path = "temp_audio.wav"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    transcript = get_engine().transcribe(tmp_path)
    return {"transcript": transcript}

@app.post("/summarize")
async def summarize_text(request: Request):
    body = await request.json()
    text = body.get("text", "")
    summary = get_engine().summarize(text)
    return {"summary": summary}

@app.post("/sentiment")
async def sentiment_analysis(request: Request):
    body = await request.json()
    text = body.get("text", "")
    sentiment = get_engine().get_sentiment(text)
    return {"sentiment": sentiment}
