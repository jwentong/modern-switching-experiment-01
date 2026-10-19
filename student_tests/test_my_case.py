"""Independent boundary expectations, calculated before running the implementation.

These tests were proposed by the AI assistant; student review is still required.
"""
import pytest

from src.metrics import summarize
from src.models import Arrival, Config
from src.utils import simulate


@pytest.mark.parametrize(
    "mode, wire_utilization, delay_ms",
    [("circuit", 96 / 256, 2), ("packet", 128 / 256, 1)],
)
def test_two_user_hand_calculation(mode, wire_utilization, delay_ms):
    # Circuit: idle at tick 0, then sends 96 at tick 1, delivery at 2 ms.
    # Packet: sends 96 + 32 at tick 0, delivery at 1 ms.
    cfg = Config(users=2, ticks=2)
    raw = simulate([Arrival(0, 1, 96)], cfg, mode)
    result = summarize(raw, cfg)
    assert result["payload_utilization"] == pytest.approx(96 / 256)
    assert result["wire_utilization"] == pytest.approx(wire_utilization)
    assert result["mean_delay_ms"] == delay_ms
    assert result["max_delay_ms"] == delay_ms
    assert result["loss_ratio"] == 0
    assert result["backlog_payload_bits"] == 0


def test_partial_packet_is_all_backlog_and_has_no_delivery_sample():
    # One tick sends 128 of 232 wire bits; no whole payload is delivered.
    cfg = Config(users=1, ticks=1)
    raw = simulate([Arrival(0, 0, 200)], cfg, "packet")
    result = summarize(raw, cfg)
    assert raw["wire_sent_bits"] == 128
    assert raw["completed"] == []
    assert raw["delivered_payload_bits"] == 0
    assert raw["generated_payload_bits"] == raw["backlog_payload_bits"] == 200
    assert result["payload_utilization"] == 0
    assert result["wire_utilization"] == 1
    assert result["mean_delay_ms"] is None
    assert result["max_delay_ms"] is None


@pytest.mark.parametrize("mode, expected_wire", [("circuit", 160), ("packet", 192)])
def test_partial_record_keeps_full_buffer_reservation_until_delivery(mode, expected_wire):
    # Buffer=200. At tick 0, payload 160 is admitted and partly sent.
    # At tick 1, 160 is STILL reserved, so arriving payload 80 is dropped.
    # Only afterwards does service finish the first record at boundary 2.
    # Releasing sent fragments early would incorrectly admit the 80-bit record.
    cfg = Config(users=1, ticks=2, buffer_payload_bits=200)
    raw = simulate([Arrival(0, 0, 160), Arrival(1, 0, 80)], cfg, mode)
    result = summarize(raw, cfg)
    assert raw["trace"][0]["buffer_payload_bits"] == 160
    assert raw["generated_payload_bits"] == 240
    assert raw["delivered_payload_bits"] == 160
    assert raw["dropped_payload_bits"] == 80
    assert raw["backlog_payload_bits"] == 0
    assert raw["wire_sent_bits"] == expected_wire
    assert len(raw["completed"]) == 1
    assert result["loss_ratio"] == pytest.approx(1 / 3)
    assert result["mean_delay_ms"] == result["max_delay_ms"] == 2


def test_packet_completed_at_window_end_is_included():
    # Arrival at tick 1 completes at boundary 2, exactly the end of [0,2).
    # Delay is one service tick (2 - 1), not zero and not two.
    cfg = Config(users=2, ticks=2)
    raw = simulate([Arrival(1, 1, 96)], cfg, "packet")
    result = summarize(raw, cfg)
    assert raw["delivered_payload_bits"] == 96
    assert result["mean_delay_ms"] == 1
    assert result["backlog_payload_bits"] == 0


def test_fractional_tick_duration_scales_completion_delay():
    # The same two-user arrival takes two circuit ticks, each lasting 0.5 ms.
    cfg = Config(users=2, ticks=2, tick_ms=0.5)
    result = summarize(simulate([Arrival(0, 1, 96)], cfg, "circuit"), cfg)
    assert result["mean_delay_ms"] == result["max_delay_ms"] == 1
