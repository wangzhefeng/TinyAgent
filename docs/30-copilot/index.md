> 所属：[TinyAgent Docs](../README.md) › [载体应用](index.md)

# Experiment Copilot（实验副驾驶）

## 定位

贯穿各学习层级的载体应用：面向时序预测实验仓库的 Agent 助手——给定研究问题，规划实验 → 生成/校验 YAML 配置 → 调用批量入口执行 → 解析指标产物 → 输出对比表与图 → 写 markdown 报告。

**默认操作对象**：`~/projects/tsproj_ml`（canonical YAML 配置、`batch_run.py`、结构化指标产物），已确认。

## 安全边界（强制）

摘要（全文见 [AGENTS.md §7](../../AGENTS.md)）：

1. 起步只读（list / read / diff）；写操作须人工确认（HITL）后启用；
2. subprocess 白名单（仅 `batch_run.py`、`run.py` 等显式入口）；
3. 不读取、不打印、不提交任何密钥与 `.env`；
4. 长任务/高成本任务执行前必须请求批准。

## 阶段规划

| 阶段 | 里程碑 | 能力 |
|---|---|---|
| C0 | M1 | 只读工具：`list_configs` / `read_config` / `read_metrics` / `diff_configs` |
| C1 | M2 | 用自研框架重组工具；`src/qa_chain/` 迁入为 doc_qa 能力 |
| C2 | M3 | HITL 批准 + 长任务断点续跑（LangGraph interrupt） |
| C3 | M4 | planner / executor / analyst / reporter 多智能体 + 工具 MCP server 化 |
| C4 | M5 | 真实实验产物评测集；Survey Agent 毕业项 |

## 现状

- `apps/experiment_copilot/doc_qa/`（M0 自 `src/qa_chain/` 迁入）：RAG 问答（chroma + 智谱 embedding + Streamlit），待修复缺失的 `embedding_api` 依赖。`database/` 为 RAG 语料（数据，不入文档体系）。

## 相关

- [60-ecosystem](../60-ecosystem/index.md)：MCP server 化
- [70-evals](../70-evals/index.md)：C4 评测
