from __future__ import annotations

import numpy as np

from .core import (
    Segment,
    SelectorConfig,
    as_2d,
    robust_scale,
    rowwise_robust_z,
    softmax,
)


def detect_segments(
    candidate_predictions: np.ndarray,
    local_evidence: np.ndarray,
    *,
    config: SelectorConfig | None = None,
) -> list[Segment]:
    """Detect target-free change points and enforce segment size constraints."""
    config = config or SelectorConfig()
    config.validate()
    predictions = as_2d("candidate_predictions", candidate_predictions)
    evidence = as_2d("local_evidence", local_evidence)
    if predictions.shape != evidence.shape:
        raise ValueError("candidate_predictions and local_evidence shape mismatch")
    rows, candidates = predictions.shape
    if rows == 0 or candidates < 2:
        raise ValueError("at least one row and two candidates are required")
    if rows <= config.max_segment_rows:
        return [Segment(0, rows)]

    normalized = rowwise_robust_z(evidence, config.epsilon)
    order = np.argsort(normalized, axis=1)
    winner = order[:, -1]
    top = normalized[np.arange(rows), order[:, -1]]
    second = normalized[np.arange(rows), order[:, -2]]
    margin = top - second
    posterior = softmax(normalized)
    entropy = -np.sum(posterior * np.log(np.maximum(posterior, 1e-12)), axis=1)
    dispersion = np.std(predictions, axis=1)

    strength = np.zeros(rows, dtype=np.float64)
    strength[1:] += 3.0 * (winner[1:] != winner[:-1])
    for signal, weight in ((margin, 1.0), (entropy, 1.0), (dispersion, 0.8)):
        gradient = np.abs(np.diff(signal, prepend=signal[0]))
        strength += weight * np.clip(
            gradient / robust_scale(gradient, config.epsilon), 0.0, 10.0
        )
    strength[: config.min_segment_rows] = 0.0
    strength[max(0, rows - config.min_segment_rows) :] = 0.0

    positive = strength[strength > 0]
    threshold = (
        float(np.quantile(positive, config.boundary_quantile))
        if positive.size
        else np.inf
    )
    ranked = sorted(
        np.flatnonzero(strength >= threshold).tolist(),
        key=lambda index: (-strength[index], index),
    )
    selected = [0, rows]
    for index in ranked:
        if len(selected) - 2 >= config.max_boundaries:
            break
        if all(abs(index - boundary) >= config.min_segment_rows for boundary in selected):
            selected.append(int(index))
    selected = sorted(set(selected))

    expanded = [selected[0]]
    for left, right in zip(selected[:-1], selected[1:]):
        gap = right - left
        if gap > config.max_segment_rows:
            parts = int(np.ceil(gap / config.max_segment_rows))
            expanded.extend(
                left + int(round(part * gap / parts))
                for part in range(1, parts)
            )
        expanded.append(right)
    boundaries = sorted(set(expanded))
    return [
        Segment(int(start), int(end))
        for start, end in zip(boundaries[:-1], boundaries[1:])
        if end > start
    ]
