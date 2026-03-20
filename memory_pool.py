class MemoryPool:

    def __init__(self):
        self.data = []

    def store(self, item):
        self.data.append(item)

    def search(self, goal):

        results = []

        for d in self.data:
            if goal in str(d):
                results.append(d)

        return results[:5]