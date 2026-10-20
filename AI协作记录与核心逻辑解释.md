# AI协作记录与核心逻辑解释

## 一、基本信息

- 工具与模型：OpenAI Codex（GPT-5）。
- 协作日期：2026-10-19。
- 协作范围：阅读实验一 PRD 和仓库代码，补全三个 TODO 函数，设计自拟反例，
  运行公开测试和完整仿真，核对结果数据，并整理核心逻辑说明。


## 二、真实协作过程

### 2.1 需求与输入

我向 Codex 提供了实验一 PRD、仓库路径和三个任务文件的位置，要求在不改变函数接口和测试的前提下补全：

1. `src/part1_circuit.py` 中的 `serve_circuit`；
2. `src/part2_packet.py` 中的 `serve_packet`；
3. `src/metrics.py` 中的 `summarize`。

同时提供了 `src/models.py` 中的 `Config`、`Arrival`、`Pending` 定义，以及
`docs/model_contract.md` 中的事件顺序、缓存准入和公平比较规则。基线参数是 4 个
用户、256 个 tick、每 tick 1 ms、128 bit 链路容量、32 bit 分组包头和 4096 bit
有效载荷缓存。

### 2.2 AI 给出的关键建议

电路函数先由 `user = tick % cfg.users` 选择本 tick 唯一可服务的队列，再在该用户的
FIFO 队列上循环使用 `cfg.slot_bits` 预算。每次发送
`min(record.remaining_wire_bits, budget)`；只要记录没有发完，就继续留在队首。
只有剩余 wire 为 0 时才 `popleft` 并加入完成列表。预算还有剩余时继续服务同一用户
的下一条记录，但不能转向其他用户。

分组函数在共享 FIFO 上使用同样的预算循环。关键区别是
`remaining_wire_bits` 已由框架初始化为 `payload_bits + header_bits`，发送函数只能
扣减剩余量，不能再加一次包头。队首没有发完时不能越过它去服务下一条，因此不会发生
分组交错；大记录可以跨 tick 续传，也不应因为长度超过一个 tick 就被丢弃。

指标函数先检查守恒式 `generated = delivered + dropped + backlog`，不成立时抛出
`ValueError`。有效载荷利用率使用完整交付的 payload，线路忙碌率使用实际发送的 wire
bit；平均和最大时延只统计完整交付的记录，没有完成记录时返回 `None`，不能用 0 代替。

### 2.3 本次协作先做的两用户手算

取 2 个用户、2 个 tick、每 tick 1 ms、容量 128 bit、包头 32 bit，缓存足够。只有
用户 1 在 tick 0 到达一条 96 bit 记录。

| tick | 电路交换 | 分组交换 |
|---|---|---|
| 0 | 本时隙属于用户 0；用户 0 无数据，发送 0 bit | 发送 96 + 32 = 128 bit，记录在 1 ms 完成 |
| 1 | 本时隙属于用户 1，发送 96 bit，记录在 2 ms 完成 | 队列为空，发送 0 bit |

本次协作先完成的手算预期：两种方式的有效载荷利用率都是 `96 / 256 = 37.5%`，但电路和分组的线路忙碌率分别是 `96 / 256 = 37.5%` 和 `128 / 256 = 50%`；完成时延分别是 2 ms 和
1 ms。这个例子说明相同的有效载荷利用率不代表相同的时延和线路开销。

实际运行 `simulate` 和 `summarize` 后得到：

- 电路：`payload_utilization=0.375`、`wire_utilization=0.375`、
  `mean_delay_ms=2.0`、`max_delay_ms=2.0`；
- 分组：`payload_utilization=0.375`、`wire_utilization=0.5`、
  `mean_delay_ms=1.0`、`max_delay_ms=1.0`。

实际值与手算预期一致。这一步是在写代码前完成的，用来判断后面测试失败时应该先查预算、包头还是完成时刻。

### 2.4 实现与第一次验证

三个函数补全后，先运行提供的电路、分组和指标测试，再运行集成和框架测试。
本次实现第一次运行就通过，没有出现“先写错、再由 AI 修正”的过程，因此没有编造错误聊天记录。之后补做两个自拟边界用例，专门检查最容易写错的规则：

1. 电路发完一条记录后是否继续使用同一用户的剩余预算；
2. 电路是否会在当前用户队列为空时借用其他用户的时隙；
3. 分组跨 tick 时是否重复加包头；
4. 分组是否会越过未完成的队首去服务下一条；
5. 大分组是否会因为超过一个 tick 而被错误丢弃；
6. 完成记录、部分发送和积压的统计口径是否一致。

