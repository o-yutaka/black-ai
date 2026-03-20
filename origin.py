from thinking_engine import ThinkingEngine


class BlackNode:

    def __init__(self, mode):
        self.engine = ThinkingEngine()
        self.mode = mode

    def run(self, goal):
        result = self.engine.run(goal)

        return {
            "mode": self.mode,
            "result": result
        }


class BlackOrchestrator:

    def __init__(self):

        self.nodes = [
            BlackNode("aggressive"),
            BlackNode("defensive"),
            BlackNode("balanced")
        ]

    def execute(self, goal):

        results = []

        for node in self.nodes:
            res = node.run(goal)
            results.append(res)

        # ------------------------
        # 勝者選定（ここが核）
        # ------------------------
        best = sorted(
            results,
            key=lambda x: x["result"]["decision"]["winner"]["score"],
            reverse=True
        )[0]

        return {
            "winner": best,
            "all": results
        }