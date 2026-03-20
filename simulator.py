import random


class Simulator:

    def simulate(self, strategy):

        base_success = 1.0
        base_risk = 0.3

        # タイプ取得
        s_type = strategy["type"]

        # -------------------------
        # 戦略ごとの影響
        # -------------------------

        if "extreme" in s_type:
            success = base_success * 1.4
            risk = base_risk * 2.0

        elif "hybrid" in s_type:
            success = base_success * 1.2
            risk = base_risk * 1.2

        elif "adaptive" in s_type:
            success = base_success * 1.3
            risk = base_risk * 1.0

        elif "inverse" in s_type:
            success = base_success * 0.8
            risk = base_risk * 0.7

        else:
            success = base_success
            risk = base_risk

        # -------------------------
        # ランダム揺れ（現実性）
        # -------------------------

        success *= random.uniform(0.8, 1.2)
        risk *= random.uniform(0.8, 1.2)

        return {
            "strategy": strategy,
            "success": success,
            "risk": risk
        }


    # -------------------------
    # マルチステップ（未来）
    # -------------------------
    def simulate_multi(self, strategy, steps=3):

        total_success = 0
        total_risk = 0

        current = strategy.copy()

        for _ in range(steps):

            result = self.simulate(current)

            total_success += result["success"]
            total_risk += result["risk"]

        return {
            "strategy": strategy,
            "avg_success": total_success / steps,
            "avg_risk": total_risk / steps
        }