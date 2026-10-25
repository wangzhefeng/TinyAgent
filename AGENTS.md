# AGENTS.md

本文件是 TinyAgent 的**强制协作规则**，适用于人类与 AI Agent。
目标：代码可维护，文档不腐化，学习路径清晰。

## 1. 项目定位与主线

TinyAgent 是 AI Agent 学习与实验仓库，双主线 + 一个载体应用：

| 主线 | 位置 | 说明 |
|---|---|---|
| 学习路径 | `learn/`（L0–L2、L5 已迁入；L3/L4/L6 随里程碑填充） | 从零手写 → 框架 → 模式 → 生态 → 评测 |
| 自研框架 | `packages/tinyagent-core/`（发行名 `tinyagent-core`，导入名 `tinyagent`；hello_agents 能力已于 v0.3.1 并入后移除该目录） | 教学级、可扩展的 Agent 框架 |
| 载体应用 | `apps/experiment_copilot/`（doc_qa 已迁入） | 实验副驾驶，默认操作 `~/projects/tsproj_ml` |

学习地图与里程碑见 [learning-path](docs/00-overview/learning-path.md)。

## 2. 文档系统（强制）

1. **唯一文档中心**：项目级文档全部放在 `docs/`。
   - 允许的例外：根目录 `README.md`（总索引）与本文件。
   - 代码目录（`learn/`、`packages/`、`apps/`）**不放长 README**。
2. **根 README 只做索引**：项目定位、快速索引、快速开始、目录概览、文档入口。
3. **渐进式披露**：
   - 入口页（`docs/README.md`、各域 `index.md`）只放概要与目录；
   - 正文页尽量 **≤ 150 行**，超过就拆页；
   - 页面之间用相对链接连接，不复制内容。
4. **单页单主题**：一个页面只解释一个主题；相关背景用链接。
5. **导航头**：正文页顶部写
   ```markdown
   > 所属：[TinyAgent Docs](../README.md) › [域](index.md)
   ```
6. **命名**：小写、短横线；入口统一 `index.md`；历史/迁移材料放 `docs/90-reference/`；二进制放 `docs/archive/` 或 `docs/images/`。

## 3. 修改功能时必须更新文档

| 变更 | 必须更新 |
|---|---|
| 新增/删除/移动功能或示例 | 对应域页面、域 `index.md`、[repo-map](docs/00-overview/repo-map.md) |
| 改命令/参数/依赖 | 对应操作页、根 README 快速开始（如受影响）、[environment](docs/00-overview/environment.md) |
| 改目录结构 | 根 README 目录概览、[architecture](docs/00-overview/architecture.md)、repo-map |
| 改测试 | [testing](docs/80-development/testing.md) |
| 改框架公共 API | [framework](docs/20-framework/index.md) 及相关页 |
| 改 Copilot 工具或安全边界 | [copilot](docs/30-copilot/index.md) |
| 删除内容 | [cleanup-log](docs/80-development/cleanup-log.md) |
| 新增外部参考 | [learning-resources](docs/90-reference/learning-resources.md) |

**完成标准**：代码可运行 + 相关文档已更新 + 链接可跳转 + 必要时更新索引。

## 4. 编码风格（强制要点）

完整规范见 [coding-style](docs/80-development/coding-style.md)。要点：

- 保留既有文件头横幅与分节注释；import 三段式（标准库 / 第三方 / 本地）；
- 日志统一 `from utils.log_util import logger`，禁止 print 调试代码入库；
- 公开函数写 Google 风格 docstring（首行英文一句话，中文正文）；
- 脚本从仓库根目录运行；新代码禁止新增 `sys.path` hack（迁移期旧代码保留）；
- 提交前 `uv run ruff check .`：新代码必须通过，迁移期旧代码告警可豁免。

## 5. 提交/评审清单

- [ ] 代码可从仓库根目录运行？
- [ ] 是否新增/移动/删除了代码目录？→ 更新 repo-map 与 architecture。
- [ ] 是否改了命令或参数？→ 更新对应域页面。
- [ ] 是否新增了文档？→ 加入域 `index.md` 与 `docs/README.md`。
- [ ] 是否有超过 150 行的文档？→ 拆分。
- [ ] 代码目录是否新增 README/长 markdown？→ 移到 `docs/`。
- [ ] 相对链接是否有效？→ `python scripts/check_docs.py`。
- [ ] 是否引入新第三方依赖？→ 说明理由；重依赖进 extras。
- [ ] 提交信息：`type(scope): summary`（feat / docs / refactor / fix / chore / test）。

## 6. 定期巡检

```bash
python scripts/check_docs.py
uv run ruff check .
uv run pytest            # 测试体系建立后
```

`check_docs.py` 会报告：超过 150 行的文档、指向不存在文件的相对链接、`docs/` 外的 markdown（根 README / AGENTS 除外）。

## 7. Experiment Copilot 安全边界（强制）

Copilot 及一切示例代码若操作外部真实仓库，必须遵守：

1. 默认操作对象仅 `~/projects/tsproj_ml`；
2. 起步阶段只读（list / read / diff）；写操作（生成/修改 YAML、写报告）必须经人工确认（HITL）后启用；
3. subprocess 白名单（仅 `batch_run.py`、`run.py` 等显式入口），禁止任意 shell；
4. 不读取、不打印、不提交任何密钥与 `.env`；
5. 长任务/高成本任务执行前必须请求人工批准。

## 8. 文档事实来源

- 目录/职责：`docs/00-overview/architecture.md`
- 代码映射：`docs/00-overview/repo-map.md`
- 学习路径：`docs/00-overview/learning-path.md`
- 域入口：`docs/10-*` ~ `docs/70-*`
- 工程规范：`docs/80-development/`
- 参考资料/迁移：`docs/90-reference/`

若文档与代码冲突，以**代码 + 测试**为准，并立即修正文档；不要保留"过期但看起来正确"的描述。

## 9. 术语

见 [terminology](docs/00-overview/terminology.md)。要点：tool calling 统一译"工具调用"；HITL 为"人工介入"；checkpoint 为"检查点"；guardrail 为"护栏"；handoff 为"移交"。

## 10. 禁止事项

- 禁止在代码目录新增长 README；
- 禁止复制整段文档到多个页面；
- 禁止只改代码不改文档；
- 禁止删除文档页面而不更新索引/链接；
- 禁止把数据、权重、日志、密钥提交进 git（见 `.gitignore`）；
- 禁止绕过 Copilot 安全边界对外部仓库执行写操作。
