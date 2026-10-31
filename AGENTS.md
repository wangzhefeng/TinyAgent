# AGENTS.md

本文件是 TinyAgent 的**强制协作规则**，适用于人类与 AI Agent。目标：代码可维护、文档与实现一致、个人 Agent 安全可用。

## 1. 项目定位

TinyAgent 是 **Python 自托管、单用户、可持续进化的个人 Agent**：通过 CLI 接受任务，安全操作工作区，记住偏好、检索经验、沉淀 Skills，并定时主动完成任务。

- 应用优先，不以通用 Agent 框架或教学项目为目标。
- 当前只提供本地 CLI；新渠道和服务接口必须经过评审。

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
| `evals/` | personal 任务契约与 fixtures |
| `tests/` | 单元测试 |
| `docs/usage/` | 当前安装、配置与使用 |
| `docs/architecture/` | 当前架构、公共 API 与设计决策 |
| `docs/evaluation/` | 当前评测契约与验证结果 |
| `docs/development/` | 开发规则、独立教学快照与下一阶段 |

## 3. 文档系统（强制）

1. **唯一文档中心**：项目级文档全部放在 `docs/`。例外仅为根目录 `README.md` 与本文件。
2. **四个文档域**：使用、架构、评测、开发；不得新增职责重复的历史/参考目录。
3. **只写当前事实**：已删除的功能、旧项目过程和迁移记录不保留在现行文档中。
4. **渐进式披露**：根 README 只做项目入口；`docs/README.md` 说明目录职责；正文单页单主题，尽量不超过 150 行。
5. 页面顶部写所属导航，使用相对链接；代码目录不放长 README，评测 fixture 使用 `.txt` 等非文档后缀。

## 4. 修改功能时必须更新文档

| 变更 | 必须更新 |
|---|---|
| 安装、命令、参数、workspace/state、产物 | [使用指南](docs/usage/guide.md)、根 README（如受影响） |
| 目录、模块、公共 API、能力边界 | [架构概览](docs/architecture/overview.md) |
| 重要设计取舍与工具安全边界 | [设计决策](docs/architecture/decisions.md) |
| fixtures、任务契约、评分与验证结果 | [评测规范](docs/evaluation/scenarios.md) |
| 编码、测试或文档规则 | [开发指南](docs/development/contributing.md) |
| 后续方向与待决策事项 | [下一阶段](docs/development/next-phase.md) |

**完成标准**：代码可运行 + 相关文档已更新 + 链接可跳转 + 必要时更新索引。删除内容时直接清理现行引用，不另写历史迁移记录。

## 5. 编码风格（强制要点）

完整规范见[开发指南](docs/development/contributing.md)。要点：

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
- [ ] 目录、命令、参数或依赖变化是否更新对应现行文档？
- [ ] 新文档是否归入四个文档域并加入 `docs/README.md`？
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

`check_docs.py` 检查超长文档、失效相对链接和 `docs/` 外的 markdown（根 README / AGENTS 除外）。

## 9. 文档事实来源

- 使用与配置：`docs/usage/guide.md`
- 架构与设计决策：`docs/architecture/`
- 评测：`docs/evaluation/scenarios.md`
- 工程规范：`docs/development/contributing.md`
- 后续规划：`docs/development/next-phase.md`

若文档与代码冲突，以**代码 + 测试**为准，并立即修正文档；不要保留“过期但看起来正确”的描述。

## 10. 术语与禁止事项

tool calling 统一译“工具调用”；HITL 为“人工介入”；checkpoint 为“检查点”；guardrail 为“护栏”；handoff 为“移交”。

- 禁止在代码目录新增长 README；
- 禁止复制整段文档到多个页面；
- 禁止只改代码不改文档；
- 禁止删除文档页面而不更新索引/链接；
- 禁止把数据、权重、日志、密钥提交进 git（见 `.gitignore`）；
- 禁止绕过工作区、审批、预授权或 Skills 审核边界。
