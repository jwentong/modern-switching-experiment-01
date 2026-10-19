###### \# AI 协作记录

###### 

###### \## 记录 1：环境问题——虚拟环境中缺少 pytest

###### 

###### \- \*\*真实需求\*\*：运行 `grading/test\_framework.py` 时提示

###### &#x20; `.venv\\Scripts\\python.exe: No module named pytest`，需要在不破坏虚拟环境的前提下让测试跑起来。

###### \- \*\*AI 建议\*\*：确认当前目录和解释器路径；在 `.venv` 中安装 `requirements.txt` 和 `pytest`；

###### &#x20; 统一用 `.\\.venv\\Scripts\\python.exe -m pytest` 调用，避免误用系统全局 pytest。

###### \- \*\*我的验证\*\*：执行

###### &#x20; `.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt`

###### &#x20; 和 `.\\.venv\\Scripts\\python.exe -m pip install pytest`，

###### &#x20; 再用 `.\\.venv\\Scripts\\python.exe -m pytest --version` 确认；

###### &#x20; 最后 `test\_framework.py` 显示 4 passed。

###### \- \*\*采纳/修正理由\*\*：采纳“显式调用 .venv 解释器 + 单独安装 pytest”的做法，

###### &#x20; 因为 requirements.txt 不一定包含 pytest，且直接输入 `pytest` 可能落到全局环境。

###### 

###### \## 记录 2：环境问题——PowerShell 找不到 git

###### 

###### \- \*\*真实需求\*\*：在 11.3 执行 `git clone` 时报

###### &#x20; `无法将“git”项识别为 cmdlet、函数、脚本文件或可运行程序的名称`。

###### \- \*\*AI 建议\*\*：先用 `git --version`、`where.exe git`、`Test-Path "C:\\Program Files\\Git\\cmd\\git.exe"`

###### &#x20; 区分“未安装”和“未加入 PATH”；安装 Git for Windows 时勾选

###### &#x20; “Git from the command line and also from 3rd-party software”；安装后关闭并重开终端。

###### \- \*\*我的验证\*\*：安装 Git 后重开 PowerShell，`git --version` 正常输出版本号，

###### &#x20; 再执行 `git clone https://github.com/Lxiang-holl/modern-switching-experiment-01.git` 成功。

###### \- \*\*采纳/修正理由\*\*：采纳“先诊断再安装/配 PATH”的顺序，避免直接改 PATH 造成重复追加。

###### 

###### \## 记录 3：serve\_circuit 固定时隙发送

###### 

###### \- \*\*真实需求\*\*：补全 `src/part1\_circuit.py` 的 `serve\_circuit`，

###### &#x20; 要求当前服务用户 = `tick % cfg.users`，空时隙不借给其他用户，

###### &#x20; 部分发送只扣 `remaining\_wire\_bits`，不误报完成。

###### \- \*\*AI 建议\*\*：用 `while budget > 0 and q` 循环，取 `q\[0]`，

###### &#x20; `send = min(budget, rec.remaining\_wire\_bits)`，

###### &#x20; 只有 `remaining\_wire\_bits == 0` 才 `popleft()` 并加入完成列表，否则 `break`。

###### \- \*\*我的验证\*\*：先按 AC01、AC02 手算：

###### &#x20; 当前用户队列空时返回 `(0, \[])`；200 bit 记录、容量 128 时首 tick 发 128、剩 72。

###### &#x20; 再运行 `.\\.venv\\Scripts\\python.exe -m pytest grading/test\_circuit.py -q`，结果 4 passed。

###### \- \*\*采纳/修正理由\*\*：采纳循环结构；特别核对“空时隙不能借出”和“部分发送不完成”两个边界。

###### 

###### \## 记录 4：serve\_packet 共享 FIFO 与包头只计一次

###### 

###### \- \*\*真实需求\*\*：补全 `src/part2\_packet.py` 的 `serve\_packet`，

###### &#x20; 确认 `remaining\_wire\_bits` 已由框架初始化为 `payload\_bits + header\_bits`，

###### &#x20; 函数内不能再加包头；大记录可跨 tick，不抢占、不交错。

###### \- \*\*AI 建议\*\*：与电路类似用预算循环，但\*\*不加\*\* `header\_bits`；

