> 所属：[TinyAgent Docs](../README.md) › 开发

# 开发指南

## 1. 环境与门禁

```bash
uv sync --all-extras
uv run pytest tests -q
uv run ruff check .
uv run python scripts/check_docs.py
uv run python -m evals.run_eval
```

脚本从仓库根目录运行。核心依赖放入 `[project].dependencies`，MCP/SOCKS 放入 extras，开发依赖放入 `dependency-groups.dev`；新增依赖必须说明理由。

## 2. 编码规则

- import 按标准库、第三方、本地分组并排序。
- 新模块使用模块 docstring；公开函数和类使用 Google 风格 docstring 与类型注解。
- 禁止 print 调试入库；CLI 用户输出只放在 `main()` 或渠道层。
- 不新增 `sys.path` hack；使用包导入或 workspace 安装。
- 注释解释“为什么”，行为变化后同步更新注释和 docstring。
- 提交信息使用 `type(scope): summary`，类型包括 feat、docs、refactor、fix、chore、test；正文说明如何验证与如何回滚。

## 3. 测试

`tests/unit/` 当前有 64 个用例，mock LLM、无 API key 可运行，覆盖 Agent 循环、工具、存储、审批、记忆、调度、计划模式、MCP 接线与子 Agent。

- 单测命名为 `test_<module>.py`，共享夹具放 `tests/conftest.py`。
- 公共 API 或行为变化必须先改/补测试。
- 每个修复的 Bug 保留一个回归用例（单测或 `evals/` 场景），换模型或发布前重跑。
- 每个测试使用独立 workspace/state，不读取真实凭证或现有私人项目。
- 应用级任务契约放 `evals/`，规则见[评测规范](../evaluation/scenarios.md)。
- `docs/development/tutorials/` 保存原样迁移的独立教学快照，不参与 Ruff 检查和默认 pytest 收集；按教程索引中的显式路径单独测试，不作为产品代码风格示例。

## 4. 文档职责与联动

| 变更 | 必须更新 |
|---|---|
| 安装、命令、参数、workspace/state、产物 | [使用指南](../usage/guide.md) 与根 README |
| 目录、模块、公共 API、能力边界 | [架构概览](../architecture/overview.md) |
| 重要设计取舍 | [设计决策](../architecture/decisions.md) 中对应主题 |
| fixtures、任务契约、评分与验证结果 | [评测规范](../evaluation/scenarios.md) |
| 编码、测试或文档规则 | 本文 |
| 后续方向与待决策事项 | [下一阶段](next-phase.md) |

文档只描述当前事实。每页尽量不超过 150 行，顶部提供所属导航；链接和篇幅由 `scripts/check_docs.py` 检查。

## 5. 术语

- tool calling / function calling：工具调用。
- HITL：人工介入。
- checkpoint：检查点。
- guardrail：护栏。
- handoff：移交。
- session / memory / eval：会话 / 记忆 / 评测。

## 相关

- [架构概览](../architecture/overview.md) ｜ [评测规范](../evaluation/scenarios.md)
