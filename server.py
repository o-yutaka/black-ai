from fastapi import FastAPI
from thinking_engine import ThinkingEngine

app = FastAPI()

engine = ThinkingEngine()

@app.get("/")
def root():
    return {"status": "BLACK ONLINE"}

@app.post("/think")
def think(data: dict):
    return engine.run(data["goal"])