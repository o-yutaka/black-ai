　from fastapi import FastAPI, WebSocket
import json
import asyncio

app = FastAPI()


@app.get("/")
def root():
    return {"status": "BLACK DISTRIBUTED ONLINE"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        data = await ws.receive_text()
        data = json.loads(data)

        goal = data.get("goal", "")

        strategies = [
            {"type": "expand", "score": 0.9},
            {"type": "optimize", "score": 0.7},
            {"type": "aggressive", "score": 0.85}
        ]

        for s in strategies:
            await ws.send_text(json.dumps({
                "type": "thinking",
                "data": s
            }))
            await asyncio.sleep(0.5)

        winner = sorted(strategies, key=lambda x: x["score"], reverse=True)[0]

        await ws.send_text(json.dumps({
            "type": "winner",
            "data": winner
        }))

        await ws.send_text(json.dumps({
            "type": "evolution",
            "data": {"improved": True}
        }))