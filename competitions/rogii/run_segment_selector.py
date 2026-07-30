from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from competitions.rogii.segment_selector import (
    SelectorConfig,
    build_local_evidence,
    select_segment_trajectory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run target-safe segment-level structured candidate selection."
    )
    parser.add_argument("--input", type=Path, required=True, help="NPZ candidate bundle")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    return parser.parse_args()


def load_config(path: Path | None) -> SelectorConfig:
    if path is None:
        return SelectorConfig()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SelectorConfig(**payload)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    config.validate()
    bundle = np.load(args.input, allow_pickle=False)
    predictions = bundle["candidate_predictions"]
    if "local_evidence" in bundle:
        evidence = bundle["local_evidence"]
    else:
        evidence = build_local_evidence(
            predictions,
            gr_score=bundle["gr_score"] if "gr_score" in bundle else None,
            pf_score=bundle["pf_score"] if "pf_score" in bundle else None,
            geometry_score=bundle["geometry_score"] if "geometry_score" in bundle else None,
            surface_score=bundle["surface_score"] if "surface_score" in bundle else None,
            config=config,
        )
    names = (
        [str(value) for value in bundle["candidate_names"]]
        if "candidate_names" in bundle
        else None
    )
    observed = bundle["observed_tvt"] if "observed_tvt" in bundle else None
    visible = bundle["visible_prefix_mask"] if "visible_prefix_mask" in bundle else None
    result = select_segment_trajectory(
        predictions,
        evidence,
        config=config,
        candidate_names=names,
        observed_tvt=observed,
        visible_prefix_mask=visible,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "selected_trajectory.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["row", "tvt"])
        writer.writerows(enumerate(result.trajectory.tolist()))
    (args.output_dir / "segment_report.json").write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    np.save(args.output_dir / "segment_weights.npy", result.segment_weights)
    print(json.dumps(result.diagnostics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
