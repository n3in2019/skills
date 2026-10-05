# AI 工程 Skills

多个独立、按需加载的 skill 集合。把工程原则转成 AI 的操作步骤、判断条件和验证要求，不复述书籍原文。

| Skill | 用途 |
| --- | --- |
| [cpp-enginerning](skills/cpp-enginerning/SKILL.md) | C++ 设计、实现、审查与重构，检查生命周期、并发、ABI 和成本 |
| [improve-code-quality](skills/improve-code-quality/SKILL.md) | 限制上下文与改动范围，改善边界并验证渐进重构 |

[AGENTS.md](AGENTS.md) 维护共用协作规则。每个 `skills/<name>/` 独立携带 `SKILL.md`、可选 `agents/openai.yaml` 和按需资源。新增 skill 只扩展自己的目录与本表，不将全部规则注入每次对话。

## 在其他仓库复用

以支持仓库内 `.agents/skills/` 的 Codex 环境为例，在目标仓库根目录执行（需要 Git，目标目录已存在时先审查合并，不覆盖）：

```bash
git clone https://github.com/n3in2019/skills.git /tmp/ai-engineering-skills
mkdir -p .agents/skills
cp -R /tmp/ai-engineering-skills/skills/cpp-enginerning .agents/skills/
```

使用 `$cpp-enginerning`，例如：

> 使用 $cpp-enginerning 修复当前解析错误。先定位接口、调用者和测试，限制到相关路径，保持其他输入行为并报告验证结果。

其他工具按其支持的 skill 目录放置完整目录；不支持自动加载时，显式要求读取 `SKILL.md`，再按需读取相对引用。只复制需要的 skill。

不要覆盖已有 `AGENTS.md`。合并以下导航，并补齐项目自己的构建/测试命令、语言版本和错误/兼容政策：

> 修改或审查代码时，读取 `.agents/skills/cpp-enginerning/SKILL.md`，只加载当前任务相关的实现、接口、调用者和测试；遵循本仓库约定。

## 维护与验证

Frontmatter 包含 `name`、`description`，名称与目录一致。用 skill-creator 的 `quick_validate.py <skill目录>` 检查格式，同时检查相对链接和示例；格式验证不代表任务效果验证。

示例验证方法见 [examples.md](skills/improve-code-quality/references/examples.md)。后续新增有独立触发条件的 skill，避免共用规则重复漂移。

C++ 任务优先选择 `cpp-enginerning`；其他语言或通用质量任务选择 `improve-code-quality`。二者独立携带所需资料，无需同时加载。名称 `cpp-enginerning` 按用户指定拼写保留。

C++ 版参考 2026-10-05 工程原则讨论产出的代码质量 skill 与 C++ 审查清单，保留契约、小步变换和验证诚实原则；未复制旧包中未执行的评测或历史通过记录。

## C++ skill 的研究与评测

[研究结论](docs/research/cpp-enginerning-2026-10-05.md) 记录一手依据、规则取舍和证据边界；[行为评测](evaluation/cpp-enginerning/README.md) 提供独立夹具、复跑命令与结果。评测材料不需要随 skill 安装。
