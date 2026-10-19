"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    budget = cfg.slot_bits
    wire_bits = 0
    completed_records = []

    while budget > 0 and queue:
        rec = queue[0]
        send = min(budget, rec.remaining_wire_bits)

        rec.remaining_wire_bits -= send
        wire_bits += send
        budget -= send

        if rec.remaining_wire_bits == 0:
            completed_records.append(queue.popleft())
        else:
            break

    return wire_bits, completed_records