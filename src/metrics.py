def summarize(raw, cfg):
    generated = raw.get('generated_payload_bits', 0)
    delivered = raw.get('delivered_payload_bits', 0)
    dropped = raw.get('dropped_payload_bits', 0)
    backlog = raw.get('backlog_payload_bits', 0)
    
    if generated != delivered + dropped + backlog:
        raise ValueError("Conservation law violated")

    total_capacity = cfg.ticks * cfg.slot_bits
    payload_utilization = delivered / total_capacity if total_capacity > 0 else 0
    wire_utilization = raw.get('wire_bits', 0) / total_capacity if total_capacity > 0 else 0
    
    completions = raw.get('completed_records', [])
    if len(completions) > 0:
        mean_delay = sum(c['delay_ticks'] for c in completions) / len(completions) * cfg.tick_ms
        max_delay = max(c['delay_ticks'] for c in completions) * cfg.tick_ms
    else:
        mean_delay = None
        max_delay = None
        
    loss_ratio = dropped / generated if generated > 0 else 0
    
    return {
        'payload_utilization': payload_utilization,
        'wire_utilization': wire_utilization,
        'mean_delay_ms': mean_delay,
        'max_delay_ms': max_delay,
        'loss_ratio': loss_ratio,
        'backlog_payload_bits': backlog
    }