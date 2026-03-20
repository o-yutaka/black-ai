from fastapi import FastAPI
from origin import BlackOrchestrator

app = FastAPI()

orchestrator = BlackOrchestrator()


@app.get("/")
def root():
    return {"status": "BLACK DISTRIBUTED ONLINE"}


@app.post("/think")
def think(data: dict):
    goal = data.get("goal", "")
    return orchestrator.execute(goal)