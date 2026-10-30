# AGENTS.md

本文件是 TinyAgent 的**强制协作规则**，适用于人类与 AI Agent。目标：代码可维护、文档不腐化、个人 Agent 安全可用。

## 1. 项目定位

TinyAgent 是 **Python 自托管、单用户、可持续进化的个人 Agent**：通过 CLI 接受任务，安全操作工作区，记住偏好、检索经验、沉淀 Skills，并定时主动完成任务。

- 应用优先，不以通用 Agent 框架或教学项目为目标。
- 参考 Hermes 的个人学习循环、Pi 的小内核与可选 Runtime，以及手写教程的代码级安全边界。
- 旧学习与示例资产归档在私有 `TinyAgent-lab` 仓库；旧 Experiment Copilot 不再使用。

## 2. 目录职责

| 位置 | 职责 |
|---|---|
| `src/tinyagent/agent/` | Run/Event 与 ContextView |
| `src/tinyagent/runtime/` | SQLite、执行、恢复、审批与 Scheduler |
| `src/tinyagent/tools/` | 工作区、学习和调度工具 |
| `src/tinyagent/execution/` | 本地与沙箱执行后端 |
| `src/tinyagent/memory/` | USER/MEMORY 与冻结快照 |
| `src/tinyagent/skills/` | Skills 草稿与人工审核 |
| `src/tinyagent/channels/`、`cli.py` | CLI 入口 |
| `evals/` | 个人任务、学习循环和例行自动化评测 |
| `tests/` | 单元测试 |
| `docs/` | 唯一文档中心 |

目录与文档映射见 [architecture](docs/00-overview/architecture.md) 和 [repo-map](docs/00-overview/repo-map.md)。

## 3. 文档系统（强制）

1. **唯一文档中心**：项目级文档全部放在 `docs/`。例外仅为根目录 `README.md` 与本文件。
2. **根 README 只做索引**：项目定位、快速开始、能力、目录概览和文档入口。
3. **渐进式披露**：入口页只放概要与目录；正文页尽量 **≤ 150 行**，超过就拆页；页面之间使用相对链接，不复制内容。
4. **单页单主题**：正文页顶部写所属导航；命名使用小写短横线，入口统一 `index.md`；历史/迁移材料放 `docs/40-reference/`。
5. 代码目录**不放长 README**；评测 fixture 中的数据文件使用 `.txt` 等非文档后缀。

## 4. 修改功能时必须更新文档

| 变更 | 必须更新 |
|---|---|
| 新增/删除/移动功能或示例 | 对应域页面、域 `index.md`、[repo-map](docs/00-overview/repo-map.md) |
| 改命令/参数/依赖 | 对应操作页、根 README 快速开始（如受影响）、[environment](docs/00-overview/environment.md) |
| 改目录结构 | 根 README 目录概览、[architecture](docs/00-overview/architecture.md)、repo-map |
| 改测试 | [testing](docs/30-development/testing.md) |
| 改公共 API | [framework](docs/10-framework/index.md) 及相关 ADR |
| 改工具或安全边界 | [ADR-0011](docs/10-framework/adr/0011-approval-execution.md) |
| 删除内容 | [cleanup-log](docs/30-development/cleanup-log.md) |

**完成标准**：代码可运行 + 相关文档已更新 + 链接可跳转 + 必要时更新索引。

## 5. 编码风格（强制要点）

完整规范见 [coding-style](docs/30-development/coding-style.md)。要点：

- import 三段式（标准库 / 第三方 / 本地），段内字母序；
- 禁止 print 调试代码入库；CLI 用户输出除外；
- 公开函数写 Google 风格 docstring（首行英文一句话，中文正文）；
- 脚本从仓库根目录运行；新代码禁止新增 `sys.path` hack；
- 提交前 `uv run ruff check .`：新代码必须通过。

## 6. 安全边界（强制）

1. 默认只读；只有显式 `--writable` 才开放写入和 shell，`--yes` 仅用于可审查的隔离环境。
2. 不默认读取任何现有真实项目；每个应用和评测使用独立 workspace、state 和权限配置。
3. shell 采用命令白名单、固定工作目录、超时和输出上限；禁止任意 shell。
4. 沙箱优先；不可用时，写入/shell 每次单独展示真实参数并人工确认，无人值守直接拒绝。
5. 定时任务使用全新隔离会话和有限预授权，不能创建任务、自动写记忆或修改 Skills；shell 不允许预授权。
6. 记忆自动写入仅限主会话稳定事实并保留审计；Skills 必须经人工审核后才可使用。
7. 不读取、不打印、不提交任何密钥、`.env`、凭证或私人原文；数据库和记忆文件位于 Agent 工作区之外。
8. 长任务/高成本任务执行前必须请求人工批准；真实模型验收记录 usage，缺失成本记 unknown，不记为零。

## 7. 提交/评审清单

- [ ] 代码可从仓库根目录运行？
- [ ] 新增/移动/删除目录时，是否更新 repo-map 与 architecture？
- [ ] 命令、参数或依赖变化时，是否更新对应操作页和环境文档？
- [ ] 新文档是否加入域 `index.md` 与 `docs/README.md`？
- [ ] 是否有超过 150 行的文档需要拆分？
- [ ] 相对链接是否有效？→ `uv run python scripts/check_docs.py`。
- [ ] 新依赖是否说明理由，重依赖是否进入 extras？
- [ ] 提交信息：`type(scope): summary`（feat / docs / refactor / fix / chore / test）。

## 8. 定期巡检

```bash
uv run python scripts/check_docs.py
uv run ruff check .
uv run pytest tests -q
uv run python -m evals.run_eval
```

`check_docs.py` 会报告超长文档、失效相对链接和 `docs/` 外的 markdown（根 README / AGENTS 除外）。

## 9. 文档事实来源

- 目录/职责：`docs/00-overview/architecture.md`
- 代码映射：`docs/00-overview/repo-map.md`
- 框架与 ADR：`docs/10-framework/`
- 评测：`docs/20-evals/`
- 工程规范：`docs/30-development/`
- 重构与迁移：`docs/40-reference/`

若文档与代码冲突，以**代码 + 测试**为准，并立即修正文档；不要保留“过期但看起来正确”的描述。

## 10. 术语与禁止事项

术语见 [terminology](docs/00-overview/terminology.md)：tool calling 统一译“工具调用”；HITL 为“人工介入”；checkpoint 为“检查点”；guardrail 为“护栏”；handoff 为“移交”。

- 禁止在代码目录新增长 README；
- 禁止复制整段文档到多个页面；
- 禁止只改代码不改文档；
- 禁止删除文档页面而不更新索引/链接；
- 禁止把数据、权重、日志、密钥提交进 git（见 `.gitignore`）；
- 禁止绕过工作区、审批、预授权或 Skills 审核边界。
