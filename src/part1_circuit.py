"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
def serve_circuit(queues, tick, cfg):
    user = tick % cfg.users
    q = queues[user]

    budget = cfg.slot_bits
    wire_bits = 0
    completed_records = []

    while budget > 0 and q:
        rec = q[0]
        send = min(budget, rec.remaining_wire_bits)

        rec.remaining_wire_bits -= send
        wire_bits += send
        budget -= send

        if rec.remaining_wire_bits == 0:
            completed_records.append(q.popleft())
        else:
            break

    return wire_bits, completed_records