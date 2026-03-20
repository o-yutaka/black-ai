from decision_engine import DecisionEngine
from memory_pool import MemoryPool
from evolution_engine import EvolutionEngine


class ThinkingEngine:

    def __init__(self):
        self.decision = DecisionEngine()
        self.memory = MemoryPool()
        self.evolution = EvolutionEngine()

    def run(self, goal):

        # Memory
        mem = self.memory.search(goal)

        # 思考
        result = self.decision.decide(goal, mem)

        # 進化
        evo = self.evolution.evolve(result["top"])

        # 保存
        self.memory.store({
            "goal": goal,
            "result": result
        })

        return {
            "decision": result,
            "evolution": evo,
            "memory": mem
        }