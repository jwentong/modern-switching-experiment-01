"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
def serve_circuit(queues, tick, cfg):
    user = tick % cfg.users
    q = queues[user]

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