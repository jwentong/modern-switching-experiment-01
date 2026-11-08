"""自拟反例：验证“部分发送不算交付”与“包头只计一次、长分组不丢弃”。

两个用例都先手算再断言，数字与教师 AC 用例不同，用于揭示常见实现错误：
1) 把部分发送的记录提前 pop 或计入 delivered，会把 200 bit 的记录误报为已送达；
2) 每个 tick 重复加 32 bit 包头，会让 300 bit 分组的线路比特变成 384 而不是 332，
   或者在“记录长于一个时隙”时直接丢弃。
"""
from src.models import Arrival, Config
from src.utils import simulate
from src.metrics import summarize


def test_partial_send_and_window_backlog():
    """1 用户、每 tick 128 bit、3 个 tick。

    手算：
      tick0 到达 200 bit，发 128，余 72；
      tick1 发完 72，完成边界为 2，delay_ticks = 2；
      tick2 到达 300 bit，发 128，余 172，窗口结束仍为积压。
    合计：生成 500、交付 200、丢弃 0、积压 300（原始 payload，不是剩余 172）。
    wire = 128 + 72 + 128 = 328，窗口容量 = 3 * 128 = 384。
    若实现把部分发送误记为完成，delivered 会变成 500 或时延样本多出 1 条。
    """
    cfg = Config(users=1, ticks=3)
    arrivals = [Arrival(0, 0, 200), Arrival(2, 0, 300)]
    raw = simulate(arrivals, cfg, 'circuit')

    assert raw['generated_payload_bits'] == 500
    assert raw['delivered_payload_bits'] == 200
    assert raw['dropped_payload_bits'] == 0
    assert raw['wire_sent_bits'] == 328
    assert raw['backlog_payload_bits'] == 300
    assert [c['delay_ticks'] for c in raw['completed']] == [2]
    # 部分发送只扣 remaining_wire_bits，不得改写原始 payload。
    assert raw['completed'][0]['payload_bits'] == 200

    m = summarize(raw, cfg)
    assert m['payload_utilization'] == 200 / 384
    assert m['wire_utilization'] == 328 / 384
    assert m['mean_delay_ms'] == 2.0
    assert m['max_delay_ms'] == 2.0
    assert m['loss_ratio'] == 0
    assert m['backlog_payload_bits'] == 300


def test_packet_header_once_across_ticks():
    """1 用户、每 tick 128 bit、4 个 tick，分组 300 bit 需要 332 个线路比特。

    手算：tick0 发 128（余 204）、tick1 发 128（余 76）、tick2 发 76 完成，
    完成边界为 3。若每 tick 重复加 32 bit 包头，或按“超过一个时隙就丢弃”处理，
    线路比特会变成 384 或出现丢弃；正确值为 332，且 loss_ratio = 0。
    """
    cfg = Config(users=1, ticks=4)
    raw = simulate([Arrival(0, 0, 300)], cfg, 'packet')

    assert raw['wire_sent_bits'] == 332          # 300 + 32，包头只加一次
    assert raw['delivered_payload_bits'] == 300
    assert raw['dropped_payload_bits'] == 0
    assert raw['backlog_payload_bits'] == 0
    assert [c['delay_ticks'] for c in raw['completed']] == [3]

    m = summarize(raw, cfg)
    assert m['payload_utilization'] == 300 / 512
    assert m['wire_utilization'] == 332 / 512
    assert m['mean_delay_ms'] == 3.0
    assert m['loss_ratio'] == 0
