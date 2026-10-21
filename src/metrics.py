"""任务3：补全指标统计。"""
def summarize(raw, cfg):
    """返回字典，键名必须保留：
    payload_utilization=delivered_payload_bits/(cfg.ticks*cfg.slot_bits)
    wire_utilization=wire_sent_bits/(cfg.ticks*cfg.slot_bits)
    mean_delay_ms、max_delay_ms：完成记录的delay_ticks乘cfg.tick_ms；
      无完成记录时两者返回None，不能写0掩盖无送达。
    loss_ratio=dropped_payload_bits/generated_payload_bits；无生成数据时为0。
    backlog_payload_bits：所有未完成记录的原始payload总和，直接取raw对应值。
    只用观察窗口[0,ticks)，不追加排空时间；有效载荷按完整交付记录计数。
    raw['completed']元素含payload_bits、delay_ticks、user。
    要检查generated=delivered+dropped+backlog，不相等抛ValueError。
    """
    # 取出raw中的原始统计量
    generated_payload_bits = raw["generated_payload_bits"]
    delivered_payload_bits = raw["delivered_payload_bits"]
    dropped_payload_bits = raw["dropped_payload_bits"]
    wire_sent_bits = raw["wire_sent_bits"]
    backlog_payload_bits = raw["backlog_payload_bits"]
    completed_records = raw["completed"]

    # 守恒校验：generated == delivered + dropped + backlog，不相等抛ValueError
    if generated_payload_bits != delivered_payload_bits + dropped_payload_bits + backlog_payload_bits:
        raise ValueError("Payload conservation check failed: generated != delivered + dropped + backlog")

    total_line_bits = cfg.ticks * cfg.slot_bits
    payload_utilization = delivered_payload_bits / total_line_bits
    wire_utilization = wire_sent_bits / total_line_bits

    # 时延计算
    if len(completed_records) == 0:
        mean_delay_ms = None
        max_delay_ms = None
    else:
        delay_ticks_list = [rec["delay_ticks"] for rec in completed_records]
        mean_ticks = sum(delay_ticks_list) / len(delay_ticks_list)
        max_ticks = max(delay_ticks_list)
        mean_delay_ms = mean_ticks * cfg.tick_ms
        max_delay_ms = max_ticks * cfg.tick_ms

    # 丢失率：无生成payload，loss_ratio=0；否则做除法
    if generated_payload_bits == 0:
        loss_ratio = 0.0
    else:
        loss_ratio = dropped_payload_bits / generated_payload_bits

    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog_payload_bits
    }

