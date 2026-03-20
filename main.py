from thinking_engine import ThinkingEngine
from origin import Origin


# BLACKノード（複数）
engines = [
    ThinkingEngine(),
    ThinkingEngine(),
    ThinkingEngine()
]

origin = Origin(engines)


# 実行
result = origin.run("ビジネス拡大")

print(result)