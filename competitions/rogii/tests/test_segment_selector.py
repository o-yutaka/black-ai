from __future__ import annotations

import numpy as np

from competitions.rogii.segment_selector import (
    SelectorConfig,
    calibrate_candidates_from_prefix,
    select_segment_trajectory,
)


def _synthetic_case(rows: int = 720) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.linspace(0.0, 14.0, rows)
    truth = 12000.0 + 7.5 * np.sin(x) + 0.22 * np.arange(rows)
    candidates = np.column_stack(
        [
            truth + np.where(np.arange(rows) < 240, 0.10, 7.0),
            truth
            + np.where(
                (np.arange(rows) >= 240) & (np.arange(rows) < 480),
                -0.12,
                -6.5,
            ),
            truth + np.where(np.arange(rows) >= 480, 0.08, 8.0),
        ]
    )
    evidence = np.full_like(candidates, -2.0)
    evidence[:240, 0] = 5.0
    evidence[240:480, 1] = 5.0
    evidence[480:, 2] = 5.0
    evidence += np.random.default_rng(11).normal(0.0, 0.12, evidence.shape)
    return truth, candidates, evidence


def test_segment_selector_beats_every_single_candidate() -> None:
    truth, candidates, evidence = _synthetic_case()
    config = SelectorConfig(
        min_segment_rows=72,
        max_segment_rows=280,
        max_switches=4,
        switch_penalty=0.15,
        continuity_weight=0.10,
        slope_jump_weight=0.15,
        curvature_jump_weight=0.05,
    )
    result = select_segment_trajectory(candidates, evidence, config=config)
    selected_rmse = float(np.sqrt(np.mean((result.trajectory - truth) ** 2)))
    single_rmse = np.sqrt(np.mean((candidates - truth[:, None]) ** 2, axis=0))
    assert selected_rmse < float(single_rmse.min()) * 0.30
    assert result.diagnostics["switch_count"] <= config.max_switches
    assert len(set(result.candidate_path.tolist())) == 3


def test_switch_limit_is_enforced() -> None:
    _, candidates, evidence = _synthetic_case()
    result = select_segment_trajectory(
        candidates,
        evidence,
        config=SelectorConfig(
            min_segment_rows=64,
            max_segment_rows=180,
            max_switches=1,
            switch_penalty=0.0,
            continuity_weight=0.0,
            slope_jump_weight=0.0,
            curvature_jump_weight=0.0,
        ),
    )
    assert int(np.sum(result.candidate_path[1:] != result.candidate_path[:-1])) <= 1


def test_prefix_calibration_removes_datum_and_slope_bias() -> None:
    rows = 400
    base = 11800.0 + np.linspace(0.0, 100.0, rows)
    truth = base + 4.0 + 0.025 * (base - np.median(base))
    candidates = np.column_stack([base, base + 8.0])
    visible = np.zeros(rows, dtype=bool)
    visible[:160] = True
    calibrated, report = calibrate_candidates_from_prefix(
        candidates,
        truth,
        visible,
        config=SelectorConfig(
            prefix_min_points=32,
            prefix_bias_ridge=0.01,
            prefix_slope_ridge=0.01,
        ),
    )
    before = float(np.sqrt(np.mean((candidates[:, 0] - truth) ** 2)))
    after = float(np.sqrt(np.mean((calibrated[:, 0] - truth) ** 2)))
    assert after < before * 0.05
    assert report[0]["prefix_rmse_after"] < report[0]["prefix_rmse_before"]


def test_low_confidence_segments_use_valid_top2_blend() -> None:
    rows = 300
    truth = 100.0 + np.linspace(0, 5, rows)
    candidates = np.column_stack([truth - 1.0, truth + 1.0, truth + 8.0])
    evidence = np.column_stack(
        [np.zeros(rows), np.full(rows, -0.01), np.full(rows, -5.0)]
    )
    result = select_segment_trajectory(
        candidates,
        evidence,
        config=SelectorConfig(
            min_segment_rows=64,
            max_segment_rows=512,
            confidence_margin=2.0,
            max_secondary_weight=0.45,
        ),
    )
    assert np.allclose(result.segment_weights.sum(axis=1), 1.0)
    assert np.all(result.segment_weights >= 0.0)
    assert np.max(np.sum(result.segment_weights > 0, axis=1)) == 2
    assert np.isfinite(result.trajectory).all()
