"""Reproduce parameter scans without changing the teacher's baseline runner.

Run from the repository root: .venv/Scripts/python.exe student_tests/run_extra.py
"""
import csv
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import summarize
from src.models import Config
from src.performance_test import SCENARIOS
from src.utils import make_traffic, simulate


def run_scan(parameter, values, output):
    baseline = Config()
    rows, traces = [], {}
    configs = {}
    for value in values:
        cfg = replace(baseline, **{parameter: value})
        configs[str(value)] = asdict(cfg)
        for scenario in SCENARIOS:
            arrivals = make_traffic(scenario, cfg, seed=2026)
            for mode in ("circuit", "packet"):
                raw = simulate(arrivals, cfg, mode)
                rows.append({parameter: value, "scenario": scenario, "mode": mode,
                             **summarize(raw, cfg)})
                traces[f"{value}/{scenario}/{mode}"] = raw
    name = "header_scan" if parameter == "header_bits" else "buffer_scan"
    obj = dict(parameter=parameter, values=values, seed=2026, configs=configs,
               rows=rows, traces=traces)
    (output / f"{name}.json").write_text(
        json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{name}: {len(rows)} rows, {len(traces)} traces")


if __name__ == "__main__":
    destination = ROOT / "results" / "extra"
    destination.mkdir(parents=True, exist_ok=True)
    run_scan("header_bits", [0, 16, 32, 64, 128], destination)
    run_scan("buffer_payload_bits", [512, 1024, 4096, 8192], destination)
