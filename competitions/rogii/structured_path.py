from __future__ import annotations

from typing import Sequence

import numpy as np

from .core import Segment, SelectorConfig, robust_scale, rowwise_robust_z, softmax


def emission_costs(
    evidence: np.ndarray,
    segments: Sequence[Segment],
    config: SelectorConfig,
) -> np.ndarray:
    normalized = rowwise_robust_z(evidence, config.epsilon)
    costs = np.empty((len(segments), evidence.shape[1]), dtype=np.float64)
    for index, segment in enumerate(segments):
        local = normalized[segment.start : segment.end]
        costs[index] = -config.evidence_weight * (
            0.65 * np.mean(local, axis=0) + 0.35 * np.median(local, axis=0)
        )
    return costs


def _trajectory_scales(predictions: np.ndarray, epsilon: float) -> tuple[float, float, float]:
    value = robust_scale(np.std(predictions, axis=1), epsilon)
    slopes = np.diff(predictions, axis=0)
    slope = robust_scale(slopes, epsilon)
    curvature = np.diff(predictions, n=2, axis=0) if len(predictions) >= 3 else slopes
    return value, slope, robust_scale(curvature, epsilon)


def boundary_cost_matrix(
    predictions: np.ndarray,
    left: Segment,
    right: Segment,
    scales: tuple[float, float, float],
    config: SelectorConfig,
) -> np.ndarray:
    candidates = predictions.shape[1]
    value_scale, slope_scale, curve_scale = scales
    left_index, right_index = left.end - 1, right.start
    continuity = np.abs(
        predictions[left_index][:, None] - predictions[right_index][None, :]
    ) / value_scale
    left_slope = predictions[left_index] - predictions[max(left.start, left_index - 1)]
    right_slope = (
        predictions[min(right.end - 1, right_index + 1)] - predictions[right_index]
    )
    slope_jump = np.abs(left_slope[:, None] - right_slope[None, :]) / slope_scale

    def curvature_at(index: int) -> np.ndarray:
        if len(predictions) < 3 or index <= 0 or index >= len(predictions) - 1:
            return np.zeros(candidates)
        return predictions[index + 1] - 2.0 * predictions[index] + predictions[index - 1]

    curve_jump = np.abs(
        curvature_at(left_index)[:, None] - curvature_at(right_index)[None, :]
    ) / curve_scale
    switch = 1.0 - np.eye(candidates, dtype=np.float64)
    return (
        config.switch_penalty * switch
        + config.continuity_weight * continuity
        + config.slope_jump_weight * slope_jump
        + config.curvature_jump_weight * curve_jump
    )


def viterbi_path(
    predictions: np.ndarray,
    segments: Sequence[Segment],
    emission: np.ndarray,
    config: SelectorConfig,
) -> tuple[np.ndarray, float, list[np.ndarray]]:
    segment_count, candidate_count = emission.shape
    max_switches = min(config.max_switches, max(0, segment_count - 1))
    dp = np.full((segment_count, max_switches + 1, candidate_count), np.inf)
    prev_candidate = np.full_like(dp, -1, dtype=np.int32)
    prev_switches = np.full_like(dp, -1, dtype=np.int32)
    dp[0, 0] = emission[0]
    scales = _trajectory_scales(predictions, config.epsilon)
    transitions: list[np.ndarray] = []

    for segment_index in range(1, segment_count):
        transition = boundary_cost_matrix(
            predictions, segments[segment_index - 1], segments[segment_index], scales, config
        )
        transitions.append(transition)
        for switches in range(max_switches + 1):
            for current in range(candidate_count):
                for previous in range(candidate_count):
                    used = switches - int(previous != current)
                    if used < 0:
                        continue
                    cost = dp[segment_index - 1, used, previous] + transition[previous, current]
                    if cost < dp[segment_index, switches, current]:
                        dp[segment_index, switches, current] = cost
                        prev_candidate[segment_index, switches, current] = previous
                        prev_switches[segment_index, switches, current] = used
                dp[segment_index, switches, current] += emission[segment_index, current]

    flat = int(np.argmin(dp[-1]))
    switches, candidate = np.unravel_index(flat, dp[-1].shape)
    path = np.empty(segment_count, dtype=np.int32)
    path[-1] = candidate
    for segment_index in range(segment_count - 1, 0, -1):
        previous = prev_candidate[segment_index, switches, path[segment_index]]
        used = prev_switches[segment_index, switches, path[segment_index]]
        if previous < 0:
            raise RuntimeError("Viterbi backtrace failed")
        path[segment_index - 1] = previous
        switches = used
    return path, float(np.min(dp[-1])), transitions


def segment_blend_weights(
    emission: np.ndarray,
    path: np.ndarray,
    transitions: Sequence[np.ndarray],
    config: SelectorConfig,
) -> tuple[np.ndarray, np.ndarray]:
    segment_count, candidate_count = emission.shape
    weights = np.zeros((segment_count, candidate_count), dtype=np.float64)
    confidence = np.zeros(segment_count, dtype=np.float64)
    for segment_index in range(segment_count):
        adjusted = emission[segment_index].copy()
        if segment_index > 0:
            adjusted += transitions[segment_index - 1][path[segment_index - 1]]
        if segment_index + 1 < segment_count:
            adjusted += transitions[segment_index][:, path[segment_index + 1]]
        selected = int(path[segment_index])
        second = next(int(i) for i in np.argsort(adjusted) if i != selected)
        margin = float(adjusted[second] - adjusted[selected])
        confidence[segment_index] = margin
        weights[segment_index, selected] = 1.0
        if margin < config.confidence_margin:
            probability = softmax(
                (-np.array([adjusted[selected], adjusted[second]]) / config.blend_temperature)[None, :]
            )[0]
            secondary = min(float(probability[1]), config.max_secondary_weight)
            weights[segment_index, selected] = 1.0 - secondary
            weights[segment_index, second] = secondary
    return weights, confidence
