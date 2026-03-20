def evaluate(strategy, sim):

    score = sim["success"] - sim["risk"]

    # Memory補正
    for m in memory:
        if m["strategy"] == strategy["type"]:
            score *= 1.1

    # モード補正
    if MODE == "aggressive":
        score *= 1.2

    elif MODE == "defensive":
        score *= 0.9

    elif MODE == "balanced":
        pass

    return score