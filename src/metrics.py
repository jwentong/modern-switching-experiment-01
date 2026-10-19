"""任务3：补全指标统计。"""
def summarize(raw, cfg):
    generated = raw["generated_payload_bits"]
    delivered = raw["delivered_payload_bits"]
    dropped = raw["dropped_payload_bits"]
    backlog = raw["backlog_payload_bits"]

    wire_sent = raw.get("wire_sent_bits", raw.get("wire_bits_sent", 0))
    completed = raw.get("completed", raw.get("completed_records", [])) or []

    # 守恒检查必须在任何计算之前
    if generated != delivered + dropped + backlog:
        raise ValueError(
            f"payload conservation violated: generated={generated}, "
            f"delivered={delivered}, dropped={dropped}, backlog={backlog}"
        )

    capacity = cfg.ticks * cfg.slot_bits

    payload_utilization = delivered / capacity if capacity else 0.0
    wire_utilization = wire_sent / capacity if capacity else 0.0

    delays = []
    for rec in completed:
        if isinstance(rec, dict):
            d = rec.get("delay_ticks")
            if d is None:
                d = rec["finish_tick"] - rec["arrival_tick"]
        else:
            d = getattr(rec, "delay_ticks", None)
            if d is None:
                d = rec.finish_tick - rec.arrival_tick
        delays.append(d)

    mean_delay_ms = (sum(delays) / len(delays)) * cfg.tick_ms if delays else None
    max_delay_ms = max(delays) * cfg.tick_ms if delays else None
    loss_ratio = dropped / generated if generated else 0.0

    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog,
    }