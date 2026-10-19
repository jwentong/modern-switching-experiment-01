# 实验一项目规则

## 范围和授权
- 本目录仅用于现代交换原理实验一，教师基线提交为 bc9099e3f932168af640ce0d03abc2c3f283e10f。
- 用户于 2026-10-19 授权读取、创建和补充本项目规则；后续重新处理 AGENTS.md 前仍须询问。
- 仅实现三个学生 TODO，补充学生测试、参数实验、报告、AI 记录与真实运行产物。
- 不修改教师接口、业务生成、仿真框架、grading、评分脚本或 .github/workflows。
- 删除、修改凭据或 CI/CD、数据库迁移、安装全局依赖或修改系统设置、git push/rebase/reset --hard、公开发布之前必须单独询问用户。

## 目录和命名
- src/ 保留教师结构，仅修改 part1_circuit.py、part2_packet.py、metrics.py 中的目标函数。
- student_tests/test_my_case.py 保存独立边界测试，注明先验计算和错误识别依据。
- student_tests/run_parameter_experiment.py 保存可复现的附加参数实验入口。
- results/ 根目录只放默认配置的 JSON、CSV 和三张 PNG；附加结果放 results/extra/，名称明确表明参数。
- REPORT.md 为实际结果报告，AI_LOG.md 如实记录本次协作，不伪造学生独立手算、理解确认或操作。
- .venv/ 是本项目虚拟环境，不上传。保留教师原文件名；不混放其他课程或私人文件。
- 不自行清理文件；需要清理时先列明对象并请求授权。

## 模型和验证
- 两模型使用同一输入、容量、缓存和观察窗口；电路不借时隙，分组不重复加头。
- 部分发送不计完整交付，未完成记录按原始 payload 计积压；无完成样本的时延为 None。
- 每次只完成一个目标函数，验证后再进入下一个；不通过改测试或忽略错误提高分数。
- 所有命令在项目根目录执行，使用 .venv/Scripts/python.exe。
- 起点检查：src/test_environment.py 与 pytest grading/test_framework.py -q。
- 分项检查：pytest grading/test_circuit.py -q、pytest grading/test_packet.py -q、pytest grading/test_metrics.py -q。
- 完整验证：src/performance_test.py、pytest grading/test_integration.py -q、pytest student_tests -q、grading/calculate_grade.py。
- 复核基线 8 行指标与 8 组轨迹、守恒、相同参数重复运行一致、三张图可读。
- 自动项最高 70 分，人工项及最终成绩待教师确认；本地通过不等于已提交或已获成绩。
- 姓名、学号、GitHub 账号由用户提供；缺失时明确标为待提供，不编造。用户理解及手算确认单独列为待完成。
