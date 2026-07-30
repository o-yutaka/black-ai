from __future__ import annotations

import numpy as np

from .core import SelectorConfig, as_2d, robust_scale


def calibrate_candidates_from_prefix(
    candidate_predictions: np.ndarray,
    observed_tvt: np.ndarray,
    visible_prefix_mask: np.ndarray,
    *,
    config: SelectorConfig | None = None,
) -> tuple[np.ndarray, list[dict[str, float]]]:
    """Correct candidate datum+slope using visible prefix rows only."""
    config = config or SelectorConfig()
    config.validate()
    predictions = as_2d("candidate_predictions", candidate_predictions)
    observed = np.asarray(observed_tvt, dtype=np.float64)
    mask = np.asarray(visible_prefix_mask, dtype=bool)
    if observed.shape != (len(predictions),) or mask.shape != observed.shape:
        raise ValueError("observed_tvt and visible_prefix_mask must match row count")
    valid = mask & np.isfinite(observed)
    if int(valid.sum()) < config.prefix_min_points:
        return predictions.copy(), [
            {"bias": 0.0, "slope_delta": 0.0, "used_points": int(valid.sum())}
            for _ in range(predictions.shape[1])
        ]

    calibrated = predictions.copy()
    reports: list[dict[str, float]] = []
    penalty = np.diag(
        [config.prefix_bias_ridge, config.prefix_slope_ridge]
    ).astype(np.float64)
    for candidate in range(predictions.shape[1]):
        x = predictions[valid, candidate]
        y = observed[valid]
        center = float(np.median(x))
        design = np.column_stack([np.ones(len(x)), x - center])
        target = y - x
        weights = np.ones(len(x), dtype=np.float64)
        beta = np.zeros(2, dtype=np.float64)
        for _ in range(config.prefix_iterations):
            sqrt_w = np.sqrt(weights)
            weighted = design * sqrt_w[:, None]
            beta = np.linalg.solve(
                weighted.T @ weighted + penalty,
                weighted.T @ (target * sqrt_w),
            )
            residual = target - design @ beta
            threshold = config.prefix_huber_delta * robust_scale(
                residual, config.epsilon
            )
            weights = np.ones_like(residual)
            large = np.abs(residual) > threshold
            weights[large] = threshold / np.maximum(np.abs(residual[large]), 1e-12)
        correction = beta[0] + beta[1] * (predictions[:, candidate] - center)
        calibrated[:, candidate] += correction
        reports.append(
            {
                "bias": float(beta[0]),
                "slope_delta": float(beta[1]),
                "used_points": int(valid.sum()),
                "prefix_rmse_before": float(np.sqrt(np.mean((x - y) ** 2))),
                "prefix_rmse_after": float(
                    np.sqrt(np.mean((calibrated[valid, candidate] - y) ** 2))
                ),
            }
        )
    return calibrated, reports
