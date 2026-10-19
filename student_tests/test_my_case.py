"""自拟反例：揭示「部分发送被误记为交付」以及「固定时隙被借用」两类实现错误。

选择依据（对应 PRD 6.2 节可选项）：
  1. 部分发送误记交付 —— 若实现把 remaining_wire_bits>0 的记录也加入完成列表，
     守恒会被破坏，且框架 simulate() 会因 "incomplete record reported as delivered"
     直接抛 ValueError。
  2. 错误借用电路时隙 —— 若实现不按 tick % users 限定服务用户，非本时隙用户会被
     提前发送，导致该用户记录提前完成、时延失真。

本文件只验证模型规则，不检查文件是否存在、不照抄教师实现。
"""
from collections import deque

from src.models import Config, Pending
from src.part1_circuit import serve_circuit


def _cfg(users, slot_bits=128):
    return Config(users=users, slot_bits=slot_bits, header_bits=0)


def test_circuit_partial_send_not_delivered():
    """单用户、slot_bits=128，到达一条 200 bit 记录：
    tick 0 只能发 128 bit，记录尚未完成，必须返回空完成列表且 remaining 扣到 72。
    这能揭示「把部分发送记录当作完整交付」的错误实现。
    """
    rec = Pending(user=0, arrival_tick=0, payload_bits=200, remaining_wire_bits=200)
    q = [deque([rec])]  # 每用户一个 deque 的列表
    wire, done = serve_circuit(q, 0, _cfg(users=1))
    assert wire == 128
    assert done == []                     # 部分发送绝不能记入完成列表
    assert rec.remaining_wire_bits == 72  # 只扣减剩余线速比特，不更改 payload


def test_circuit_cannot_borrow_idle_slot():
    """2 用户，仅用户 1 队列有记录。tick 0 的服务用户是 0（空），
    电路交换不能把空时隙让给用户 1；用户 1 的记录必须留到 tick 1。
    这能揭示「空时隙自动让给其他用户」的错误实现。
    """
    rec = Pending(user=1, arrival_tick=0, payload_bits=32, remaining_wire_bits=32)
    q = [deque(), deque([rec])]
    assert serve_circuit(q, 0, _cfg(users=2)) == (0, [])
    assert len(q[1]) == 1                 # 用户 1 的记录原样保留
    wire, done = serve_circuit(q, 1, _cfg(users=2))
    assert wire == 32 and done == [rec] and not q[1]
