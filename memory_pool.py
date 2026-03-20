class MemoryPool:

    def __init__(self):
        self.data = []

    # ------------------------
    # 保存
    # ------------------------
    def store(self, item):
        self.data.append(item)

    # ------------------------
    # 検索（簡易）
    # ------------------------
    def search(self, goal):

        results = []

        for d in self.data:
            if goal in d.get("goal", ""):
                results.append(d)

        return results[-5:]  # 最新5件