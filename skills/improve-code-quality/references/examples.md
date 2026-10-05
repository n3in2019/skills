# 小步重构示例

## C++：给共享判断命名，不扩大模块

任务：让重试条件可读。先读 `should_retry` 的声明、调用者和测试，确认 attempt 从 0 开始；只改此实现及相关测试。固定契约：仅超时或忙可重试，且 attempt 必须小于 max_attempts。此步不改变错误类型、ABI 或重试调度。

以下是可独立编译运行的 C++17 示例，before 是原实现，after 只提取命名谓词：

```cpp
#include <cassert>
#include <initializer_list>

enum class Error { none, timeout, busy, invalid };

bool should_retry_before(Error error, unsigned attempt, unsigned max_attempts) {
    return (error == Error::timeout || error == Error::busy)
        && attempt < max_attempts;
}

bool is_transient(Error error) {
    return error == Error::timeout || error == Error::busy;
}

bool should_retry_after(Error error, unsigned attempt, unsigned max_attempts) {
    return is_transient(error) && attempt < max_attempts;
}

int main() {
    // 契约断言独立于两份实现的比较，避免双方犯同样错误。
    assert(should_retry_after(Error::timeout, 0, 1));
    assert(should_retry_after(Error::busy, 1, 2));
    assert(!should_retry_after(Error::timeout, 2, 2));
    assert(!should_retry_after(Error::busy, 0, 0));
    assert(!should_retry_after(Error::invalid, 0, 3));
    assert(!should_retry_after(Error::none, 0, 3));
    for (auto error : {Error::none, Error::timeout, Error::busy, Error::invalid}) {
        for (unsigned limit = 0; limit <= 3; ++limit) {
            for (unsigned attempt = 0; attempt <= 4; ++attempt) {
                assert(should_retry_before(error, attempt, limit)
                    == should_retry_after(error, attempt, limit));
            }
        }
    }
}
```

将代码块保存为 `retry.cpp`，运行：

```bash
c++ -std=c++17 -Wall -Wextra -Werror -pedantic retry.cpp -o retry-check
./retry-check
```

检查原项目的相关目标构建与测试。谓词仅在本翻译单元使用时放入匿名命名空间；不要因此导出新 API。验证后停止，不顺手引入重试策略类、修改限额语义或添加重试线程。

## 语言无关：消除规则重复，保持副作用顺序

任务：订单确认和预览重复计算同一运费。先读两个入口、运费契约和持久化测试，确认二者共享规则：金额单位为分，满 10000 免运费，否则 800；零金额也收 800。保持通知、保存、返回的顺序。

Before（伪代码）：

```text
confirm(order):
    fee = 0 if order.subtotal_cents >= 10000 else 800
    save(order, fee)
    notify(order.id)
    return fee

preview(order):
    fee = 0 if order.subtotal_cents >= 10000 else 800
    return fee
```

After（只提取纯计算，入口各自保留副作用）：

```text
shipping_fee_cents(subtotal_cents):
    return 0 if subtotal_cents >= 10000 else 800

confirm(order):
    fee = shipping_fee_cents(order.subtotal_cents)
    save(order, fee)
    notify(order.id)
    return fee

preview(order):
    return shipping_fee_cents(order.subtotal_cents)
```

先为两个入口建立以下行为保护，再提取并运行同一测试：

| 场景 | 预期 |
| --- | --- |
| 金额 0、9999、10000、10001 | 费用依次 800、800、0、0 |
| confirm 保存成功 | 调用记录先 save 后 notify，返回费用 |
| save 失败 | 原错误向上传播，不调用 notify |
| notify 失败 | 保存已发生，原错误向上传播，不自动补偿或重试 |
| preview | 返回费用，不保存、不通知 |

不要将不同地区的其他运费逻辑一并抽象，除非确认也是同一规则。正常、边界与失败路径验证通过后停止。伪代码需映射到目标项目的测试框架，本示例本身不宣称可执行。
