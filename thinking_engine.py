def run(self, goal):

    mem = self.memory.search(goal)

    result = self.decision.decide(goal, mem)

    # ------------------------
    # 勝者だけ保存
    # ------------------------
    winner = result["winner"]

    self.memory.store({
        "goal": goal,
        "strategy": winner["strategy"]["type"],
        "score": winner["score"]
    })

    evo = self.evolution.evolve(result["top"])

    return {
        "decision": result,
        "evolution": evo,
        "memory": mem
    }