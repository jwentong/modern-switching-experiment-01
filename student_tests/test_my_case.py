import pytest
from collections import deque
from src.models import Config, Pending
from src.part1_circuit import serve_circuit

def test_circuit_cannot_borrow_empty_slot():
    """
    反例（错误借用电路时隙）：
    - 输入：2 个用户。tick 0 时，用户 0 队列为空，用户 1 队列有 96 bit 数据。
    - 手算预期：tick 0 属于用户 0，由于用户 0 没数据，本 tick 发送量必须为 0。
      用户 1 的数据必须原封不动，不能借用用户 0 的空时隙。
    - 揭示的错误：如果实现中错误地遍历了所有队列寻找数据，会导致破坏“固定时隙”模型，产生不公平的复用。
    """
    # 1. 构造明确输入
    cfg = Config(users=2, ticks=2, slot_bits=128)
    queues = [deque(), deque()]
    # 用户 1 到达了 96 bit 的数据
    queues[1].append(Pending(user=1, arrival_tick=0, payload_bits=96, remaining_wire_bits=96))

    # 2. 执行被测函数（tick 0 应该服务 user 0）
    sent_bits, completed = serve_circuit(queues, tick=0, cfg=cfg)

    # 3. Assert 断言验证
    # 因为 tick 0 轮到 user 0，但 user 0 没数据，所以发送量必须是 0
    assert sent_bits == 0, "错误：当前用户为空时，不应借用其他用户的时隙发送数据！"
    
    # 没有任何记录被完成
    assert len(completed) == 0, "错误：没有发送数据，不应产生完成记录！"
    
    # 用户 1 的数据必须完好无损地等在队列里
    assert len(queues[1]) == 1
    assert queues[1][0].remaining_wire_bits == 96, "错误：用户 1 的数据被错误地发送了！"