from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import json
import asyncio
import random

app = FastAPI()

# -------------------------
# 覇権モード
# -------------------------
MODE = "aggressive"  # balanced / aggressive / defensive

# -------------------------
# Memory（学習）
# -------------------------
memory = []

# -------------------------
# UI
# -------------------------
@app.get("/")
def root():
    return FileResponse("index.html")


# -------------------------
# 戦略生成（thinking）
# -------------------------
def generate_strategies(goal):

    base = [
        "expand",
        "optimize",
        "aggressive",
        "defensive",
        "exploit",
        "disrupt"
    ]

    strategies = []

    for b in base:
        strategies.append({
            "type": b,
            "weight": random.uniform(0.8, 1.3)
        })

    return strategies


# -------------------------
# シミュレーション
# -------------------------
def simulate(strategy):

    success = random.uniform(1.0, 1.7) * strategy["weight"]
    risk = random.uniform(0.2, 0.7)

    return {
        "success": success,
        "risk": risk
    }


# -------------------------
# 評価（Memory + モード）
# -------------------------
def evaluate(strategy, sim):

    score = sim["success"] - sim["risk"]

    # Memory補正（学習）
    for m in memory:
        if m["strategy"] == strategy["type"]:
            score *= 1.1

    # モード補正（人格）
    if MODE == "aggressive":
        score *= 1.2
    elif MODE == "defensive":
        score *= 0.9

    return score


# -------------------------
# WebSocket（UI連携）
# -------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    while True:
        data = await ws.receive_text()
        data = json.loads(data)

        goal = data.get("goal", "")

        strategies = generate_strategies(goal)

        results = []

        # thinking表示
        for s in strategies:

            sim = simulate(s)
            score = evaluate(s, sim)

            result = {
                "strategy": s,
                "simulation": sim,
                "score": score
            }

            results.append(result)

            await ws.send_text(json.dumps({
                "type": "thinking",
                "data": {
                    "type": s["type"],
                    "score": score
                }
            }))

            await asyncio.sleep(0.3)

        # 勝者決定
        winner = sorted(results, key=lambda x: x["score"], reverse=True)[0]

        # Memory保存
        memory.append({
            "goal": goal,
            "strategy": winner["strategy"]["type"],
            "score": winner["score"]
        })

        # winner表示
        await ws.send_text(json.dumps({
            "type": "winner",
            "data": {
                "type": winner["strategy"]["type"],
                "score": winner["score"]
            }
        }))

        # evolution表示
        await ws.send_text(json.dumps({
            "type": "evolution",
            "data": {
                "memory_size": len(memory),
                "mode": MODE
            }
        }))