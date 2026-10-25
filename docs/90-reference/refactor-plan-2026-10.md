> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# TinyAgent 重构方案（2026-10）

状态：**已评审确认（2026-10-25），作为 M0 起执行依据**。M0 已于 2026-10-25 执行完毕（7 个 commit：`git log --oneline` 可溯），验收通过：check_docs 全绿、新代码 ruff 零告警、workspace 成员 `tinyagent` 可导入、`git mv` 全程保留文件历史。

## 0. 已确认决策

| 决策项 | 结论 |
|---|---|
| 载体应用 | Experiment Copilot，默认操作 `~/projects/tsproj_ml` |
| 自研框架 | 教学级 + 可扩展；发行名 `tinyagent-core`，导入名 `tinyagent`；根项目名保持 `tinyagent` |
| L0–L6 目录命名 | `learn/levelN_英文主题` |
| M0 执行方式 | **直接在 `main` 逐 commit 执行**（不用分支）；CI 暂缓，M2 测试就绪后再配 |
| 默认 LLM | 智谱 BigModel **OpenAI 兼容端点** `https://open.bigmodel.cn/api/paas/v4`，默认 `glm-4.7-flash`（**免费档**，高峰可能 429/1305 拥堵）；拥堵或强质量需求切 `glm-5.3-flash`（¥0.8/¥2.8 每百万 token，已实测可用）；**DeepSeek 备用（`deepseek-flash`，按需使用，尽量不用）** |
| 删除项 | `src/dify_dev/`（已确认） |
| **库化（2026-10-25 追加）** | `src/` 提根、仓库即库 `tinyagent-core`（Lab 层同仓不打包）；LICENSE 与 PyPI 发布暂缓——本表 §1/§2/§6 中 workspace/成员包的描述以本行为准 |
| **更名（2026-10-25 追加）** | 发行名 `tinyagent-core` → `tinyagent`，与导入名统一；本文件其余 `tinyagent-core` 字样均为历史时点名称，按本行为准 |

前置已落地：`AGENTS.md`、`scripts/check_docs.py`、`utils/log_util.py`（解除 `.gitignore` 误忽略）、`docs/` 十域骨架、`.env` 规范化 + `.env.example`。

## 1. 目标结构

双主线 + 载体应用：`learn/`（L0–L6 学习路径）、`packages/tinyagent-core`（自研框架）、`apps/experiment_copilot`（实验副驾驶）。目标目录：

```text
TinyAgent/
├── AGENTS.md  README.md(索引化)  pyproject.toml(workspace 根)  uv.lock
├── scripts/            # check_docs.py(已建)、env_setup.sh 等
├── utils/              # log_util.py(已建，解除 .gitignore 忽略)
├── docs/               # 00-overview | 10-scratch | 20-framework | 30-copilot
│   │                   # 40-langgraph | 50-patterns | 60-ecosystem | 70-evals
│   │                   # 80-development | 90-reference | images | archive
├── packages/tinyagent-core/    # 自研框架（uv workspace 成员）
│   └── src/tinyagent/          # api / core / agents / tools / memory / session / tracing / ext
├── learn/
│   ├── level0_llm_basics/     # chat API、流式、结构化输出、链式/路由
│   ├── level1_from_scratch/   # 手写 react / plan_execute / reflection
│   ├── level2_own_framework/  # 用 tinyagent 重写 L1 + 对标源码笔记
│   ├── level3_langgraph/      # agents-from-scratch 邮件助手课程
│   ├── level4_patterns/       # 架构模式实验室
│   ├── level5_ecosystem/      # mcp / adk / frameworks 横评 / deployment
│   └── level6_evals/          # 评测方法与对比实验
├── apps/experiment_copilot/   # 载体应用（doc_qa 起步 → 多 agent 版）
├── evals/                     # 评测数据集与结果
└── tests/                     # unit(框架,mock LLM) + smoke(learn 示例)
```

## 2. 资产迁移映射

