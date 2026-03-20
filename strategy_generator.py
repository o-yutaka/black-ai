import random


class StrategyGenerator:

    def __init__(self):

        self.base = [
            "expand",
            "exploit",
            "disrupt",
            "defend"
        ]

        self.modifiers = [
            "base",
            "hybrid",
            "extreme",
            "adaptive",
            "inverse"
        ]

    def generate(self, goal, memory=None):

        strategies = []

        # 基本生成
        for b in self.base:
            for m in self.modifiers:
                strategies.append({
                    "type": f"{m}_{b}",
                    "goal": goal,
                    "weight": self._initial_weight(m)
                })

        # Memory拡張（吸収）
        if memory:
            strategies.extend(self._memory_expand(goal, memory))

        # 進化（変異）
        strategies = self._mutate(strategies)

        return strategies


    # ------------------------
    # 初期重み
    # ------------------------
    def _initial_weight(self, modifier):

        if modifier == "extreme":
            return 1.3
        if modifier == "hybrid":
            return 1.1
        if modifier == "adaptive":
            return 1.2

        return 1.0


    # ------------------------
    # Memory吸収
    # ------------------------
    def _memory_expand(self, goal, memory):

        extended = []

        for m in memory:

            extended.append({
                "type": f"memory_{m}",
                "goal": goal,
                "weight": 1.2
            })

        return extended


    # ------------------------
    # 変異（進化）
    # ------------------------
    def _mutate(self, strategies):

        mutated = []

        for s in strategies:

            if random.random() > 0.75:
                s["weight"] *= random.uniform(0.8, 1.3)

            mutated.append(s)

        return mutated