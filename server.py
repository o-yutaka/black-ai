from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import json
import asyncio
import random
import os
from openai import OpenAI

app = FastAPI()

# ★ APIキー（確実取得）
API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

MODE = "aggressive"

memory = []

@app.get("/")
def root():
    return FileResponse("index.html")


def generate_strategies(goal):

    base = [
        "expand",
        "optimize",
        "aggressive",
        "defensive",
        "exploit",
        "disrupt"
    ]

    return [
        {"type": b, "weight": random.uniform(0.8, 1.3)}
        for b in base
    ]


def simulate(strategy):

    return {
        "success": random.uniform(1.0, 1.7) * strategy["weight"],
        "risk": random.uniform(0.2, 0.7)
    }


def evaluate(strategy, sim):

    score = sim["success"] - sim["risk"]

    for m in memory:
        if m["strategy"] == strategy["type"]:
            score *= 1.1

    if MODE == "aggressive":
        score *= 1.2
    elif MODE == "defensive":
        score *= 0.9

    return score


def generate_answer(goal, winner):

    # ★ APIキー未設定時の安全処理
    if not API_KEY:
        return "API KEY NOT SET"

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Explain clearly and simply."},
                {"role": "user", "content": f"Goal: {goal}\nBest strategy: {winner}\nExplain what to do."}
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        return "ERROR: " + str(e)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        data = await ws.receive_text()
        data = json.loads(data)

        goal = data.get("goal", "")

        strategies = generate_strategies(goal)

        results = []

        for s in strategies:

            sim = simulate(s)
            score = evaluate(s, sim)

            results.append({
                "strategy": s,
                "score": score
            })

            await ws.send_text(json.dumps({
                "type": "thinking",
                "data": {
                    "type": s["type"],
                    "score": score
                }
            }))

            await asyncio.sleep(0.2)

        winner = sorted(results, key=lambda x: x["score"], reverse=True)[0]

        memory.append({
            "goal": goal,
            "strategy": winner["strategy"]["type"],
            "score": winner["score"]
        })

        await ws.send_text(json.dumps({
            "type": "winner",
            "data": {
                "type": winner["strategy"]["type"],
                "score": winner["score"]
            }
        }))

        # ★ GPT回答
        answer = generate_answer(goal, winner["strategy"]["type"])

        await ws.send_text(json.dumps({"type": "answer_start"}))

        for c in answer:
            await ws.send_text(json.dumps({
                "type": "answer_stream",
                "data": c
            }))
            await asyncio.sleep(0.01)

        await ws.send_text(json.dumps({"type": "answer_end"}))