import random


class EvolutionEngine:

    def __init__(self):
        self.history = []

    # ------------------------
    # 進化メイン
    # ------------------------
    def evolve(self, results):

        if not results:
            return None

        # 勝者
        winner = results[0]

        # 敗者
        losers = results[1:]

        # ------------------------
        # 勝者強化
        # ------------------------
        winner = self._reinforce(winner)

        # ------------------------
        # 敗者分解
        # ------------------------
        parts = self._decompose(losers)

        # ------------------------
        # 合成（新戦略生成）
        # ------------------------
        new_strategies = self._synthesize(winner, parts)

        # ------------------------
        # 記録
        # ------------------------
        self.history.append({
            "winner": winner,
            "generated": new_strategies
        })

        return {
            "winner": winner,
            "new": new_strategies
        }

    # ------------------------
    # 勝者強化
    # ------------------------
    def _reinforce(self, winner):

        winner["score"] *= 1.1
        return winner

    # ------------------------
    # 敗者分解
    # ------------------------
    def _decompose(self, losers):

        parts = []

        for l in losers:

            strategy = l["strategy"]["type"]

            parts.extend(strategy.split("_"))

        return parts

    # ------------------------
    # 合成（進化の核）
    # ------------------------
    def _synthesize(self, winner, parts):

        new = []

        base = winner["strategy"]["type"]

        for _ in range(3):

            if parts:
                p = random.choice(parts)
                new_strategy = f"{p}_{base}"
            else:
                new_strategy = f"mutated_{base}"

            new.append({
                "type": new_strategy,
                "weight": random.uniform(0.8, 1.3)
            })

        return new