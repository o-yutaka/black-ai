from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "BLACK ONLINE"}


@app.post("/think")
def think(data: dict):
    goal = data.get("goal", "")

    # 仮の意思決定
    strategies = [
        {"type": "expand", "score": 0.9},
        {"type": "optimize", "score": 0.7},
        {"type": "aggressive", "score": 0.85}
    ]

    winner = sorted(strategies, key=lambda x: x["score"], reverse=True)[0]

    return {
        "goal": goal,
        "decision": winner,
        "all": strategies
    }