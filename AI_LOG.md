# AI协作记录

工具与模型：DeepSeek Harness 编码助手（deepseek-flash），Python 3.12 虚拟环境，pytest 9.2。

协作方式（如实记录）：由 AI 助手补全三个函数、运行全部测试、生成 8 组结果与报告初稿；作者负责复核手算、审阅断言与结论后再提交。下面的过程是本次会话中真实发生的推导与修正，供作者复核时逐条对照。

## 一项真实协作过程

**需求与输入**：实现 `src/part2_packet.py` 的 `serve_packet(queue, tick, cfg)`。约束是：`remaining_wire_bits` 已由框架初始化为 `payload_bits + header_bits`，不得重复加头；每 tick 预算 `slot_bits`，必须发完队首再发下一条；记录可跨 tick 续传，不得交错、不得因超长丢弃；返回实际发送比特与完整发送的记录列表。

**AI建议**：用一个预算循环统一处理两种交换：

```python
while budget > 0 and queue:
    record = queue[0]
    send = min(budget, record.remaining_wire_bits)
    record.remaining_wire_bits -= send
    budget -= send
    if record.remaining_wire_bits == 0:
        queue.popleft()
        completed.append(record)
```

关键点是 `min` 截断、只在剩余为 0 时出队、循环继续消费剩余预算；电路版本只把 `queue` 换成 `queues[tick % cfg.users]`。

**推导与测试**：先按 PRD 6.1 手算 2 用户例子——电路 37.5% / 37.5% / 2 ms，分组 37.5% / 50% / 1 ms，再用 `simulate` 运行，数值逐项一致。随后用 AC04 的预算消耗（A 232、B 64：首 tick A 余 104，次 tick A 104 + B 24、B 余 40）核对跨记录续发，`grading/test_packet.py` 4 项通过。

**一次真实的修正**：自拟反例第一版的算术是错的。最初写的是“200 bit 记录 + 128 bit/tick × 3 tick → 线路发送 384”，测试立即报 `assert 328 == 384`。复盘发现 tick 1 发完剩余的 72 bit 后预算只用掉 72，剩下 56 bit 没有记录可发，正确值是 128 + 72 + 128 = 328。这不是实现错误，而是手算漏了“空闲预算不补发”；随后同时修正了断言和 docstring 中的手算说明。这个过程说明：**测试失败时先怀疑自己的手算，再怀疑实现**，并且预算按实际发出的比特累计，不是每 tick 固定发满 128。

**核心逻辑解释**（作者复核时需能讲清）：
- 不重复加包头：包头只在 `simulate` 准入创建 `Pending` 时加一次，`serve_packet` 只扣减 `remaining_wire_bits`；跨 tick 续传时该字段已经是“剩余线路比特”，再加头会得到 384 而不是 332。
- 不借用固定时隙：电路的服务对象只由 `tick % cfg.users` 决定，队列为空就返回 `(0, [])`，不能“顺手”服务其他用户，否则 staggered_burst 的电路结果会虚高。
- 不遗漏积压：`backlog_payload_bits` 由框架在窗口结束时用 `reserved` 给出，等于所有未完成记录的**原始** payload，部分发送的记录不能用剩余比特代替，否则守恒式不成立、`summarize` 会抛 `ValueError`。

## 验证记录

| 验证项 | 命令/方法 | 结果 |
|---|---|---|
| 教师框架测试 | `pytest grading/test_framework.py` | 4 passed |
| 电路 4 项 | `pytest grading/test_circuit.py` | 4 passed |
| 分组 4 项 | `pytest grading/test_packet.py` | 4 passed |
| 指标 3 项 | `pytest grading/test_metrics.py` | 3 passed |
| 集成 3 项 | `pytest grading/test_integration.py` | 3 passed |
| 自拟反例 2 项 | `pytest student_tests -q` | 2 passed |
| 2 用户手算 | 手工推导 + `simulate` 对照 | 与手算一致 |
| 结果守恒 | 8 组 `generated = delivered + dropped + backlog` | 全部成立 |
| 重复性 | 相同参数重跑 `performance_test.py` | 5 个结果文件哈希一致 |

自动评分：`python grading/calculate_grade.py` 得 70.0/70 自动项（环境 5 + 电路 20 + 分组 20 + 指标 15 + 结果 10）。