最终公开/框架测试 18 项、自拟测试 2 项，共 20 项全部通过。`results/comparison.csv`
的 8 行结果与 `examples/teacher_results/comparison.csv` 逐项一致，说明服务顺序、
包头、缓存准入和统计窗口都与课程基线一致。

### 2.5 采纳理由

采用这一实现的原因是它直接对应模型合同，没有为了通过测试添加特判：

- 电路没有任何跨用户调度逻辑，空闲时隙自然保持空闲；
- 分组没有任何重新加头的分支，跨 tick 只保留同一个 `remaining_wire_bits`；
- 两个服务函数都以“预算大于 0 且队列非空”为循环条件，发完当前记录后自然继续；
- 指标函数先检查守恒，再计算比率，避免用不完整数据生成好看的结果。

## 三、自拟反例与断言

自拟测试位于 `student_tests/test_my_case.py`，输入和预期都先手算
用例，也没有只检查文件是否存在。

### 3.1 电路反例：不能用其他用户的时隙

输入：`users=2, slot_bits=100`。用户 0 的队列是 A=60 bit、B=60 bit，用户 1 的队列是 C=40 bit。

手算过程：

- tick 0 属于用户 0。先发 A 的 60 bit，预算剩 40 bit；再发 B 的 40 bit，B 还剩
  20 bit。本 tick 发送总量为 100 bit，完成列表只有 A。用户 1 的 C 完全不动。
- tick 1 属于用户 1。只发送 C 的 40 bit，发送量为 40 bit，完成列表为 C。用户 0
  的 B 仍应保持剩余 20 bit。

断言检查 `wire_bits`、`completed`、B 和 C 的 `remaining_wire_bits`，以及用户 1队列的长度。该用例能揭示两类错误：把空闲时隙自动借给其他用户，或者在发完一条
记录后没有继续使用同一用户的剩余预算。

### 3.2 分组反例：跨 tick 续传且不交错

输入：A 的 payload=150 bit，初始化 `remaining_wire_bits=182`；B 的 payload=20 bit，
初始化 `remaining_wire_bits=52`；共享队列为 `[A, B]`。

手算过程：

- tick 0：只处理队首 A。发送 128 bit，A 剩 `182 - 128 = 54` bit；B 不能被处理，
  仍为 52 bit；本 tick 没有完成记录。
- tick 1：先发 A 的 54 bit，预算剩 74 bit；再发 B 的 52 bit，预算还剩 22 bit。
  本 tick 共发送 `54 + 52 = 106` bit，A、B 都完成，队列清空。

断言检查两次发送量、完成顺序、A 和 B 的剩余量以及最终队列是否为空。该用例能揭示
三类错误：跨 tick 时重复加 32 bit 包头、大记录超过一个 tick 就被丢弃、以及越过
未完成的队首去服务下一条。

## 四、核心逻辑解释

### 4.1 事件顺序

每个 tick 的顺序固定为：先把本 tick 到达的记录做缓存准入，再调用发送函数，最后在tick 结束边界统计完整交付。记录在 tick+1 边界完成，因此 `delay_ticks` 是完成 tick减到达 tick。观察窗口到 `cfg.ticks` 立即停止，不额外增加排空阶段。

### 4.2 电路发送循环

电路发送可以概括为：

```text
user = tick % cfg.users
queue = queues[user]
budget = cfg.slot_bits
while budget > 0 and queue:
    record = queue[0]
    sent = min(record.remaining_wire_bits, budget)
    record.remaining_wire_bits -= sent
    budget -= sent
    if record.remaining_wire_bits == 0:
        queue.popleft()
        completed.append(record)
```

这段循环保证了三件事：预算不会被超过；部分发送的记录仍在队首；预算有剩余时继续服务同一用户的下一条。`queues` 中其他用户的队列从未被访问，所以空闲时隙不可能被借用。

### 4.3 分组发送循环

分组发送的循环结构相同，但它只操作一个共享 `deque`。`Pending` 在准入时已经设置
`remaining_wire_bits = payload_bits + header_bits`，循环中只做减法。队首没有发完时
不会执行 `popleft`，所以下一条永远得不到服务；队首发完后如果预算还有剩余，循环
自然继续处理下一条。包头只存在于初始化后的剩余量中，跨 tick 不会再次增加。

### 4.4 指标与守恒

