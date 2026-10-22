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
    # 1. 取出基础数据（从说明书和常规框架推断出的变量名）
    generated = raw.get("generated_payload_bits", 0)
    delivered = raw.get("delivered_payload_bits", 0)
    dropped = raw.get("dropped_payload_bits", 0)
    backlog = raw.get("backlog_payload_bits", 0)
    wire_sent = raw.get("wire_sent_bits", 0)
    
    # 2. 检查数据守恒（AC09）
    if generated != delivered + dropped + backlog:
        raise ValueError("数据不守恒：generated != delivered + dropped + backlog")
        
    # 3. 计算利用率
    total_capacity = cfg.ticks * cfg.slot_bits
    payload_utilization = delivered / total_capacity if total_capacity > 0 else 0
    wire_utilization = wire_sent / total_capacity if total_capacity > 0 else 0
    
    # 4. 计算丢失率
    loss_ratio = dropped / generated if generated > 0 else 0
    
    # 5. 计算时延
    completed_list = raw.get("completed", [])
    if len(completed_list) > 0:
        delays = [item["delay_ticks"] for item in completed_list]
        mean_delay = (sum(delays) / len(delays)) * cfg.tick_ms
        max_delay = max(delays) * cfg.tick_ms
    else:
        # AC08 要求：无完成记录时必须返回 None
        mean_delay = None
        max_delay = None
        
    # 6. 返回字典
    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay,
        "max_delay_ms": max_delay,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog
    }
