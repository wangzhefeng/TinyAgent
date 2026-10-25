> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 清理记录

删除/清理动作须留痕：日期、动作、原因。大规模结构迁移见[重构方案](../90-reference/refactor-plan-2026-10.md)。

| 日期 | 动作 | 原因 |
|---|---|---|
| 2026-10-25 | 解除 `.gitignore` 对 `utils/` 的忽略，新建 `utils/log_util.py`、`utils/__init__.py` | 修复多处 `from utils.log_util import logger` 的缺失依赖（自 TinyLLM 移植） |
| 2026-10-25 | 计划删除 `src/dify_dev/`（待 M0 执行） | 空壳 TODO；低代码平台与"从零构建"学习目标关联最弱（已确认） |
| 2026-10-25 | 计划删除 `tinyagent.egg-info/`（待 M0 执行） | 失效打包配置的残留，可再生 |
| 2026-10-25 | M0 执行删除：`src/dify_dev/`、`tinyagent.egg-info/`、`requirements.txt`、`.vscode/`、`hello_agents/.env.example`（并入根 `.env.example`） | 结构迁移映射 #9/#12/#17/#18 |
| 2026-10-25 | M0 吸收后删除 6 处代码目录 README：`src/mcp_dev/`、`src/adk_dev/`（空文件）、`hello_agents/`、`framework_camel/`、`local_server/`、`langgraph/framework/` | 内容并入 `docs/60-ecosystem/`（MCP 三页 + 框架要点）与 `docs/20-framework/`；消除 check_docs 全部现存告警 |
