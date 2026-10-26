"""
自拟反例测试：电路交换不允许借用空闲时隙
场景：2用户，tick=0 → 当前服务用户 = 0 % 2 = 0
用户0队列为空，用户1队列里面有待发送报文
按照规则AC01：就算别的用户有数据，当前用户为空就什么都不能发
预期：wire_bits=0，completed_records为空，用户1的报文原封不动留在队列
"""
from collections import deque
from src.part1_circuit import serve_circuit
from src.models import Config, Pending


def test_my_no_borrow_timeslot():
    # 构造配置：2个用户，每个tick最多128bit
    cfg = Config(
        users=2,
        ticks=256,
        slot_bits=128,
        tick_ms=1,
        header_bits=32,
        buffer_payload_bits=4096
    )

    # 两个用户队列
    queues: list[deque[Pending]] = [deque(), deque()]

    # 用户0队列：空
    # 用户1队列放一条待发送报文，剩余待发送200bit
    p1 = Pending(user=1, arrival_tick=0, payload_bits=200, remaining_wire_bits=200)
    queues[1].append(p1)

    # tick=0，服务用户0；用户0没数据，不能去碰用户1
    wire_bits, completed = serve_circuit(queues, tick=0, cfg=cfg)

    # --------手算预期结果--------
    # 1.本tick发送0比特，不能借用时隙发送用户1
    assert wire_bits == 0, f"预期发送0bit，实际发送{wire_bits}"
    # 2.没有报文完成
    assert len(completed) == 0
    # 3.用户1队列报文还在，remaining_wire_bits完全不变还是200
    assert queues[1][0].remaining_wire_bits == 200

    print("✅ 自拟反例测试通过：没有发生时隙借用，符合AC01规则")
