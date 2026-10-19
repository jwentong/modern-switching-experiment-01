"""学生自拟反例：验证固定时隙不借用，以及分组FIFO跨tick填满预算。"""
from collections import deque

from src.models import Config, Pending
from src.part1_circuit import serve_circuit
from src.part2_packet import serve_packet


def test_circuit_cannot_borrow_idle_slot():
    """tick 0属于用户0；即使用户1有数据，也不能借用用户0的空时隙。"""
    waiting = Pending(user=1, arrival_tick=0, payload_bits=96, remaining_wire_bits=96)
    queues = [deque(), deque([waiting])]
    cfg = Config(users=2, ticks=2, slot_bits=128, tick_ms=1.0, header_bits=32)

    wire_bits, completed = serve_circuit(queues, tick=0, cfg=cfg)

    assert wire_bits == 0
    assert completed == []
    assert list(queues[1]) == [waiting]
    assert waiting.remaining_wire_bits == 96


def test_packet_fifo_budget_continuation():
    """AC04：A剩232 bit、B剩64 bit，128 bit/tick。

    手算：
    - tick 0：发送A 128，A剩104；B保持64；无完成。
    - tick 1：发送A 104，A完成；剩余24发B，B剩40。
    因此tick 1实际发送128 bit，完成列表只有A。
    """
    a = Pending(user=0, arrival_tick=0, payload_bits=200, remaining_wire_bits=232)
    b = Pending(user=1, arrival_tick=0, payload_bits=32, remaining_wire_bits=64)
    queue = deque([a, b])
    cfg = Config(users=2, ticks=2, slot_bits=128, tick_ms=1.0, header_bits=32)

    wire_bits, completed = serve_packet(queue, tick=0, cfg=cfg)
    assert wire_bits == 128
    assert completed == []
    assert a.remaining_wire_bits == 104
    assert b.remaining_wire_bits == 64

    wire_bits, completed = serve_packet(queue, tick=1, cfg=cfg)
    assert wire_bits == 128
    assert completed == [a]
    assert list(queue) == [b]
    assert b.remaining_wire_bits == 40
