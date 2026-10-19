"""任务3：补全指标统计。"""
def summarize(raw, cfg):
    capacity = cfg.ticks * cfg.slot_bits

    delivered = raw["delivered_payload_bits"]
    wire = raw["wire_sent_bits"]
    dropped = raw["dropped_payload_bits"]
    generated = raw["generated_payload_bits"]
    backlog = raw["backlog_payload_bits"]

    if generated != delivered + dropped + backlog:
        raise ValueError("bit conservation failed")

    completed = raw["completed"]

    if completed:
        delays = []
        for rec in completed:
            if isinstance(rec, dict):
                delays.append(rec["delay_ticks"])
            else:
                delays.append(rec.delay_ticks)
        mean_delay_ms = (sum(delays) / len(delays)) * cfg.tick_ms
        max_delay_ms = max(delays) * cfg.tick_ms
    else:
        mean_delay_ms = None
        max_delay_ms = None

    return {
        "payload_utilization": delivered / capacity if capacity else 0,
        "wire_utilization": wire / capacity if capacity else 0,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": dropped / generated if generated else 0,
        "backlog_payload_bits": backlog,
    }