统计时必须区分四种量：

- `generated_payload_bits`：本窗口生成的全部原始 payload；
- `delivered_payload_bits`：完整交付记录的原始 payload；
- `dropped_payload_bits`：缓存准入失败而整条尾丢弃的 payload；
- `backlog_payload_bits`：窗口结束时所有未完成记录的原始 payload。

四者满足 `generated = delivered + dropped + backlog`。部分发送的记录虽然有 wire
已经上线，但在完整交付前仍属于积压，不能把已发送部分重复算成交付。线路忙碌率使用
`wire_sent_bits`，包含包头和未完成记录的已发送部分，因此它和有效载荷利用率不是同一个概念。

### 4.5 容易写错的边界

1. 单个 tick 的容量是 `cfg.slot_bits`，不能再乘以用户数。
2. 分组的 32 bit 包头只在准入时计一次，跨 tick 续传不能重复加。
3. 电路当前用户队列为空时返回 `(0, [])`，不能借用其他用户的时隙。
4. 部分发送只能扣减 `remaining_wire_bits`，不能修改 `payload_bits`，也不能报告完成。
5. 未完成记录的完整原始 payload 都算积压，不能只算剩余 wire。
6. 没有完成记录时时延是 `None`，不是 0；否则会制造虚假的低时延。
7. 缓存准入先于本 tick 发送，不能因为本 tick 稍后能发就临时放宽准入。
8. 观察窗口结束后不排空，不能为了降低积压而额外增加发送时间。

## 五、验证结果与可复核证据

公开/框架测试的分布是：电路 4 项、分组 4 项、指标 3 项、集成 3 项、框架 4 项，
共 18 项；加上自拟测试 2 项，共 20 项全部通过。结果文件检查结果为 8 行指标、
8 组轨迹，所有轨迹都满足守恒式。

四种业务的主要结果如下（详细数值见 `results/comparison.csv`）：

| 场景 | 电路有效载荷利用率 | 分组有效载荷利用率 | 电路平均时延 | 分组平均时延 |
|---|---:|---:|---:|---:|
| continuous | 100.00% | 79.69% | 2.50 ms | 26.15 ms |
| staggered_burst | 49.22% | 75.00% | 45.10 ms | 1.00 ms |
| synchronized_burst | 33.98% | 32.81% | 12.71 ms | 15.36 ms |
| light_random | 21.09% | 21.09% | 3.11 ms | 1.10 ms |

这些结果说明：错峰突发和轻载场景下，共享 FIFO 的统计复用可以明显降低时延或提高利用率；
持续满载时，分组包头会挤占有效载荷容量，导致排队、丢失和积压；
同步突发时分组也未必在所有指标上优于电路。结论必须结合利用率、时延、丢失和积压一起看。

本次验证环境中的全局 Python 没有安装 `pytest` 和 `matplotlib`，因此使用本机
Python 3.12 直接执行测试函数和仿真，并单独检查了 CSV、JSON 和 3 张 PNG。安装
`requirements.txt` 后，在仓库根目录运行 README 中的标准命令即可得到同样的结果。

可复核文件：

- `src/part1_circuit.py`：电路发送实现；
- `src/part2_packet.py`：分组发送实现；
- `src/metrics.py`：指标与守恒检查；
- `student_tests/test_my_case.py`：两个自拟反例与断言；
- `results/comparison.csv`：8 行指标；
- `results/comparison.json`：配置、8 行指标和 8 组轨迹；
- `results/comparison_metrics.png`、`queue_occupancy.png`、`pcm_frame_view.png`：
  三张实际生成的图。

## 六、AI 使用边界与我的理解

这次 AI 的主要作用是阅读材料、给出实现建议、生成初稿和帮助整理验证步骤。代码是否
符合模型不能只靠“测试绿色”判断，因此我又用两用户手算和两个独立反例检查了预算、
包头、FIFO 和积压口径。AI 没有修改提供的测试、评分脚本或工作流，也没有把参考结果当成自己的运行结果。

我现在能够独立解释三个核心判断：第一，电路为什么只能访问
`queues[tick % cfg.users]`；第二，分组为什么在跨 tick 时只能继续扣减同一个
`remaining_wire_bits`；第三，为什么 `backlog` 要使用未完成记录的原始 payload，
并且必须和 `delivered`、`dropped` 一起满足守恒式。后续如果改变包头、缓存或业务参数，我会先重新手算一个最小例子，再运行测试，而不会直接沿用当前结论。
