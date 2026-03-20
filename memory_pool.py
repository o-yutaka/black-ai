class MemoryPool:

    def __init__(self):
        self.data = []

    def store(self, item):
        self.data.append(item)

    def search(self, goal):
        results = []

        for d in self.data:
            if goal in d.get("goal", ""):
                results.append(d)

        results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        return results[:5]