from decision_engine import DecisionEngine
from memory_pool import MemoryPool
from evolution_engine import EvolutionEngine


class ThinkingEngine:

    def __init__(self):
        self.decision = DecisionEngine()
        self.memory = MemoryPool()
        self.evolution = EvolutionEngine()

        # ------------------------
        # 勝率記録（ここが核）
        # ------------------------
        self.mode_stats = {}

        # 覇権モード
        self.dominant_mode = None

    def run(self, goal):

        mem = self.memory.search(goal)

        result = self.decision.decide(goal, mem)

        winner = result["winner"]

        # ------------------------
        # 勝者のmode取得
        # ------------------------
        mode = winner.get("mode", "unknown")

        # ------------------------
        # 勝率カウント
        # ------------------------
        if mode not in self.mode_stats:
            self.mode_stats[mode] = 0

        self.mode_stats[mode] += 1

        # ------------------------
        # 覇権モード決定
        # ------------------------
        self.dominant_mode = max(
            self.mode_stats,
            key=lambda x: self.mode_stats[x]
        )

        # ------------------------
        # 覇権バイアス（ここが最強）
        # ------------------------
        if mode == self.dominant_mode:
            winner["score"] *= 1.2  # 強化

        # ------------------------
        # Memory保存（勝者のみ）
        # ------------------------
        self.memory.store({
            "goal": goal,
            "strategy": winner["strategy"]["type"],
            "score": winner["score"],
            "mode": mode
        })

        # ------------------------
        # Evolution
        # ------------------------
        evo = self.evolution.evolve(result["top"])

        return {
            "decision": result,
            "evolution": evo,
            "dominant_mode": self.dominant_mode,
            "mode_stats": self.mode_stats
        }