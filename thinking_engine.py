from decision_engine import DecisionEngine
from memory_pool import MemoryPool


class ThinkingEngine:

    def __init__(self):
        self.decision = DecisionEngine()
        self.memory = MemoryPool()
        self.history = []

    def run(self, goal):

        # ① Memory取得
        mem = self.memory.search(goal)

        # ② 意思決定
        result = self.decision.decide(goal, mem)

        # ③ 保存
        self.memory.store({
            "goal": goal,
            "result": result
        })

        self.history.append(result)

        return {
            "goal": goal,
            "memory": mem,
            "decision": result
        }