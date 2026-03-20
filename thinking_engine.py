　from decision_engine import DecisionEngine
from memory_pool import MemoryPool
from evolution_engine import EvolutionEngine


class ThinkingEngine:

    def __init__(self, mode="balanced"):

        self.decision = DecisionEngine()
        self.memory = MemoryPool()
        self.evolution = EvolutionEngine()

        self.mode = mode

        # 思考履歴
        self.history = []

    # ------------------------
    # メイン実行
    # ------------------------
    def run(self, goal):

        # ① Memory取得
        memory_context = self.memory.search(goal)

        # ② 意思決定
        result = self.decision.decide(goal, memory_context)

        winner = result["winner"]

        # ③ モード補正（性格）
        winner = self._apply_mode(winner)

        # ④ Memory保存
        self.memory.store({
            "goal": goal,
            "strategy": winner["strategy"]["type"],
            "score": winner["score"]
        })

        # ⑤ 進化（ここが追加された核）
        evolution_result = self.evolution.evolve(result["all"])

        # ⑥ 履歴保存
        self.history.append({
            "goal": goal,
            "winner": winner,
            "evolution": evolution_result
        })

        return {
            "decision": result,
            "evolution": evolution_result
        }


    # ------------------------
    # 長期思考
    # ------------------------
    def run_long_term(self, goal):

        memory_context = self.memory.search(goal)

        result = self.decision.decide_long_term(goal, memory_context)

        self.memory.store({
            "goal": goal,
            "strategy": result["strategy"]["type"],
            "score": result["score"]
        })

        return result


    # ------------------------
    # モード（個性）
    # ------------------------
    def _apply_mode(self, winner):

        if self.mode == "aggressive":
            winner["score"] *= 1.2

        elif self.mode == "defensive":
            winner["score"] *= 0.9

        elif self.mode == "balanced":
            pass

        return winner


    # ------------------------
    # 自己分析
    # ------------------------
    def self_reflect(self):

        patterns = {}

        for h in self.history:

            strat = h["winner"]["strategy"]["type"]

            if strat not in patterns:
                patterns[strat] = 0

            patterns[strat] += 1

        return sorted(patterns.items(), key=lambda x: x[1], reverse=True)


    # ------------------------
    # 学習強化
    # ------------------------
    def reinforce(self):

        insights = self.self_reflect()

        if not insights:
            return None

        best = insights[0]

        return {
            "best_strategy": best[0],
            "count": best[1]
        }