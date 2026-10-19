"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    q = queue

    budget = cfg.slot_bits
    wire = 0
    completed = []

    while q and budget > 0:
        rec = q[0]

        if rec.remaining_wire_bits <= budget:
            send = rec.remaining_wire_bits
            wire += send
            budget -= send
            rec.remaining_wire_bits = 0
            q.popleft()
            completed.append(rec)
        else:
            rec.remaining_wire_bits -= budget
            wire += budget
            budget = 0

    return wire, completed