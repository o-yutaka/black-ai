from strategy_generator import StrategyGenerator
from simulator import Simulator
from scorer import Scorer


class DecisionEngine:

    def __init__(self):

        self.generator = StrategyGenerator()
        self.simulator = Simulator()
        self.scorer = Scorer()

    # ------------------------
    # メイン決定
    # ------------------------
    def decide(self, goal, memory=None):

        # ① 戦略生成
        strategies = self.generator.generate(goal, memory)

        results = []

        # ② シミュレーション + スコア
        for s in strategies:

            sim = self.simulator.simulate(s)

            score = self.scorer.score(sim)

            results.append({
                "strategy": s,
                "simulation": sim,
                "score": score
            })

        # ③ ソート
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        winner = results[0]

        return {
            "winner": winner,
            "top": results[:5],
            "all": results
        }


    # ------------------------
    # 長期判断（マルチステップ）
    # ------------------------
    def decide_long_term(self, goal, memory=None):

        strategies = self.generator.generate(goal, memory)

        results = []

        for s in strategies:

            sim = self.simulator.simulate_multi(s)

            score = self.scorer.score_multi(sim)

            results.append({
                "strategy": s,
                "simulation": sim,
                "score": score
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return results[0]