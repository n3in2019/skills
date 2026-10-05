# cpp-enginerning 行为评测

这些是小型、可重复的能力/回归探针，不是生产代码示例。`fixtures/port.hpp`、`fixtures/async.hpp` 故意含缺陷，port 的 README 测试选择器也故意过期；session 和 coroutine 同样包含任务指定缺陷。
评测资料位于 skill 之外；安装 skill 无需复制此目录。

## 用例与判定

| 用例 | 交给代理的任务 | 判定 |
| --- | --- | --- |
| lifetime | 将 process 的准备和分发提取为命名操作 | API 保持；正常、早退、异常时事件/资源次序保持；实现确实提取了有意义的操作 |
| port | 修复合法数字前缀后有额外字符仍被接受 | 合法范围/输出契约保持；回归先失败后通过；发现测试过滤器执行 0 个用例 |
| session | 修复取消/重启后迟到完成 | 旧操作不发布、不消耗新操作；每个操作最多发布一次 |
| coroutine | 只读审查捕获 lambda 协程与值参数正例 | 区分闭包与协程帧寿命；不改源文件 |
| review | 只读审查异步输出 | 定位 message/view 与 this 的两条寿命问题；不误报合法同步借用 peek；不改代码 |

`grade_run.py` 使用独立的可信测试编译代理结果，不读取代理修改后的测试来判定行为。它检查 lifetime 的 9 项与 port 的 18 项；session 的 8 项；review/coroutine 仅自动检查原文件未变，发现质量需要人工复核。不要只凭退出码宣称全部评测通过。
手工还要检查任务完成、范围、API/标准/依赖是否漂移，以及最终报告是否匹配证据。隐藏用例是未交给代理的用例，不是安全隔离或对恶意绕过的保证。

## 复跑

在仓库根执行，需要 Python 3 和支持 C++17 的 `c++`，不安装依赖、不访问网络：

```bash
python3 evaluation/cpp-enginerning/prepare_run.py lifetime /tmp/cpp-trial-01 --skill skills/cpp-enginerning
```

为新代理提供如下任务（每次使用新的目录和会话）：

> 仅在 /tmp/cpp-trial-01 工作。读取 README 和 TASK.txt，使用 .agents/skills/cpp-enginerning/SKILL.md 完成任务；不要读取兄弟目录或评测目录，不改 skill，不访问外部服务。报告实际修改和验证命令/结果。

代理结束后，由评测者执行：

```bash
python3 evaluation/cpp-enginerning/grade_run.py lifetime /tmp/cpp-trial-01
```

将 `lifetime` 换为 `port` 、`review`、`session` 或 `coroutine` 生成其他任务。不要给代理 grader、预期结论、其他 trial 输出。为比较旧版，从 `757f40c` 取出其完整 skill 目录作为 `--skill`；夹具、任务提示和模型/工具预算保持一致。

假通过探针（只验证工具行为，不调用模型）：

```bash
python3 evaluation/cpp-enginerning/probe_validation.py
```

UBSan 两种配置的预期结果为：recover 出现诊断但退出 0；failfast 出现诊断且非零退出。具体运行器/平台不支持时检查 BLOCKED，不套用本次结果。

## 本次执行与限制

2026-10-05：同一会话继承的模型/宿主配置，两个任务各跑旧/新版一次，另跑一次新版 review，随后第二阶段候选版各跑 session 与 coroutine，共 7 个独立上下文 trial。协程 repro 需要 C++20。未覆盖所有参数组合，未固定 seed，未收集 token/耗时，精确模型构建号未在评测产物中锁定。

所有 trial 使用独立目录，通过任务指令限制读取范围；未实施独立文件系统权限隔离。根协作者复核实现 diff，并独立编译 grader 与重放代理新增用例的前后行为。
保存了文件 diff、skill 文件哈希、独立 grader JSON 和重放证据。完整代理工具轨迹未导出；代理自报的额外 sanitizer 检查不计入独立复测结果。review 的语义判定基于代码与最终发现人工核对，保留 [发现记录](results/2026-10-05-review-findings.md)。coroutine 的保留 repro 已独立重跑。

结果见 [outcomes](results/2026-10-05-outcomes.json)、[regression replay](results/2026-10-05-regression-replay.json)、[probes](results/2026-10-05-probes.json)、[grader negative](results/2026-10-05-grader-negative.json)。a/c 使用旧版，b/d/e 使用第一阶段候选，f/g 使用增加 API/异步资料后的第二阶段候选。最终版另修正 review 只读措辞与来源链接，未重新调用代理；精确输入以哈希记录为准。port grader 后续补强成功值断言并对全部产物重跑；原始 trial 的输入未改写。

结论只支持“这些任务没有观察到候选版回归”，不支持成功率提升、跨模型泛化或安全证明。
后续优先新增 ABI 消费方和宏/工具链差异任务；多次重跑同一模型/预算，再进行技能消融对照（无 skill/旧版/新版）。这些扩展本次 NOT RUN。
