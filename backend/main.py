from fastapi import FastAPI, WebSocket, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from signaling import signaling_router
from ai_engine import AIEngine

app = FastAPI()

# --- CORS: production Vercel domain + previews + local dev ---
ALLOWED_ORIGINS = [
    "https://echoiq.vercel.app",   # production
    "http://localhost:3000",       # local dev
]
# allow preview deploys like https://echoiq-xxxxx.vercel.app
ALLOWED_ORIGIN_REGEX = r"^https://echoiq-[a-z0-9\-]+\.vercel\.app$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=False,       # not using cookies -> keep CORS simple
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket routes (unchanged)
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

@app.get("/health")
def health():
    return {"ok": True}

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
