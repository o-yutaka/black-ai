class Scorer:

    def score(self, sim_result):

        success = sim_result["success"]
        risk = sim_result["risk"]
        weight = sim_result["strategy"]["weight"]

        # ------------------------
        # 基本スコア
        # ------------------------

        score = 0

        # 成功（重視）
        score += success * 0.5

        # リスク（減点）
        score += (1 - risk) * 0.3

        # 戦略の強さ
        score += weight * 0.2

        return score


    # ------------------------
    # マルチスコア（長期）
    # ------------------------
    def score_multi(self, sim_result):

        success = sim_result["avg_success"]
        risk = sim_result["avg_risk"]
        weight = sim_result["strategy"]["weight"]

        score = 0

        score += success * 0.4
        score += (1 - risk) * 0.3
        score += weight * 0.3

        return score


    # ------------------------
    # 正規化（比較しやすく）
    # ------------------------
    def normalize(self, scores):

        max_score = max(scores)

        return [s / max_score for s in scores]