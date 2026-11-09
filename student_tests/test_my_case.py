"""自拟反例：用明确输入 + 手算预期验证模型规则，能暴露特定实现错误。

本文件针对三个典型错误各写一个用例：
1. 电路交换错误借用空时隙（把本应空闲的时隙让给其他用户）。
2. 分组交换重复计算包头（在已含包头的 remaining_wire_bits 上再加一次头）。
3. 部分发送的记录被误报为已交付，或漏算积压。
"""
from collections import deque
from src.models import Config, Pending, Arrival
from src.part1_circuit import serve_circuit
from src.part2_packet import serve_packet
from src.utils import simulate
from src.metrics import summarize


def test_circuit_does_not_borrow_idle_slot():
    """手算：2 个用户，tick 0 只服务 user=0%2=0。
    若 user0 队列为空而 user1 有 32 bit 记录，本 tick 应发 0 bit、无完成，
    user1 记录原地等待（不得把空时隙借给 user1）。
    若实现错误地“有空就服务别人”，此处会返回 32 并把 user1 记录完成，测试失败。"""
    q = [deque(), deque([Pending(1, 0, 32, 32)])]
    n, done = serve_circuit(q, 0, Config(users=2))
    assert n == 0
    assert done == []
    assert len(q[1]) == 1  # user1 的记录仍在等待


def test_packet_header_counted_once():
    """手算：payload 96 + 包头 32 = 128 wire，正好一个时隙预算。
    应在一个 tick 内发 128 bit 并完成该记录。
    若实现错误地再加一次包头（变成 160），则 128 预算内无法完成，测试失败。"""
    rec = Pending(0, 0, 96, 128)
    q = deque([rec])
    n, done = serve_packet(q, 0, Config())
    assert n == 128
    assert done == [rec]
    assert len(q) == 0


def test_partial_send_kept_in_backlog_not_delivered():
    """手算：payload 200 > 128 预算，观察窗口仅 1 tick。
    首 tick 只能发出 128 wire，记录未完成；窗口结束时交付=0、积压=200、丢失=0，
    平均时延无样本应为 None。
    若实现把“已发 128”误当作交付、或漏算积压，守恒与断言都会失败。"""
    cfg = Config(ticks=1)
    raw = simulate([Arrival(0, 0, 200)], cfg, 'packet')
    assert raw['delivered_payload_bits'] == 0
    assert raw['backlog_payload_bits'] == 200
    assert raw['dropped_payload_bits'] == 0
    m = summarize(raw, cfg)
    assert m['mean_delay_ms'] is None
    assert m['payload_utilization'] == 0
