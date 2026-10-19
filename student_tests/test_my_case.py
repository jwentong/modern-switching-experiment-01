"""Independent cases with expectations derived in PREDICTIONS.md before running."""
from dataclasses import replace

import pytest

from src.metrics import summarize
from src.models import Arrival, Config
from src.utils import simulate


@pytest.mark.parametrize("mode,delay,wire", [("circuit", 2, 96), ("packet", 1, 128)])
def test_two_user_hand_calculation(mode, delay, wire):
    cfg = Config(users=2, ticks=2)
    raw = simulate([Arrival(0, 1, 96)], cfg, mode)
    metrics = summarize(raw, cfg)
    assert raw["completed"] == [dict(user=1, payload_bits=96, delay_ticks=delay)]
    assert raw["wire_sent_bits"] == wire
    assert metrics["payload_utilization"] == 0.375
    assert metrics["wire_utilization"] == wire / 256
    assert metrics["mean_delay_ms"] == metrics["max_delay_ms"] == delay
    assert metrics["loss_ratio"] == metrics["backlog_payload_bits"] == 0


@pytest.mark.parametrize("mode", ["circuit", "packet"])
def test_partial_record_reserves_full_payload_before_next_admission(mode):
    # t0 sends 128 bits, but the incomplete 200-bit record keeps ALL its quota.
    # At t1, 200 + 40 > 220, so the new record must be dropped before service.
    cfg = Config(users=2, ticks=2, buffer_payload_bits=220)
    raw = simulate([Arrival(0, 0, 200), Arrival(1, 1, 40)], cfg, mode)
    assert raw["generated_payload_bits"] == 240
    assert raw["dropped_payload_bits"] == 40
    assert raw["trace"][0]["buffer_payload_bits"] == 200
    metrics = summarize(raw, cfg)
    assert metrics["loss_ratio"] == pytest.approx(1 / 6)
    if mode == "circuit":
        assert raw["wire_sent_bits"] == 128
        assert raw["delivered_payload_bits"] == 0
        assert raw["backlog_payload_bits"] == 200
        assert metrics["mean_delay_ms"] is metrics["max_delay_ms"] is None
    else:
        assert raw["wire_sent_bits"] == 232
        assert raw["delivered_payload_bits"] == 200
        assert raw["backlog_payload_bits"] == 0
        assert raw["completed"] == [dict(user=0, payload_bits=200, delay_ticks=2)]
        assert metrics["mean_delay_ms"] == 2


def test_one_unsent_wire_bit_keeps_entire_record_in_backlog():
    # 225+32=257 wire bits; two ticks offer 256. Never count a partial delivery.
    cfg = Config(users=1, ticks=2)
    raw = simulate([Arrival(0, 0, 225)], cfg, "packet")
    metrics = summarize(raw, cfg)
    assert [row["wire_bits"] for row in raw["trace"]] == [128, 128]
    assert raw["completed"] == []
    assert raw["delivered_payload_bits"] == raw["dropped_payload_bits"] == 0
    assert metrics["backlog_payload_bits"] == 225
    assert metrics["wire_utilization"] == 1
    assert metrics["payload_utilization"] == metrics["loss_ratio"] == 0
    assert metrics["mean_delay_ms"] is metrics["max_delay_ms"] is None


@pytest.mark.parametrize("mode,delay", [("circuit", 2), ("packet", 1)])
def test_fractional_tick_duration_changes_only_delay_units(mode, delay):
    cfg = Config(users=2, ticks=2)
    traffic = [Arrival(0, 1, 96)]
    shorter = replace(cfg, tick_ms=0.125)
    raw = simulate(traffic, cfg, mode)
    assert simulate(traffic, shorter, mode) == raw
    metrics = summarize(raw, shorter)
    assert metrics["mean_delay_ms"] == metrics["max_delay_ms"] == delay * 0.125
    assert metrics["payload_utilization"] == 0.375


def test_zero_header_single_user_models_are_identical():
    cfg = Config(users=1, ticks=5, header_bits=0, buffer_payload_bits=400)
    traffic = [Arrival(0, 0, 200), Arrival(1, 0, 96), Arrival(1, 0, 16),
               Arrival(4, 0, 200)]
    circuit = simulate(traffic, cfg, "circuit")
    packet = simulate(traffic, cfg, "packet")
    assert circuit == packet
    assert circuit["generated_payload_bits"] == 512
    assert circuit["delivered_payload_bits"] == 312
    assert circuit["backlog_payload_bits"] == 200
    assert circuit["dropped_payload_bits"] == 0
    assert circuit["wire_sent_bits"] == 440
    assert summarize(circuit, cfg) == summarize(packet, cfg)
