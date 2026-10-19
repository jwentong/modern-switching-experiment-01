# 独立验证与复现

- `PREDICTIONS.md`：运行前的手算预期和业务预测，真实协作过程见根目录 AI_LOG.md。
- `test_my_case.py`：8 项参数展开后的断言，覆盖两用户基准、部分发送保留完整缓存、只差 1 bit 的窗口边界、时间单位缩放及单用户零包头等价性。
- `run_extra.py`：只改变包头或缓存，生成 results/extra/ 的 72 组附加实验，不覆盖默认基线。
- `verify_artifacts.py`：独立检查 80 组数据、CSV/JSON、预算、守恒和控制变量，记录产物 SHA256。
- `requirements-lock.txt`：本次实际依赖版本，不改变教师 requirements.txt。
- `run_all.ps1`：使用现有项目 .venv 完成本地复现；不上传、不创建 PR。

在仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe -m pytest student_tests -q
powershell -ExecutionPolicy Bypass -File student_tests/run_all.ps1
```