| # | 现有 | 去向 | 动作 |
|---|---|---|---|
| 1 | `src/TinyAgent/Agent/` | `learn/level1_from_scratch/react/` | M1 API 化：LLM 层换 OpenAI 兼容客户端（默认智谱 `glm-4.7-flash` 免费档），本地 transformers 降为可选；修 `agent_run.py` 的 `history=_` 误用 |
| 2 | `src/TinyAgent/{prompt_chaining,chat_model,routing}.py` | `learn/level0_llm_basics/` | 迁移；routing 补完实现 |
| 3 | `src/TinyAgent/down_model.py` | `learn/level5_ecosystem/deployment/` | 迁移 |
| 4 | `hello_agents/src/` | `packages/tinyagent-core/src/tinyagent/` | M2 重构迁入（非照搬）：六协议化 + `@tool` 注册 + 补 session/tracing/guardrail |
| 5 | `hello_agents/test/agent_mode/{ReAct,PlanAndSolve,Reflection}` | `learn/level1_from_scratch/{react,plan_execute,reflection}/` | 清理为独立可运行最小示例 |
| 6 | `hello_agents/test/framework/`（langgraph / agentscope / autogen / camel，含各 README） | `learn/level5_ecosystem/frameworks/` | 横评实验，各补对比笔记，README 内容并入域页 |
| 7 | `hello_agents/test/local_server/` | `learn/level5_ecosystem/deployment/` | ollama/vllm 迁移 + 接入说明 |
| 8 | `hello_agents/test/{my_simple_agent,core_llm_test}.py` | `learn/level2_own_framework/` | 迁移 |
| 9 | `hello_agents/.env.example`、`version.py` | 根 `.env.example`（已建）、包内版本 | 合并去重 |
| 10 | `src/mcp_dev/` | `learn/level5_ecosystem/mcp/` | 迁移并升级：真实工具 server + 框架侧 MCP client |
| 11 | `src/adk_dev/` | `learn/level5_ecosystem/adk/` | 迁移 + 补运行说明 |
| 12 | `src/dify_dev/` | — | **删除**（已确认） |
| 13 | `src/qa_chain/` | `apps/experiment_copilot/doc_qa/` | 迁移；修复缺失的 `embedding_api` 依赖 |
| 14 | `agent_usage/` | `packages/tinyagent-core/examples/` | M2 随新 API 改写 |
| 15 | 根 README 知识笔记 | `docs/90-reference/{agent-intro,thinking-frameworks,learning-resources}.md` | 拆分迁入，README 改为索引 |
| 16 | `hello_agents/README.md` | `docs/20-framework/index.md` 现状节 | 内容吸收后删除原文件（消除现存告警之一，见 §3） |
| 17 | `tinyagent.egg-info/` | — | 删除（打包残留，可再生） |
| 18 | `.vscode/`、`requirements.txt`（工作区已删未提交） | — | 提交删除 |

## 3. 现存告警（M0 消除）

`python scripts/check_docs.py` 当前仅余 7 处 `[outside]`（代码目录 README）：`hello_agents/README.md`、`hello_agents/test/framework/framework_camel/README.md`、`framework_langgraph/framework/README.md`、`hello_agents/test/local_server/README.md`、`src/mcp_dev/README.md`、`src/adk_dev/README.md`、`src/dify_dev/README.md`——分别由映射 #16、#6、#7、#10、#11、#12 消除。`src/qa_chain/database/` 为 RAG 语料（数据），checker 已豁免。

## 4. 自研框架要点

- **六协议**：`ChatModel`（仅依赖 OpenAI 兼容协议，默认预设智谱，模型阶梯见 §0）/ `Tool` / `SessionStore` / `Tracer` / `Guardrail` / `Memory`；核心是约 30 行的 `agent_loop`。
- **五扩展点**：`CallCodec`（ReAct 文本 ↔ 原生工具调用）、钩子中间件（retry / 降级 / 审计在此实现，含 429 拥堵时按模型阶梯自动切换）、`Runtime`（loop → 预留 graph）、注册表 + `ext/` 命名空间、版本化公共 API（`tinyagent.api`）。
- **版本演进**：v0.1（M2）loop + 双 codec + 文件 session + JSONL tracer + 单测 → v0.2 guardrail + memory + api 冻结 → v0.3（M4）handoff + MCP 工具源 + 多 agent → v0.4（M5+）graph runtime 预研 + LangChain 适配器。
- 每个抽象配一篇 ADR（`docs/20-framework/adr/`），说明对标框架与简化理由。

## 5. Copilot 阶段

C0（M1）只读工具 `list_configs/read_config/read_metrics/diff_configs`，直接服务手写 Agent 教学版 → C1（M2）自研框架重组 + doc_qa 并入 → C2（M3）HITL 批准与断点续跑 → C3（M4）planner/executor/analyst/reporter 多 agent + 工具 MCP server 化 → C4（M5）真实实验产物评测集 + Survey Agent 毕业项。安全边界见 `AGENTS.md` 第 7 节。

