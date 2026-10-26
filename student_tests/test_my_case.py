from collections import deque
from src.models import Config, Pending
from src.part1_circuit import serve_circuit

def test_circuit_cannot_borrow_empty_slot():
    """
    反例测试：验证电路交换模式下，当前用户队列为空时，绝对不能借用其他用户的时隙。
    
    揭示的错误：如果代码实现时写成了“遍历所有用户找非空队列发送”，
    就会导致线路利用率虚高，且无法体现固定时隙预留的缺点。
    """
    # 1. 明确输入
    # 配置：2个用户，本tick容量 128 bit
    cfg = Config(users=2, ticks=1, slot_bits=128, tick_ms=1, header_bits=32, buffer_payload_bits=1000)
    
    # 构造队列：用户0为空，用户1有一条 96 bit 的数据等着发
    user1_record = Pending(user=1, arrival_tick=0, payload_bits=96, remaining_wire_bits=96)
    queues = [deque(), deque([user1_record])] 
    
    # 2. 设定当前 tick = 0
    # 按照规则，tick % users = 0 % 2 = 0，当前本应服务用户0
    tick = 0
    
    # 3. 先手算预期
    # 因为用户0的队列为空，规则规定不能借用给用户1。
    # 所以本 tick 应该什么也不发，返回 (0, [])。
    
    # 执行函数
    wire_bits_sent, completed_records = serve_circuit(queues, tick, cfg)
    
    # 4. 写 assert 断言验证预期
    # 断言 1：发送的比特数必须为 0（不能偷偷借给用户1发数据）
    assert wire_bits_sent == 0, f"错误：当前用户(0)无数据，不应发送任何比特，但实际发送了 {wire_bits_sent} bit"
    
    # 断言 2：完成列表为空
    assert len(completed_records) == 0
    
    # 断言 3：用户1的数据必须原封不动地留在队列里
    assert len(queues[1]) == 1
    assert queues[1][0].remaining_wire_bits == 96