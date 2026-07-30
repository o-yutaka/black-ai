from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class SelectorConfig:
    min_segment_rows: int = 96
    max_segment_rows: int = 512
    max_switches: int = 8
    boundary_quantile: float = 0.86
    max_boundaries: int = 64

    evidence_weight: float = 1.0
    switch_penalty: float = 0.45
    continuity_weight: float = 0.35
    slope_jump_weight: float = 0.70
    curvature_jump_weight: float = 0.30

    confidence_margin: float = 0.35
    blend_temperature: float = 0.30
    max_secondary_weight: float = 0.45

    prefix_min_points: int = 48
    prefix_bias_ridge: float = 20.0
    prefix_slope_ridge: float = 400.0
    prefix_huber_delta: float = 1.5
    prefix_iterations: int = 5

    gr_weight: float = 1.0
    pf_weight: float = 0.8
    geometry_weight: float = 0.35
    surface_weight: float = 0.25
    roughness_weight: float = 0.20
    epsilon: float = 1e-8

    def validate(self) -> None:
        if self.min_segment_rows < 2:
            raise ValueError("min_segment_rows must be >= 2")
        if self.max_segment_rows < self.min_segment_rows:
            raise ValueError("max_segment_rows must be >= min_segment_rows")
        if self.max_switches < 0:
            raise ValueError("max_switches must be non-negative")
        if not 0.0 < self.boundary_quantile < 1.0:
            raise ValueError("boundary_quantile must be in (0, 1)")
        if not 0.0 <= self.max_secondary_weight <= 0.5:
            raise ValueError("max_secondary_weight must be in [0, 0.5]")
        if self.blend_temperature <= 0:
            raise ValueError("blend_temperature must be > 0")


@dataclass(frozen=True)
class Segment:
    start: int
    end: int

    @property
    def rows(self) -> int:
        return self.end - self.start


@dataclass
class SelectionResult:
    trajectory: np.ndarray
    segments: list[Segment]
    candidate_path: np.ndarray
    segment_weights: np.ndarray
    segment_confidence: np.ndarray
    diagnostics: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "segments": [asdict(segment) for segment in self.segments],
            "candidate_path": self.candidate_path.astype(int).tolist(),
            "segment_weights": self.segment_weights.tolist(),
            "segment_confidence": self.segment_confidence.tolist(),
            "diagnostics": self.diagnostics,
        }


def as_2d(name: str, value: np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 2:
        raise ValueError(f"{name} must be 2-D, got shape={array.shape}")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def robust_scale(values: np.ndarray, epsilon: float = 1e-8) -> float:
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    finite = flat[np.isfinite(flat)]
    if finite.size == 0:
        return 1.0
    center = np.median(finite)
    scale = 1.4826 * np.median(np.abs(finite - center))
    if scale <= epsilon:
        scale = float(np.std(finite))
    return max(scale, 1.0, epsilon)


def rowwise_robust_z(values: np.ndarray, epsilon: float) -> np.ndarray:
    values = as_2d("evidence", values)
    center = np.median(values, axis=1, keepdims=True)
    mad = np.median(np.abs(values - center), axis=1, keepdims=True)
    z = (values - center) / np.maximum(1.4826 * mad, epsilon)
    return np.clip(z, -10.0, 10.0)


def softmax(values: np.ndarray, axis: int = -1) -> np.ndarray:
    shifted = values - np.max(values, axis=axis, keepdims=True)
    exp = np.exp(np.clip(shifted, -60.0, 60.0))
    return exp / np.maximum(exp.sum(axis=axis, keepdims=True), 1e-12)
