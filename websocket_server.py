import asyncio
import websockets
import json

from thinking_engine import ThinkingEngine


engine = ThinkingEngine()


async def handler(websocket):

    async for message in websocket:

        data = json.loads(message)
        goal = data.get("goal")

        result = engine.run(goal)

        # ------------------------
        # 思考を段階送信（演出）
        # ------------------------

        for r in result["decision"]["top"]:

            await websocket.send(json.dumps({
                "type": "thinking",
                "data": r
            }))

            await asyncio.sleep(0.3)

        # ------------------------
        # 勝者
        # ------------------------

        await websocket.send(json.dumps({
            "type": "winner",
            "data": result["decision"]["winner"]
        }))

        # ------------------------
        # 進化
        # ------------------------

        await websocket.send(json.dumps({
            "type": "evolution",
            "data": result["evolution"]
        }))


start_server = websockets.serve(handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()