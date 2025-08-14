from fastapi import APIRouter, WebSocket

signaling_router = APIRouter()

@signaling_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            print(f"Received from frontend: {data}")
            await websocket.send_text(f"Echo: {data}")
        except Exception as e:
            print("WebSocket error:", e)
            break
