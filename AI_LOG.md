# AI协作记录

工具与模型：WorkBuddy（本地 AI 编程助手）

## 一项真实协作过程

需求与输入：请阅读 `README.md`、`docs/model_contract.md`、`src/models.py` 及 `serve_circuit`/`serve_packet` 的 docstring，说明固定时隙电路交换与共享 FIFO 分组交换的输入输出与跨 tick 续传规则，并补全 `src/part1_circuit.py` 的 `serve_circuit` 函数（一次只补全一个函数，不改教师测试与接口）。

AI建议：`serve_circuit` 先取 `user = tick % cfg.users` 定位当前时隙用户，再对其队列做预算填充循环——每轮取队首，若 `remaining_wire_bits <= budget` 则整条发出、`popleft` 并记入完成列表；否则按剩余预算扣减 `remaining_wire_bits`、预算清零后退出。空队列返回 `(0, [])`。`serve_packet` 用同一套循环，只是作用在共享 `queue` 上且不重复加包头。`summarize` 先做守恒校验再计算各指标，无完成记录时时延返回 `None`，无生成数据时丢失率为 0。

我的手算与测试：先用 PRD 6.1 节的 2 用户小例子手算（电路 tick 0 闲置、tick 1 完成 2 ms；分组 tick 0 发完 1 ms），再运行 `python -m pytest grading/test_circuit.py grading/test_packet.py grading/test_metrics.py grading/test_framework.py grading/test_integration.py -q`，实际 18 passed；`student_tests` 2 passed。

修正或采纳理由：三个函数首次实现即通过全部教师测试。为验证边界，额外编写了 `student_tests/test_my_case.py`，其中一项（部分发送不得误记为交付）在编写时最初把 `queues` 误写为单个 deque 而非"每用户一个 deque 的列表"，暴露出我对接口参数的误解，修正为列表包裹后通过——这也正是"部分发送口径"这条边界需要显式验证的原因。

我能解释的核心逻辑：
- **如何避免重加包头**：`serve_packet` 只读 `rec.remaining_wire_bits`（框架已在准入时置为 `payload_bits + header_bits`），循环内只做减法，从不 `+ header_bits`，因此包头只计一次。
- **如何避免借用固定时隙**：`serve_circuit` 第一行 `user = tick % cfg.users` 固定了服务对象，空时隙不会把预算让给其他用户。
- **如何避免统计遗漏积压**：`summarize` 用守恒式 `generated == delivered + dropped + backlog` 前置校验，不成立即抛 ValueError，保证部分发送记录的原始 payload 全部计入积压、不被重复计入交付。
