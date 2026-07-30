from __future__ import annotations

from dataclasses import asdict
from typing import Sequence

import numpy as np

from .calibration import calibrate_candidates_from_prefix
from .core import Segment, SelectionResult, SelectorConfig, as_2d
from .evidence import build_local_evidence, scores_from_mapping
from .segmentation import detect_segments
from .structured_path import emission_costs, segment_blend_weights, viterbi_path


def select_segment_trajectory(
    candidate_predictions: np.ndarray,
    local_evidence: np.ndarray,
    *,
    config: SelectorConfig | None = None,
    candidate_names: Sequence[str] | None = None,
    observed_tvt: np.ndarray | None = None,
    visible_prefix_mask: np.ndarray | None = None,
) -> SelectionResult:
    """Select the right candidate in the right segment without hidden targets."""
    config = config or SelectorConfig()
    config.validate()
    predictions = as_2d("candidate_predictions", candidate_predictions)
    evidence = as_2d("local_evidence", local_evidence)
    if predictions.shape != evidence.shape:
        raise ValueError("candidate_predictions and local_evidence shape mismatch")
    rows, candidates = predictions.shape
    names = (
        list(candidate_names)
        if candidate_names is not None
        else [f"candidate_{index}" for index in range(candidates)]
    )
    if len(names) != candidates or len(set(names)) != candidates:
        raise ValueError("candidate_names must be unique and match candidate count")

    prefix_report = None
    if observed_tvt is not None or visible_prefix_mask is not None:
        if observed_tvt is None or visible_prefix_mask is None:
            raise ValueError("observed_tvt and visible_prefix_mask must be supplied together")
        predictions, prefix_report = calibrate_candidates_from_prefix(
            predictions, observed_tvt, visible_prefix_mask, config=config
        )

    segments = detect_segments(predictions, evidence, config=config)
    emission = emission_costs(evidence, segments, config)
    path, best_cost, transitions = viterbi_path(
        predictions, segments, emission, config
    )
    weights, confidence = segment_blend_weights(
        emission, path, transitions, config
    )
    trajectory = np.empty(rows, dtype=np.float64)
    for index, segment in enumerate(segments):
        trajectory[segment.start : segment.end] = (
            predictions[segment.start : segment.end] @ weights[index]
        )
    if not np.isfinite(trajectory).all():
        raise RuntimeError("selected trajectory contains non-finite values")
    diagnostics: dict[str, object] = {
        "rows": rows,
        "candidate_count": candidates,
        "candidate_names": names,
        "segment_count": len(segments),
        "switch_count": int(np.sum(path[1:] != path[:-1])),
        "max_switches": config.max_switches,
        "best_path_cost": best_cost,
        "selected_candidates": [names[int(index)] for index in path],
        "low_confidence_segments": int(
            np.sum(confidence < config.confidence_margin)
        ),
        "target_leakage_guard": {
            "hidden_targets_used": False,
            "prefix_calibration_enabled": prefix_report is not None,
        },
        "prefix_calibration": prefix_report,
        "config": asdict(config),
    }
    return SelectionResult(
        trajectory=trajectory,
        segments=list(segments),
        candidate_path=path,
        segment_weights=weights,
        segment_confidence=confidence,
        diagnostics=diagnostics,
    )


__all__ = [
    "Segment",
    "SelectionResult",
    "SelectorConfig",
    "build_local_evidence",
    "calibrate_candidates_from_prefix",
    "detect_segments",
    "scores_from_mapping",
    "select_segment_trajectory",
]
