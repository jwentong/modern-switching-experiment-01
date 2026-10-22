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
       # 1. 从 raw 字典中提取基础数据
    generated = raw.get('generated_payload_bits', 0)
    dropped = raw.get('dropped_payload_bits', 0)
    backlog = raw.get('backlog_payload_bits', 0)
    wire_sent = raw.get('wire_sent_bits', 0)
    completed_records = raw.get('completed', [])

    # 2. 计算已交付载荷
    delivered = sum(rec['payload_bits'] for rec in completed_records)

    # 3. 守恒检查
    if generated != (delivered + dropped + backlog):
        raise ValueError(f"守恒不成立: 生成({generated}) != 交付({delivered}) + 丢弃({dropped}) + 积压({backlog})")

    # 4. 计算各种利用率
    total_capacity = cfg.ticks * cfg.slot_bits
    payload_utilization = delivered / total_capacity
    wire_utilization = wire_sent / total_capacity

    # 5. 计算丢失率（如果没生成数据，直接为0）
    loss_ratio = (dropped / generated) if generated > 0 else 0

    # 6. 计算时延
    # 把每条完成记录的 delay_ticks 提取出来，组成一个列表
    delays = [rec['delay_ticks'] for rec in completed_records]
    
    if delays:  # 如果列表不为空（有完成的记录）
        mean_delay_ms = (sum(delays) / len(delays)) * cfg.tick_ms
        max_delay_ms = max(delays) * cfg.tick_ms
    else:       # 没有任何记录完成
        mean_delay_ms = None
        max_delay_ms = None

    # 7. 组装返回字典
    return {
        'payload_utilization': payload_utilization,
        'wire_utilization': wire_utilization,
        'mean_delay_ms': mean_delay_ms,
        'max_delay_ms': max_delay_ms,
        'loss_ratio': loss_ratio,
        'backlog_payload_bits': backlog
    }
