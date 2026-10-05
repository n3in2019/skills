# 规则依据与适用边界

核对日期：2026-10-05。以下为维护者/作者/标准工作草案的一手资料，采用独立归纳，不大段摘录书籍。主流程是本项目的综合裁决，不是任何来源的官方完整清单。

| 依据 | 支持的判断 | 使用边界 |
| --- | --- | --- |
| [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)（F.1–F.3、R、CP.22、CP.51–53） | 意图、职责、资源与协程风险 | 指南并非语言标准；按项目条件渐进采用，不强制统一异常/分配政策 |
| [工作草案 basic.life](https://eel.is/c++draft/basic.life) | 对象寿命影响引用与访问合法性 | 在线草案会更新；争议应核对项目采用的标准版本 |
| [工作草案 intro.races](https://eel.is/c++draft/intro.races) | 数据竞争涉及同步关系，不能靠单线程输出证明正确 | 不把 draft 当作编译器支持承诺 |
| [Fowler: Definition of Refactoring](https://martinfowler.com/bliki/DefinitionOfRefactoring.html) | 结构调整保持可观察行为 | 本 skill 将相关错误、寿命、时序纳入具体任务契约 |
| [Fowler: Preparatory Refactoring](https://martinfowler.com/articles/preparatory-refactoring-example.html) | 可先做帮助当前需求的小步整理 | 不授权全仓库重写 |
| [Fowler: YAGNI](https://martinfowler.com/bliki/Yagni.html) | 避免猜测未来需求的能力 | 不禁止当前确实需要的测试接缝 |
| [Sandi Metz: The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) | 错误抽象可以内联后重新识别重复 | 不能仅凭有参数/条件分支就宣判抽象错误 |
| [Google: Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) | 持续改进、事实优先、风格意见非阻塞 | 不用“无需完美”放过正确性和兼容缺陷 |
| [Anthropic: Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 按需检索、紧凑上下文、代表性示例 | 是产品方工程经验，不证明本 skill 的效果 |
| [Anthropic: Agent Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 分开任务、trial、轨迹与最终状态；重复评测 | 测试结果与轨迹共同审查，小样本不能推导普遍提升 |
| [CTest manual](https://cmake.org/cmake/help/latest/manual/ctest.1.html) | 无测试处理、发现与执行应区分 | 核实本机版本是否支持对应参数 |
| [CMake CXX_STANDARD](https://cmake.org/cmake/help/latest/prop_tgt/CXX_STANDARD.html) | 标准属性可能回退；检查 REQUIRED/实际配置 | 不自动更改项目最低标准 |
| [CMake compilation database](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html) | 分析应使用真实编译参数 | 生成器/构建模式有支持范围 |
| [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) | 数据库、局部配置和定向检查 | 诊断需核查，自动 fix 不是正确性证明 |
| [ASan](https://clang.llvm.org/docs/AddressSanitizer.html) / [UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) | 按风险选择内存/UB 检查，检查诊断与恢复策略 | 受启用项、执行路径、工具链影响 |
| [GCC instrumentation](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html) | sanitizer 恢复策略和组合限制 | 本地探针使用 GCC，不将 Clang 文档中的具体选项一概套用 |
| [TSan](https://clang.llvm.org/docs/ThreadSanitizer.html) / [维护者手册](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual) | 竞争检测的运行覆盖和插桩限制 | 无报告不证明所有调度正确 |
| [Google Benchmark User Guide](https://google.github.io/benchmark/user_guide.html) | 重复、预热、计时、优化与原始结果 | 防优化函数也不保证表达式未被化简 |

补充接口/异步依据：

- [LLVM coroutine lambda 检查](https://clang.llvm.org/extra/clang-tidy/checks/cppcoreguidelines/avoid-capturing-lambda-coroutines.html)：定位闭包寿命风险，工具不可用时不能伪报执行结果。
- [工作草案 expr.await](https://eel.is/c++draft/expr.await)、[stop token](https://eel.is/c++draft/thread.stoptoken.intro)：挂起/恢复与停止请求；项目 C++ 版本和库实现仍须核实。
- [工作草案 moved-from](https://eel.is/c++draft/lib.types.movedfrom)、[except.spec](https://eel.is/c++draft/except.spec)：移动后状态和异常规范；不把标准库要求机械套给用户类型。
- [Boost 异常安全](https://www.boost.org/doc/libs/1_31_0/more/generic_exception_safety.html)：失败保证与泛型组件；不要求业务 I/O 具备可回滚事务。
- [CMake target_link_libraries](https://cmake.org/cmake/help/latest/command/target_link_libraries.html)：依赖传播依据。
- [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html)、[libstdc++ Dual ABI](https://gcc.gnu.org/onlinedocs/libstdc++/manual/using_dual_abi.html)：具体二进制兼容维度；不代表所有平台，也不承诺跨工具链兼容。

《代码整洁之道》《重构》是最初需求背景。本版不声称重新通读付费书籍全文，也不把某位作者的风格偏好提升为 C++ 语言约束。保留可解释、可检验的规则；新增规则应对应实际失败模式或明确契约。
