"""张志伟 2024280016 的自拟反例。

两个测试都在调用发送函数前写出手算预期，并检查发送预算、FIFO、
跨 tick 续传和“部分发送不得误记交付”等模型合同。
"""
from collections import deque

from src.models import Config, Pending
from src.part1_circuit import serve_circuit
from src.part2_packet import serve_packet


def test_circuit_does_not_borrow_and_defers_partial_delivery():
    """tick 0 是用户 0 的时隙，即使用户 1 排队也不得借用。

    用户 1 在 tick 1 获得 100 bit；首记录 150 bit 只能发送 100，
    因此不得交付。tick 2 不服务用户 1；tick 3 先完成首记录，
    再用剩余预算发送第二条 60 bit 中的 50 bit。
    """
    cfg = Config(users=2, ticks=4, slot_bits=100)
    first = Pending(1, 0, 150, 150)
    second = Pending(1, 0, 60, 60)
    queues = [deque(), deque([first, second])]

    assert serve_circuit(queues, 0, cfg) == (0, [])
    assert first.remaining_wire_bits == 150
    assert serve_circuit(queues, 1, cfg) == (100, [])
    assert first.remaining_wire_bits == 50
    assert len(queues[1]) == 2
    assert serve_circuit(queues, 2, cfg) == (0, [])

    wire_bits, completed = serve_circuit(queues, 3, cfg)
    assert wire_bits == 100
    assert completed == [first]
    assert list(queues[1]) == [second]
    assert second.remaining_wire_bits == 10


def test_packet_cross_tick_keeps_original_header_cost():
    """分组 200 bit 加 32 bit 包头，首次发送后应保留 104 bit。

    下一 tick 必须继续该分组，完成后才能发送后一项；若实现每 tick
    重加包头或交错队列，本测试的剩余量和完成列表会失败。
    """
    cfg = Config(slot_bits=128, header_bits=32)
    first = Pending(0, 0, 200, 232)
    second = Pending(0, 0, 16, 48)
    queue = deque([first, second])

    assert serve_packet(queue, 0, cfg) == (128, [])
    assert first.remaining_wire_bits == 104
    assert list(queue) == [first, second]

    wire_bits, completed = serve_packet(queue, 1, cfg)
    assert wire_bits == 128
    assert completed == [first]
    assert list(queue) == [second]
    assert second.remaining_wire_bits == 24
