class EvolutionEngine:

    def __init__(self):
        self.history = []

    def evolve(self, strategies):

        # 勝者
        best = sorted(strategies, key=lambda x: x["score"], reverse=True)[0]

        self.history.append(best)

        # 強化（シンプル版）
        best["strategy"]["weight"] *= 1.05

        return {
            "evolved": best,
            "history_len": len(self.history)
        }