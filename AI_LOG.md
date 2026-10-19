# AI协作记录

工具与模型：OpenAI Codex（桌面端），Python 3.12.10（D 盘嵌入式运行环境）。

## 一项真实协作过程

需求与输入：用户要求根据《实验一_PRD_电路交换与分组交换.docx》完成实验，并把生成文件尽量放在 D 盘。输入包括 PRD、教师仓库源码、`src/models.py`、`src/utils.py`、三个任务函数 docstring 和公开 grading 测试。

AI建议：先确认固定时隙和共享 FIFO 的服务边界，再补全三个函数。`serve_circuit` 只服务 `tick % cfg.users` 的队列，按 `cfg.slot_bits` 扣减 `remaining_wire_bits`；`serve_packet` 操作共享队列，不重复加包头；`summarize` 用原始统计量计算指标，并在 `generated != delivered + dropped + backlog` 时抛出 `ValueError`。

我的手算与测试：先用 2 用户、2 tick、128 bit/tick、32 bit 包头的例子手算：tick 0 用户 1 的 96 bit 记录在电路交换中等待、在分组交换中发送 128 bit 并于 1 ms 完成；电路交换在 tick 1 发送 96 bit 并于 2 ms 完成。随后用 AC04 手算共享 FIFO：A 剩 232、B 剩 64 时，tick 0 发 A 128（A 剩 104），tick 1 发 A 104（A 完成）再发 B 24（B 剩 40）。对应测试 `student_tests/test_my_case.py::test_packet_fifo_budget_continuation` 通过。

实际验证：`grading/test_circuit.py` 4 项通过，`grading/test_packet.py` 4 项通过，`grading/test_metrics.py` 3 项通过，`grading/test_integration.py` 3 项通过，`student_tests` 2 项通过；`grading/calculate_grade.py` 的自动项为 70/70。默认基线结果生成在 `results/comparison.csv/json` 和 3 张 PNG 中。

修正或采纳理由：最初尝试用官方 Python 3.12 安装包安装到 D 盘，但安装器需要写入当前用户的 `AppData\Local\Package Cache`，沙箱账户没有该目录权限，安装返回 `0x80070005`。因此改为在 `D:\codex\现代交换实验01\Python312` 解压 Python 3.12.10 embeddable 包，启用 `Lib\site-packages` 后用 `get-pip.py` 安装依赖。这个调整只改变运行环境位置，不改变实验模型、测试或结果参数。

我能解释的核心逻辑：发送循环每次都取队首，发送量取“剩余预算”和“队首剩余 wire bit”的较小值；只有 `remaining_wire_bits == 0` 才弹出并记入完成列表，所以部分发送不会被误记交付。分组记录的 `remaining_wire_bits` 已含一次包头，函数内不再加；电路函数只访问当前用户的队列，因此不会借用空时隙。指标函数直接使用 `raw` 中的生成、交付、丢弃和积压字段做守恒检查，避免把未完成记录重复计入交付。
