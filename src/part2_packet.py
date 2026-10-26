def serve_packet(queue, tick, cfg):
    budget = cfg.slot_bits
    wire_bits = 0
    completed_records = []
    while budget > 0 and queue:
        head = queue[0]
        send = min(budget, head.remaining_wire_bits)
        head.remaining_wire_bits -= send
        budget -= send
        wire_bits += send
        if head.remaining_wire_bits == 0:
            completed_records.append(queue.popleft())
    return wire_bits, completed_records