###### &#x20; 发完队首有剩余预算继续下一条；未完成时 `break` 保证 FIFO。

###### \- \*\*我的验证\*\*：按 AC03、AC04 手算：

###### &#x20; payload 96、wire 128 时一个 tick 完成，不能再加 32；

###### &#x20; A wire 232、B wire 64 时首 tick 发 A 128，A 余 104、B 不变。

###### &#x20; 运行 `test\_packet.py`，结果 4 passed。

###### \- \*\*采纳/修正理由\*\*：采纳“循环内继续发下一条”的结构；

###### &#x20; 明确拒绝“函数内再加一次包头”的写法，避免 wire 多 32。

###### 

###### \## 记录 5：summarize 字段名错误与修正

###### 

###### \- \*\*真实需求\*\*：补全 `src/metrics.py` 的 `summarize`，

###### &#x20; 返回 6 个规定键，无完成记录时时延为 `None`，无生成时丢失率为 0，

###### &#x20; 守恒不成立抛 `ValueError`。

###### \- \*\*AI 建议（第一次）\*\*：使用 `raw\["wire\_bits\_sent"]` 和 `raw\["completed\_records"]`。

###### \- \*\*实际验证与错误\*\*：运行 `test\_metrics.py` 报

###### &#x20; `KeyError: 'wire\_bits\_sent'`，3 failed。

###### &#x20; 从 `test\_empty` 的 `a.update(..., wire\_sent\_bits=0, completed=\[])`

###### &#x20; 发现实际键名是 `wire\_sent\_bits` 和 `completed`。

###### \- \*\*修正\*\*：改为

###### &#x20; `wire\_sent = raw.get("wire\_sent\_bits", raw.get("wire\_bits\_sent", 0))`，

###### &#x20; `completed = raw.get("completed", raw.get("completed\_records", \[])) or \[]`，

###### &#x20; 并把守恒检查放在最前面，保证 `test\_conservation` 能正确抛 `ValueError`。

###### \- \*\*结果\*\*：`test\_metrics.py` 3 passed。

###### \- \*\*采纳/修正理由\*\*：采纳 AI 的计算口径（分母 `ticks × slot\_bits`、

###### &#x20; 无完成返回 `None`、守恒抛 `ValueError`），但\*\*修正字段名\*\*，

###### &#x20; 以公开测试和 `models.py` 为准，不照搬建议中的键名。

###### 

###### \## 记录 6：自拟反例

###### 

###### \- \*\*真实需求\*\*：在 `student\_tests/test\_my\_case.py` 写一个独立反例，

###### &#x20; 揭示“重复加头”或“部分发送误记完成”等错误。

###### \- \*\*AI 建议\*\*：构造 payload=200、header=32、`remaining\_wire\_bits=232`、

###### &#x20; `slot\_bits=128`，手算 tick 0 发 128 剩 104、tick 1 发 104 完成，

###### &#x20; 总 wire=232；断言 tick 0 的完成列表为空、`payload\_bits` 不变。

###### \- \*\*我的验证\*\*：先手算再写 `assert`，运行

###### &#x20; `.\\.venv\\Scripts\\python.exe -m pytest student\_tests -q`，结果 1 passed。

###### \- \*\*采纳/修正理由\*\*：采纳该反例，因为它同时覆盖“重复加头”和

###### &#x20; “部分发送误记交付”两个边界，且断言可独立复现。

###### 

###### \## 总体说明

###### 

###### \- 使用的工具：对话式 AI 助手（用于解释模型、建议实现、排查环境与字段名错误）。

###### \- AI 参与范围：解释规则、给出函数骨架、帮助定位 pytest/git 环境问题和 `KeyError` 字段名问题。

###### \- 我的责任：所有代码均在本地保存、运行公开测试和自拟反例验证；

###### &#x20; 字段名以 `src/models.py` 和 `grading` 测试为准；

###### &#x20; 报告中的数据来自本人实际运行 `performance\_test.py` 的结果。

###### \- 未采纳的内容：AI 首次给出的 `wire\_bits\_sent` / `completed\_records` 键名，

###### &#x20; 经测试验证后改为 `wire\_sent\_bits` / `completed`。

