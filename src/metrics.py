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
    # 1. 基础数据（根据你的截图第5行，名字完全匹配）
    generated = raw["generated_payload_bits"]
    delivered = raw["delivered_payload_bits"]
    dropped = raw["dropped_payload_bits"]
    backlog = raw["backlog_payload_bits"]
    wire_sent = raw["wire_sent_bits"]
    
    # 2. 守恒检查
    if generated != delivered + dropped + backlog:
        raise ValueError("守恒不成立：生成量 != 交付 + 丢弃 + 积压")
        
    # 3. 计算总容量（ticks * slot_bits）
    total_capacity = cfg.ticks * cfg.slot_bits
    
    # 4. 计算利用率
    payload_utilization = delivered / total_capacity if total_capacity > 0 else 0.0
    wire_utilization = wire_sent / total_capacity if total_capacity > 0 else 0.0
    
    # 5. 计算丢失率
    loss_ratio = dropped / generated if generated > 0 else 0.0
    
    # 6. 提取完成记录
    completed = raw["completed"]
    
    # 7. 计算时延
    if completed:
        # 从每个完成的字典里提取 delay_ticks
        delays = [rec["delay_ticks"] for rec in completed]
        mean_delay_ms = (sum(delays) / len(delays)) * cfg.tick_ms
        max_delay_ms = max(delays) * cfg.tick_ms
    else:
        mean_delay_ms = None
        max_delay_ms = None
        
    # 8. 返回字典
    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog
    }
