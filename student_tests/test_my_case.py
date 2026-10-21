"""
自拟反例测试：电路交换不允许空闲时隙借给其他用户
手算预期：
users=2，tick=0，服务用户0；用户0队列为空，用户1队列有Pending报文
serve_circuit返回(0, [])，用户1队列中报文保持不变，不能被发送。
用来检测错误：错误实现把空闲时隙挪用给其他有数据的用户。
"""
from collections import deque
from src.part1_circuit import serve_circuit
from src.models import Config, Pending


def test_circuit_no_borrow_timeslot():
    # 构造配置：2用户，每tick容量128bit
    cfg = Config(
        users=2,
        ticks=256,
        slot_bits=128,
        tick_ms=1,
        header_bits=32,
        buffer_payload_bits=4096
    )

    # queues：每个用户一个deque
    queues: list[deque[Pending]] = [
        deque(),  # user0，当前tick要服务的用户，队列为空
        deque()   # user1，有报文，但是本tick不能获得时隙
    ]

    # 用户1加入一条待发送报文
    pkt = Pending(
        user=1,
        arrival_tick=0,
        payload_bits=96,
        remaining_wire_bits=96 + 32  # payload+header
    )
    queues[1].append(pkt)

    # tick=0 → tick%2 =0，服务user0
    wire_bits, completed = serve_circuit(queues, tick=0, cfg=cfg)

    # =====断言=====
    # 1.本tick发送比特必须为0，用户0空队列，不能借用时隙给user1
    assert wire_bits == 0, f"预期发送0bit，实际发送{wire_bits}"
    # 2.完成列表必须为空，没有任何报文完成
    assert len(completed) == 0
    # 3.用户1队列报文还在，remaining_wire_bits完全没有被修改
    assert len(queues[1]) == 1
    assert queues[1][0].remaining_wire_bits == 96 + 32

    # 切换 tick=1，tick%2=1，此时才轮到服务用户1
    wire_bits2, completed2 = serve_circuit(queues, tick=1, cfg=cfg)
    assert wire_bits2 == 128
    assert len(completed2) == 1

