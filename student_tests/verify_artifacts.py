"""Check exported values and parameter controls independently of grading."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics import summarize
from src.models import Config
from src.performance_test import SCENARIOS
from src.utils import make_traffic


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_raw(raw, cfg, scenario):
    assert raw["generated_payload_bits"] == sum(
        arrival.payload_bits for arrival in make_traffic(scenario, cfg, seed=2026))
    assert raw["generated_payload_bits"] == (
        raw["delivered_payload_bits"] + raw["dropped_payload_bits"]
        + raw["backlog_payload_bits"])
    assert raw["delivered_payload_bits"] == sum(r["payload_bits"] for r in raw["completed"])
    assert len(raw["trace"]) == cfg.ticks
    assert [r["tick"] for r in raw["trace"]] == list(range(cfg.ticks))
    assert raw["wire_sent_bits"] == sum(r["wire_bits"] for r in raw["trace"])
    assert raw["backlog_payload_bits"] == raw["trace"][-1]["buffer_payload_bits"]
    for row in raw["trace"]:
        assert type(row["wire_bits"]) is int and 0 <= row["wire_bits"] <= cfg.slot_bits
        assert 0 <= row["buffer_payload_bits"] <= cfg.buffer_payload_bits
    assert all(1 <= r["delay_ticks"] <= cfg.ticks for r in raw["completed"])


def check_csv(path, rows):
    with path.open(encoding="utf-8-sig", newline="") as file:
        actual = list(csv.DictReader(file))
    assert actual == [{k: "" if v is None else str(v) for k, v in row.items()} for row in rows]


def main():
    output = ROOT / "results"
    base = load(output / "comparison.json")
    cfg = Config(**base["config"])
    expected_keys = {f"{s}/{m}" for s in SCENARIOS for m in ("circuit", "packet")}
    assert set(base["traces"]) == expected_keys and len(base["rows"]) == 8
    base_rows = {f'{r["scenario"]}/{r["mode"]}': r for r in base["rows"]}
    assert set(base_rows) == expected_keys
    for key, raw in base["traces"].items():
        check_raw(raw, cfg, key.split("/")[0])
        assert {k: base_rows[key][k] for k in summarize(raw, cfg)} == summarize(raw, cfg)
    check_csv(output / "comparison.csv", base["rows"])
    checked = len(base["rows"])
    for name in ("header_scan", "buffer_scan"):
        extra = load(output / "extra" / f"{name}.json")
        parameter = extra["parameter"]
        assert len(extra["rows"]) == len(extra["values"]) * 8 == len(extra["traces"])
        for row in extra["rows"]:
            value = row[parameter]
            local_cfg = Config(**extra["configs"][str(value)])
            assert {k: v for k, v in vars(local_cfg).items() if k != parameter} == {
                k: v for k, v in vars(cfg).items() if k != parameter}
            key = f'{row["scenario"]}/{row["mode"]}'
            raw = extra["traces"][f"{value}/{key}"]
            check_raw(raw, local_cfg, row["scenario"])
            assert {k: row[k] for k in summarize(raw, local_cfg)} == summarize(raw, local_cfg)
            if value == getattr(cfg, parameter):
                assert raw == base["traces"][key]
            if parameter == "header_bits" and row["mode"] == "circuit":
                assert raw == base["traces"][key]
        check_csv(output / "extra" / f"{name}.csv", extra["rows"])
        checked += len(extra["rows"])

    names = ("comparison.json", "comparison.csv", "comparison_metrics.png",
             "queue_occupancy.png", "pcm_frame_view.png", "extra/header_scan.json",
             "extra/header_scan.csv", "extra/buffer_scan.json", "extra/buffer_scan.csv")
    hashes = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in names}
    receipt_path = output / "extra" / "verification.json"
    previous = load(receipt_path) if receipt_path.exists() else None
    unchanged = previous is not None and previous["sha256"] == hashes
    receipt = dict(python=platform.python_version(), seed=2026,
                   teaching_base_sha="bc9099e3f932168af640ce0d03abc2c3f283e10f",
                   checked_result_rows=checked, checks="passed", sha256=hashes,
                   consecutive_identical_runs=(previous["consecutive_identical_runs"] + 1
                                               if unchanged else 1))
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Validated {checked} rows/traces and matching CSVs; "
          f"identical artifact runs: {receipt['consecutive_identical_runs']}")


if __name__ == "__main__":
    main()