## 6. 工程化

- 根 `pyproject.toml`：项目名**保持 `tinyagent`**、`package = false`、uv workspace；删除 `email_assistant` 打包配置；依赖分组 `dev`（ruff/pytest/pre-commit）与 `course`（langgraph）。
- `packages/tinyagent-core`：独立 `pyproject.toml`（发行名 `tinyagent-core`，导入名 `tinyagent`），extras 按 `mcp`/`vector`/`local` 分层，重依赖不进核心。
- 测试：`tests/unit`（框架，mock LLM，无 key 可跑）+ `tests/smoke`（learn 示例 `--help`/import）。
- CI 暂缓（已确认）；本地门禁 `check_docs` + `ruff`，M2 测试就绪后再配 GitHub Actions；提交规范 `type(scope): summary`。

## 7. 实施阶段

| 阶段 | 内容 | 验收 |
|---|---|---|
| **M0 结构迁移** | **直接在 `main` 逐 commit 执行**；建目录骨架；按映射表 `git mv`（纯移动不改内容）；删除项 12/17/18；README 拆分改索引；repo-map 与域页按新结构重建（域页骨架已先行落位）；pyproject workspace 化 | check_docs 全绿；ruff 新代码零告警；抽样运行每域至少一个入口；逐 commit 可回溯 |
| **M1 L0+L1** | 手写三范式 API 化（智谱 `glm-4.7-flash` 免费档起步）；Copilot C0 只读工具 | 无本地模型可跑通 ReAct/Plan-Execute/Reflection；能答 tsproj_ml 配置/指标问题 |
| **M2 框架 v0.1** | `packages/tinyagent-core` 重构 + 单测 + examples + CI | 独立可安装；单测覆盖 loop/codec/session |

> 进度：M0–M4 已于 2026-10-25 完成（M1 实测免费档 glm-4.7-flash 返回 429/1314 套餐失效，按阶梯切换 glm-5.3-flash 验收；M2 框架 v0.1 单测全绿 + CI；M3 课程三 part + Copilot C1 含 checkpointer/interrupt 验证；M4 框架 v0.3（handoff/Swarm + MCP 工具源）、自建 MCP server 挂载实跑干净退出、六模式实验室全过、Copilot C3 四角色多智能体产出真实口径对比报告）。
| **M3 LangGraph** | 邮件助手课程全程 + Copilot C2 | 课程项目含 HITL/记忆/多 agent 跑通 |
| **M4 模式+生态** | patterns 实验室 + MCP/ADK + Copilot C3 | 框架可挂载自建 MCP server |
| **M5 评测收尾** | evals + 三版本 Copilot 对照 + Survey Agent | 同一评测集出可对比数据；学习地图全勾 |

## 8. 风险与回滚

| 风险 | 缓解 |
|---|---|
| 迁移破坏可运行性 | M0 只移动不改内容；每域抽样运行验证 |
| `sys.path` hack 依赖 cwd 断裂 | 保持"从仓库根运行"约定；M0 不改 import，M1/M2 逐级修复 |
| workspace/依赖兼容 | 合入前 `uv sync` 冒烟 |
| 免费档 429 拥堵影响开发 | 模型阶梯一行切换（§0）；M2 钩子自动化降级 |
| 误删有价值内容 | 仅 `git mv` + 显式删除清单；egg-info 可再生 |
| 框架重构走偏 | 接口先 ADR + 单测骨架评审，后实现 |
| main 直执行中途出错 | 逐 commit 小步提交，出问题按 commit 精确回退（`git revert`） |

## 9. 决策记录

以上决策均于 2026-10-25 由项目负责人确认（载体应用/框架定位/删除 Dify 见前几轮对话；命名/执行方式经选项确认；模型配置经实测确认：`glm-5.3-flash` HTTP 200 可用、`glm-4.7-flash` 免费但高峰 429）。GLM 端点与 Coding Plan 计费条款依据官方文档：[OpenAI API 兼容](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction)、[套餐概览](https://docs.bigmodel.cn/cn/coding-plan/overview.md)、[API 定价](https://docs.bigmodel.cn/cn/guide/start/pricing.md)。后续变更决策时更新本表并注明日期。
