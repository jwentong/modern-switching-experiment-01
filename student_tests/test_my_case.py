"""自拟反例：共享 FIFO 不得让后续记录抢占未完成队首。"""

from collections import deque

from src.models import Config, Pending
from src.part2_packet import serve_packet


def test_shared_fifo_does_not_interleave_large_head_record():
    """A 需跨 tick 续传；B 在 A 完成前必须保持不动。"""
    cfg = Config(users=2, ticks=2, slot_bits=128, tick_ms=1.0, header_bits=32)
    first = Pending(user=0, arrival_tick=0, payload_bits=200, remaining_wire_bits=232)
    second = Pending(user=1, arrival_tick=0, payload_bits=32, remaining_wire_bits=64)
    queue = deque([first, second])

    wire_0, completed_0 = serve_packet(queue, tick=0, cfg=cfg)
    assert wire_0 == 128
    assert completed_0 == []
    assert list(queue) == [first, second]
    assert first.remaining_wire_bits == 104
    assert second.remaining_wire_bits == 64

    wire_1, completed_1 = serve_packet(queue, tick=1, cfg=cfg)
    assert wire_1 == 128
    assert completed_1 == [first]
    assert list(queue) == [second]
    assert first.remaining_wire_bits == 0
    assert second.remaining_wire_bits == 40
