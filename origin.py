import threading


class Origin:

    def __init__(self, engines):

        self.engines = engines

    def run(self, goal):

        results = []
        threads = []

        def execute(engine):
            res = engine.run(goal)
            results.append(res)

        # 並列実行
        for e in self.engines:
            t = threading.Thread(target=execute, args=(e,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return self._select(results)


    # ------------------------
    # 勝者選定
    # ------------------------
    def _select(self, results):

        best = None
        best_score = -1

        for r in results:

            score = r["winner"]["score"]

            if score > best_score:
                best = r
                best_score = score

        return best