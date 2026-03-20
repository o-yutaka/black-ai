from fastapi import FastAPI
from decision_engine import DecisionEngine

app = FastAPI()

engine = DecisionEngine()


@app.get("/")
def root():
    return {"status": "BLACK ONLINE"}


@app.post("/think")
def think(data: dict):
    goal = data.get("goal", "")

    result = engine.decide(goal)

    return result 