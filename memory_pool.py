　def search(self, goal):

    results = []

    for d in self.data:
        if goal in d.get("goal", ""):
            results.append(d)

    # スコア高い順にする
    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    return results[:5]