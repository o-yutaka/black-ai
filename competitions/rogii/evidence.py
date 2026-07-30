from __future__ import annotations

from typing import Mapping

import numpy as np

from .core import SelectorConfig, as_2d, rowwise_robust_z


def candidate_roughness_score(candidate_predictions: np.ndarray) -> np.ndarray:
    predictions = as_2d("candidate_predictions", candidate_predictions)
    curvature = np.zeros_like(predictions)
    if len(predictions) >= 3:
        curvature[1:-1] = np.diff(predictions, n=2, axis=0)
        curvature[0] = curvature[1]
        curvature[-1] = curvature[-2]
    scale = np.maximum(np.median(np.abs(curvature), axis=0, keepdims=True), 1e-6)
    return -np.abs(curvature) / scale


def build_local_evidence(
    candidate_predictions: np.ndarray,
    *,
    gr_score: np.ndarray | None = None,
    pf_score: np.ndarray | None = None,
    geometry_score: np.ndarray | None = None,
    surface_score: np.ndarray | None = None,
    roughness_score: np.ndarray | None = None,
    config: SelectorConfig | None = None,
) -> np.ndarray:
    """Fuse target-safe inference evidence. Higher values are better."""
    config = config or SelectorConfig()
    config.validate()
    predictions = as_2d("candidate_predictions", candidate_predictions)
    evidence = np.zeros_like(predictions)
    sources = [
        (gr_score, config.gr_weight, "gr_score"),
        (pf_score, config.pf_weight, "pf_score"),
        (geometry_score, config.geometry_weight, "geometry_score"),
        (surface_score, config.surface_weight, "surface_score"),
    ]
    for source, weight, name in sources:
        if source is None or weight == 0:
            continue
        array = as_2d(name, source)
        if array.shape != predictions.shape:
            raise ValueError(f"{name} shape {array.shape} != {predictions.shape}")
        evidence += weight * rowwise_robust_z(array, config.epsilon)
    roughness = (
        candidate_roughness_score(predictions)
        if roughness_score is None
        else as_2d("roughness_score", roughness_score)
    )
    if roughness.shape != predictions.shape:
        raise ValueError("roughness_score shape mismatch")
    evidence += config.roughness_weight * rowwise_robust_z(
        roughness, config.epsilon
    )
    return evidence


def scores_from_mapping(
    candidate_predictions: np.ndarray,
    score_sources: Mapping[str, np.ndarray],
    *,
    config: SelectorConfig | None = None,
) -> np.ndarray:
    return build_local_evidence(
        candidate_predictions,
        gr_score=score_sources.get("gr"),
        pf_score=score_sources.get("pf"),
        geometry_score=score_sources.get("geometry"),
        surface_score=score_sources.get("surface"),
        roughness_score=score_sources.get("roughness"),
        config=config,
    )
