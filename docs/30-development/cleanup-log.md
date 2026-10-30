> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 清理记录

删除/清理动作须留痕：日期、动作、原因。大规模结构迁移见[重构方案](../40-reference/refactor-plan-2026-10.md)。

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-10-25 | 解除 `.gitignore` 对 `utils/` 的忽略，新建 `utils/log_util.py`、`utils/__init__.py` | 修复多处 `from utils.log_util import logger` 的缺失依赖（自 TinyLLM 移植） |
| 2026-10-25 | 计划删除 `src/dify_dev/`（待 M0 执行） | 空壳 TODO；低代码平台与"从零构建"学习目标关联最弱（已确认） |
| 2026-10-25 | 计划删除 `tinyagent.egg-info/`（待 M0 执行） | 失效打包配置的残留，可再生 |
| 2026-10-25 | M0 执行删除：`src/dify_dev/`、`tinyagent.egg-info/`、`requirements.txt`、`.vscode/`、`hello_agents/.env.example`（并入根 `.env.example`） | 结构迁移映射 #9/#12/#17/#18 |
| 2026-10-25 | M0 吸收后删除 6 处代码目录 README：`src/mcp_dev/`、`src/adk_dev/`（空文件）、`hello_agents/`、`framework_camel/`、`local_server/`、`langgraph/framework/` | 内容并入 `docs/60-ecosystem/`（MCP 三页 + 框架要点）与 `docs/10-framework/`；消除 check_docs 全部现存告警 |
| 2026-10-25 | **`hello_agents/` 整体移除**（28 文件约 3800 行；其 `test/` 已于 M0 迁出） | 能力已并入 tinyagent v0.3.1（ADR-0007：memory 空壳兑现 + Reflection/PlanAndSolve 两组件；多 provider LLM、四类 agent 变体、工具注册确认已被覆盖）；最后 6 个消费者全部改写为 tinyagent/L0 实现并实跑验证 |
| 2026-10-25 | **库化重构**：`packages/` 目录移除（`git mv` 保历史：src/ 与 examples/ 提根，成员 pyproject 并入根） | 仓库转型为单包库项目（`tinyagent-core`），Lab 层（learn/apps/evals）同仓保留不打包；wheel 验证零泄漏 |
| 2026-10-25 | 发行名更名：`tinyagent-core` → `tinyagent`（pyproject、uv.lock 与全部现行文档同步；历史记录保留当时名称） | 发行名与导入名统一，消除双名认知成本 |
| 2026-10-25 | 删除 `scripts/env_setup.sh`、`scripts/rm_dsstore.sh`、`scripts/update_codes.sh`（`git rm`） | 重构前个人脚本：env_setup 语法/依赖已失效且与现行文档冲突；rm_dsstore 一次性清理已被仓库 `.gitignore` 的 `.DS_Store` 规则覆盖；update_codes 违反提交规范（`git add .` + "update"）且含 utils 旧独立仓库残留 |
| 2026-10-25 | 评测集迁移：`evals/dataset.jsonl` → `evals/datasets/{facts,caliber}.jsonl`（改为真 JSONL + `scenario` 字段，`run_eval.py` 改为 glob 加载） | 按场景分类（取数事实 / 口径判断）为评测扩容铺路；明确入库评测资产与不入库的 `dataset/` 产物目录用途区分 |
| 2026-10-30 | P5 删除 `apps/experiment_copilot/`（37 文件）及旧 `facts/caliber` 评测集 | 已确认旧外部项目不再使用、不迁移、不作基线；个人 Agent 改用独立 fixtures |
| 2026-10-30 | `learn/`（84 文件）、`apps/survey_agent/`（3 文件）及课程文档迁移至私有 `TinyAgent-lab` | 主仓转为个人 Agent 应用；归档仓库保留可运行历史，主仓移除教学与旧框架依赖 |
| 2026-10-30 | 删除 `docs/30-copilot/`、课程域文档与 `learning-path.md` 等旧定位页面 | 文档主线改为个人 Agent 的使用、架构、评测与运维；归档内容已先在 `TinyAgent-lab` 验证 |
| 2026-10-31 | 清除 pytest/ruff 缓存、Python 字节码、`apps`/`learn` 残留目录及 `results/archive` 本地克隆；`docs/images/` 移至 `TinyAgent-lab`（提交 `aaf6688`） | 仅清理生成物与未引用资源；`results/evals/` 完整保留，旧源码、日志和 `.env` 未改动 |
| 2026-10-31 | 文档目录重排：`20-framework` → `10-framework`、`70-evals` → `20-evals`、`80-development` → `30-development`、`90-reference` → `40-reference` | 统一为连续 00/10/20/30/40 层级；同步更新全部文档、README、代码注释与链接，check_docs 通过 |
| 2026-10-31 | 删除 `examples/`、旧 Agent/codec/loop/memory/session/tracer 实现及对应测试；归档至私有 `TinyAgent-lab/legacy-v0/`（提交 `be9f781`），公共 API 升级为 v1.0 | 主仓只维护个人 Agent 产品能力，不保留旧通用框架兼容门面；稳定导出收敛为上下文、模型/工具与 Personal Runtime |
| 2026-10-31 | 清除旧框架 `logs/`、`results/archive/` 本地克隆、缓存与空目录；删除无引用的 `utils/` | 归档已推送私有仓库；当前代码不再使用旧日志器；保留 `.env`、`.venv` 和完整 `results/evals/` |
