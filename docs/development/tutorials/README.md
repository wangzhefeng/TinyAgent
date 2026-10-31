> 所属：[TinyAgent Docs](../../README.md) › 开发

# Agent 开发学习教程

本目录保存独立的教学实现，不属于 TinyAgent 产品代码，也不代表 TinyAgent 当前架构。

## Nami Agent：第 11 课

- 来源：`nami-agent` 项目的根 README 与 `lesson-11` 完整代码。
- 入口：[课程说明与完整系列索引](nami-agent/README.md)。
- 内容：长期记忆、会话检索，以及前序课程累积的完整 Agent 实现和测试。
- 迁移方式：源码、测试和 README 内容保持原样，仅取消目标位置的 `lesson-11` 目录层级。

原 README 中的 `cd lesson-11` 对应进入本项目的 `docs/development/tutorials/nami-agent/`。

从仓库根目录运行本课测试：

```bash
uv run pytest docs/development/tutorials/nami-agent/tests -q
```

测试使用模拟模型，不需要真实 API key。教程快照不参与主项目的 Ruff 检查和默认 pytest 收集，也不应作为 TinyAgent 编码风格示例。
