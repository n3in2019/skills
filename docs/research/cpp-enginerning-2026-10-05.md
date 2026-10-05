# cpp-enginerning 深入研究与验证

日期：2026-10-05。基线：`757f40ccbe033ac4c3b54dd0bd0b78e4e3b44fdc`。

## 结论

保留“契约 → 最小上下文 → 小步变换 → 验证 → 停止”的核心。最值得增加的是判断条件、验证真实性和可重复评测。继续增加未经场景检验的口号，会扩大上下文和规则冲突，却不能证明代理更可靠。

本次核对作者文章、C++ Core Guidelines/工作草案、LLVM/GCC/CMake/Google Benchmark 文档及代理上下文/评测资料。来源与适用边界见 [sources.md](../../skills/cpp-enginerning/references/sources.md)。没有重新通读付费书籍全文，不宣称给出 ISO 合规认证。

## 现有规则的主要缺口与处理

| 现状 | 工程风险 | 本次处理 |
| --- | --- | --- |
| “保持行为”主要以泛化文字表达 | 提取后返回值没变，但析构、锁或错误路径改变 | 明确观察顺序与资源寿命，补正常/早退/异常的评测 |
| 要求运行测试，未明确测试发现 | 错误过滤器执行 0 个用例也成功 | 核实用例数量、skip、NDEBUG 与实际断言 |
| 提到 sanitizer，缺少判定规则 | UBSan 报错仍退出 0；运行器受阻被误当通过 | 检查诊断、恢复策略、插桩范围与 BLOCKED |
| C++ 检查覆盖所有权，但协程表述较笼统 | 按值捕获 shared_ptr 仍可能依赖已销毁闭包 | 区分闭包、协程帧、引用/this/view 的寿命 |
| 上下文限制可能促使机械拆分 | 调用者反而需要跨多个文件理解一个概念 | 用契约与变化原因划界，允许内联错误抽象 |
| 基于项目设置检查标准，但缺乏工具证据 | 配置声明、实际命令和标准库支持不一致 | 检查真实 target/compile database，识别标准回退 |
| 机器人规则与通用 C++ 混放 | 普通项目加载无关检查，迁移其他项目政策 | 平台检查独立按需加载，当前仓库事实优先 |
| 验证只到 Markdown 和示例 | 无法知道代理是否执行了所写规则 | 新增行为夹具、独立 grader、前后重放和限制记录 |

## 关键裁决及一手依据

### 1. “函数短”不能成为自动拆分算法

[Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) 强调有意义的操作与资源/并发规则，但同时承认指南需要适配代码库、并非语言标准。这里的工程裁决是：提取必须得到可说明的概念，并核对 C++ 作用域语义。主流程保留短步骤，判断细节按需读。

函数长度、参数数量、重复次数可触发调查，但不独立决定重构。测试接缝、ABI 和实时路径可能使不同方案成立。项目标准、异常和分配政策不能从另一个项目继承。

### 2. 只去除真正共享的规则

[Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) 提醒错误抽象可比重复更昂贵；[Fowler 的 YAGNI](https://martinfowler.com/bliki/Yagni.html) 约束猜测未来需求的工作。本 skill 的裁决：比较变化原因与消费者，而不是匹配文本形状。出现越来越多开关时调查边界，必要时内联再抽取；不能把所有参数化算法一律判错。

### 3. 行为契约必须包含资源和失败

[Fowler 的重构定义](https://martinfowler.com/bliki/DefinitionOfRefactoring.html) 以可观察行为保持为核心。对 C++，我们将其落实为任务相关的返回值、错误、外部副作用、资源释放、回调线程和兼容边界。

在线 C++ 工作草案的 [basic.life](https://eel.is/c++draft/basic.life) 与 [intro.races](https://eel.is/c++draft/intro.races) 支持寿命和数据竞争的重要性。旧代码含 UB 时，某次输出不能升级为合法契约；应单列缺陷，不承诺保留 UB。在线草案会更新，具体语言争议需回到项目版本。

### 4. 验证的对象是实际行为，不是命令看起来成功

[CMake](https://cmake.org/cmake/help/latest/manual/ctest.1.html) 提供无测试处理选项；[UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) 文档说明许多检查可恢复执行。[GCC 插桩文档](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html) 是本次本机探针的工具依据。

本地 GCC 13.3.0 实测：signed overflow 在默认 UBSan 恢复模式下输出诊断但退出 0；fail-fast 配置输出诊断并退出 1。独立小型测试运行器的过期选择器返回 0 且 `tests=0`。这两种结果都不能算行为通过。

当前环境没有 CMake/CTest/Clang/clang-tidy，因此没有本机验证这些工具的具体命令，也没有 TSan、目标硬件或 ABI 矩阵结果。文档核对与工具实测分别记录。

### 5. 性能结论要求测量边界

[Google Benchmark](https://google.github.io/benchmark/user_guide.html) 提供计时、重复、预热和优化控制。工程裁决是：明确指标与真实工作，保存可比较的样本；单次 microbenchmark 均值不能替代系统尾延迟。防优化辅助函数也不保证整个表达式未被化简。本次没有性能提升结论。

### 6. 让规则可选择，并验证最终结果

[上下文工程文章](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 支持按需检索和精简上下文；[代理评测文章](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) 区分 trial、轨迹与最终状态。本次保留 54 行主流程，将风险细节分文件；资料多不意味着每次全加载。

[Google 代码审查标准](https://google.github.io/eng-practices/review/reviewer/standard.html) 支持有质量门槛的持续改进。停止条件是完成需求、验证风险、解释 diff，而非满足无限风格偏好。

### 7. 接口保证与异步状态分别建模

新增 API 资料：输入域、所有权、失败后状态、重入/阻塞、兼容边界与成本。依据 [Abrahams 的异常安全论文](https://www.boost.org/doc/libs/1_31_0/more/generic_exception_safety.html) 区分基本/强保证；不把 noexcept 等同于必定成功，也不把本地 RAII 当作外部副作用回滚。

新增异步资料：接受、取消请求、完成与销毁是不同事件。迟到回调必须核对所属操作，不能只共享 active 布尔值；此策略仍须符合调度与分配预算。协程检查闭包、帧与借用对象三条寿命；[clang-tidy 的对应检查](https://clang.llvm.org/extra/clang-tidy/checks/cppcoreguidelines/avoid-capturing-lambda-coroutines.html) 也明确按值捕获智能指针仍存在闭包风险。

## 行为评测结果

使用两个相同任务分别测试旧版和候选版，另加候选版只读审查，再以第二阶段候选执行取消与协程任务。各 trial 为新上下文与独立目录。主代理独立检查产物，不以子代理自称成功作判定。

| 任务 | 旧版 | 候选版 | 独立证据 |
| --- | --- | --- | --- |
| 提取准备/分发，保留 Lease 寿命与事件顺序 | 通过 | 通过 | grader 各 9 项通过；新增用例前后各 18 项通过 |
| 修复 port 数字前缀接受错误 | 通过 | 通过 | grader 各 18 项通过；代理新增回归在旧代码失败、新代码通过 |
| 过期测试过滤器 | 两者均发现 `tests=0`，改用正确选择器 | 同左 | 代码/README 产物及运行器探针；完整交互轨迹未导出 |
| 异步输出只读审查 | 未运行 | 通过本用例人工判定 | 识别 view 和 this 两条寿命问题，未误报同步 peek，原文件未变 |

| 取消/重启后旧完成 | 未运行 | 通过本用例 | 独立 grader 8 项通过；新增 13 项在旧代码失败 9 项、修复后全部通过 |
| 捕获 lambda 协程只读审查 | 未运行 | 通过本用例人工判定 | 正确区分安全值参数正例；独立 ASan 复现闭包 stack-use-after-return |

额外对 grader 注入提前释放 Lease 的错误，能检测失败；原始 port 缺陷被独立隐藏用例检测。新增测试没有只与实现逐行互相印证。

这组任务很小，且旧版同样通过，不能推导候选版成功率更高。没有无 skill 对照、重复 trials、跨模型、真实大仓库、ABI/多线程全面评测，也没有 token 或时间成本统计。除已独立重跑的协程 repro 外，其他代理自报 sanitizer 结果未纳入独立复测成功数。

复跑方法、哈希、补丁及 JSON 证据见 [evaluation](../../evaluation/cpp-enginerning/README.md)。

## 已落实及下一轮

本版主流程 54 行；设计取舍、API/值语义、异步状态、验证、平台检查、示例与来源按需加载。根目录继续支持多个独立 skill，通用 improve-code-quality 保持独立。

另一次只读质量评审发现并修正：port grader 漏查成功返回值、审查模式补测试措辞歧义、工具阻塞分类不足、review 结果缺少可审阅记录。port grader 补强后对全部产物重跑，并用“合法输入统一写入 65535”的错误实现验证其会失败。

7 次 trial 使用两个候选阶段；最终只读措辞与来源修正未再跑代理。未固定 seed/精确模型构建号，未导出完整轨迹，没有宣称最终文字的每个组合均已验证。哈希与阶段见评测目录。

下一轮优先旧 ABI 消费方、条件编译/工具链差异及真实项目的并发任务。使用固定模型和预算、多次运行、无 skill/旧版/新版对照，同时记录结果、范围、额外上下文成本；只有观察到重复失败时才增加规则。
