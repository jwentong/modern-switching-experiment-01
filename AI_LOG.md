# AI协作记录

工具与模型：大语言模型（deepseek）、AI agent(codex)

## 一项真实协作过程

**需求与输入**：
在完成 `src/part2_packet.py` 中的 `serve_packet` 函数时，我需要 AI 解释共享 FIFO 队列的发送逻辑，并帮我检查是否存在重复计算包头的问题。我提供给 AI 的输入包括：函数的签名 `serve_packet(queue, tick, cfg)`、模型规则（共享 FIFO，可跨 tick，每 tick 预算 128 bit）以及 `Pending` 类的字段定义。

**AI建议**：
AI 建议在每次 tick 开始时，设置 `budget = cfg.slot_bits`，然后严格从队列头部（`queue[0]`）开始发送。如果队首记录剩余所需传输的比特数 `remaining_wire_bits` 小于等于 `budget`，则扣除对应预算、将其弹出并加入 `completed` 列表；如果大于 `budget`，则只发送 `budget` 的量并扣减 `remaining_wire_bits`，停止发送。AI 特别强调：**框架在生成 `Pending` 对象时，已经将 `payload_bits + header_bits` 赋值给了 `remaining_wire_bits`，因此在 `serve_packet` 中绝对不能再加 `cfg.header_bits`。**

**我的手算与测试**：
- **手算预期**：参照 PRD 的 AC03 用例，若分组 payload 为 96，初始化 wire 为 128，本 tick 容量为 128，则应当在一个 tick 发送 128 并完成，不能再次加 32 bit 包头。
- **实际测试**：我按照 AI 的建议实现了代码，并在终端运行了 `.\.venv\Scripts\python.exe -m pytest grading/test_packet.py -q`。
- **测试结果**：显示 `4 passed`，证明我的实现完全符合“包头只计一次”和“不交错”的模型规则。

**修正或采纳理由**：
采纳了 AI 的建议，因为通过阅读 `utils.py` 源码和测试用例，我确认了 `remaining_wire_bits` 确实在初始化时就包含了包头。为了保证严谨性，我还编写了自测用例 `test_circuit_cannot_borrow_other_user_slot`，验证了另一个错误边界（电路交换不能借用时隙），运行 `pytest student_tests -q` 得到 `1 passed`，确认了边界逻辑的正确性。

**我能解释的核心逻辑**：
- **如何避免重加包头**：只操作 `remaining_wire_bits` 进行扣减，不在任何地方读取或加上 `header_bits`。
- **如何避免借用固定时隙**：在电路交换中，通过 `user = tick % cfg.users` 严格锁定当前服务队列，绝不遍历或操作其他用户的队列。
- **如何避免统计遗漏积压**：在指标函数中，直接利用 `generated = delivered + dropped + backlog` 的守恒定律，若不等则抛出 `ValueError`，确保所有未完成的数据都被计入 `backlog`。