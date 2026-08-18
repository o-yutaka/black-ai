from __future__ import annotations

import concurrent.futures
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable


@dataclass
class Candidate:
    arm: str
    messages: list[str]
    trace: dict[str, Any] | None = None
    replay_ok: bool = False
    score: float = 0.0


@dataclass
class RunRecord:
    arm: str
    elapsed_s: float
    candidate_count: int
    replay_ok: int
    best_score: float
    error: str | None = None


def _run_arm(name: str, factory: Callable[[], list[Candidate]]) -> tuple[list[Candidate], RunRecord]:
    started = time.perf_counter()
    try:
        candidates = factory()
        valid = [c for c in candidates if c.replay_ok]
        best = max((c.score for c in valid), default=0.0)
        return candidates, RunRecord(name, time.perf_counter() - started, len(candidates), len(valid), best)
    except Exception as exc:
        return [], RunRecord(name, time.perf_counter() - started, 0, 0, 0.0, repr(exc))


def run_parallel(arms: dict[str, Callable[[], list[Candidate]]], workers: int | None = None) -> dict[str, Any]:
    workers = workers or min(len(arms), os.cpu_count() or 1)
    all_candidates: list[Candidate] = []
    records: list[RunRecord] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_run_arm, name, fn) for name, fn in arms.items()]
        for future in concurrent.futures.as_completed(futures):
            candidates, record = future.result()
            all_candidates.extend(candidates)
            records.append(record)

    # Evidence-first ranking: reproducibility, measured score, then diversity signature.
    all_candidates.sort(key=lambda c: (c.replay_ok, c.score, len(set(c.messages))), reverse=True)
    selected: list[Candidate] = []
    seen: set[tuple[str, ...]] = set()
    for candidate in all_candidates:
        signature = tuple(candidate.messages)
        if signature in seen:
            continue
        seen.add(signature)
        selected.append(candidate)
        if len(selected) >= 2000:
            break

    return {
        "records": [asdict(r) for r in sorted(records, key=lambda r: r.best_score, reverse=True)],
        "candidate_count": len(all_candidates),
        "selected_count": len(selected),
        "candidates": [asdict(c) for c in selected],
    }


def save_result(result: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
