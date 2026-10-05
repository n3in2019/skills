# 只读审查的人工判定记录

这是主协作者根据代理最终报告和夹具代码整理的发现记录，不是完整工具轨迹。

## Trial e：异步输出

- `Printer::submit` 将局部参数 message 的 string_view 保存到延迟回调；message 离开作用域后 view 悬空。明确缺陷。
- 回调捕获 this，而契约允许 Printer 在 submit 后立即销毁；随后访问对象成员会使用已销毁对象。独立于字符串寿命的第二条明确缺陷。
- `peek(const int&)` 只做同步借用，所给调用范围内未越过对象寿命，不构成同类缺陷。代理没有误报。
- 最小建议：让异步工作持有实际需要的数据，并明确对象/回调寿命；不能仅换成 shared_ptr 就宣称所有并发问题解决。
- 文件逐字保持，人工判定本用例通过。代理自报 ASan 复现未被主协作者独立重跑，不计入独立动态证据。

## Trial g：协程

- `make_task` 的局部捕获 lambda 在返回时销毁；初始挂起的协程仍会经闭包访问 state，shared_ptr 按值捕获不使闭包进入协程帧。
- 第二次 resume 解引用已销毁闭包；即使调用方保留 pointee 所有权，也不解决闭包寿命。明确缺陷。
- `make_safe_task` 的 shared_ptr 值参数由协程帧持有；有效非空输入下，跨挂起保留所有权，第二次 resume 增加值，销毁帧时释放。代理正确区分正例。
- 最小建议采用已有值参数协程模式，保留挂起顺序。源文件逐字保持，人工判定本用例通过。
- 主协作者独立重跑保留的 repro：safe exit=0，ownership exit=0（观察到不安全工厂在首次 resume 前失去所有权），unsafe exit=1 并报告 ASan stack-use-after-return。

复现（在仓库根执行，需要 GCC 的 C++20 与 ASan/UBSan 支持）：

```bash
c++ -std=c++20 -O0 -g -Wall -Wextra -Wpedantic -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=all evaluation/cpp-enginerning/results/coroutine-repro.cpp -o /tmp/coroutine-repro
ASAN_OPTIONS=detect_leaks=0:detect_stack_use_after_return=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 /tmp/coroutine-repro safe
ASAN_OPTIONS=detect_leaks=0:detect_stack_use_after_return=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 /tmp/coroutine-repro ownership
ASAN_OPTIONS=detect_leaks=0:detect_stack_use_after_return=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 /tmp/coroutine-repro unsafe
```

最后一条预期失败且有指定诊断；非零退出本身不证明复现。记录仅适用本环境；LeakSanitizer 因环境限制关闭。
