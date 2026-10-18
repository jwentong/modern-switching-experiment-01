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
    
    # 计算整个观察窗口的链路总容量
    total_capacity = cfg.ticks * cfg.slot_bits

    # 读取仿真统计数据
    generated = raw["generated_payload_bits"]
    delivered = raw["delivered_payload_bits"]
    dropped = raw["dropped_payload_bits"]
    backlog = raw["backlog_payload_bits"]
    wire_sent = raw["wire_sent_bits"]
    completed = raw["completed"]

    # 检查有效载荷的数据守恒
    if generated != delivered + dropped + backlog:
        raise ValueError("payload conservation check failed")

    # 计算有效载荷利用率和线路忙碌率
    payload_utilization = delivered / total_capacity
    wire_utilization = wire_sent / total_capacity

    # 将每条完成记录的时延转换为毫秒
    delays = [
        item["delay_ticks"] * cfg.tick_ms
        for item in completed
    ]

    # 没有完成记录时，平均时延和最大时延均为 None
    if delays:
        mean_delay_ms = sum(delays) / len(delays)
        max_delay_ms = max(delays)
    else:
        mean_delay_ms = None
        max_delay_ms = None

    # 没有生成数据时，丢失率定义为 0
    if generated == 0:
        loss_ratio = 0
    else:
        loss_ratio = dropped / generated

    # 返回老师要求的指标字典
    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog,
    }

