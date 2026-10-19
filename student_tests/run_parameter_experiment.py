"""Reproduce the header_bits=0 comparison without changing baseline results.

Run from the repository root:
    .venv/Scripts/python.exe student_tests/run_parameter_experiment.py
"""
import csv
import json
from dataclasses import asdict, replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from src.metrics import summarize
from src.models import Config
from src.performance_test import SCENARIOS
from src.utils import make_traffic, simulate


def main():
    cfg = replace(Config(), header_bits=0)
    rows, traces = [], {}
    for scenario in SCENARIOS:
        arrivals = make_traffic(scenario, cfg, seed=2026)
        for mode in ("circuit", "packet"):
            raw = simulate(arrivals, cfg, mode)
            rows.append(dict(scenario=scenario, mode=mode, **summarize(raw, cfg)))
            traces[f"{scenario}/{mode}"] = raw

    output = ROOT / "results" / "extra"
    output.mkdir(parents=True, exist_ok=True)
    data = dict(
        experiment="header_bits_0",
        changed_parameter="header_bits",
        baseline_value=32,
        seed=2026,
        config=asdict(cfg),
        rows=rows,
        traces=traces,
    )
    (output / "header_bits_0.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (output / "header_bits_0.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Generated results/extra/header_bits_0.json and header_bits_0.csv")


if __name__ == "__main__":
    main()
