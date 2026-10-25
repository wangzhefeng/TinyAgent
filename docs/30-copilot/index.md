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

| 阶段 | 里程碑 | 能力 | 状态 |
|---|---|---|---|
| C0 | M1 | 只读工具：`list_configs` / `read_config` / `list_results` / `read_result_summary` | **已完成（2026-10-25）** |
| C1 | M2/M3 | 用自研框架重组工具；`doc_qa/` 修复依赖并入应用 | **已完成（2026-10-25）** |
| C2 | M3 | HITL 批准 + 长任务断点续跑（LangGraph interrupt） | 部分：interrupt 课程验证 ✅，Copilot 内置待 M5 |
| C3 | M4 | planner / executor / analyst / reporter 多智能体 + 工具 MCP server 化 | **已完成（2026-10-25）**：server 化 ✅、四角色编排 ✅ |
| C4 | M5 | 真实实验产物评测集；Survey Agent 毕业项 | 规划 |

## C0 使用（已完成）

```bash
# 工具自检（无 LLM）：列出配置/结果并汇总指标
python -m apps.experiment_copilot.copilot0.tools

# ReAct Agent + 只读工具，回答 tsproj_ml 配置与指标问题
python -m apps.experiment_copilot.copilot0.run_react
```

- 工具集：`apps/experiment_copilot/copilot0/tools.py`；目标仓库可用环境变量 `TPROJ_ML_ROOT` 覆盖（默认 `~/projects/tsproj_ml`）。
- 指标来源：各 result identity 下的 `test_scores_df.csv`（MAE/RMSE/Bias/MAPE/Accuracy + Naive 基线），按 `scope=aggregate` 求均值。
- 安全实现：路径 resolve 后强制落在 `config/`、`results/` 内（防穿越）；单次返回 6000 字符截断；无任何写/执行操作。

## C1 框架版（已完成）

```bash
python -m apps.experiment_copilot.copilot1.run_framework
```

- `copilot1/`：同一组只读工具以 `@tool` 声明（类型注解自动生成 Schema），经 `TinyAgent`（react codec）+ `AllowlistGuardrail` 白名单 + 会话/追踪运行——安全边界的框架化落地。
- `doc_qa/`：修复原教程缺失的 `embedding_api` 模块（`ZhipuAIEmbeddings` 走智谱 OpenAI 兼容端点 Embedding-3；M3E 留提示性占位）。运行 streamlit 界面另需 `uv pip install streamlit chromadb`（按需安装，未入默认依赖）。

## 现状

- `apps/experiment_copilot/doc_qa/`（M0 自 `src/qa_chain/` 迁入）：RAG 问答（chroma + 智谱 embedding + Streamlit），待修复缺失的 `embedding_api` 依赖。`database/` 为 RAG 语料（数据，不入文档体系）。

## 相关

- [60-ecosystem](../60-ecosystem/index.md)：MCP server 化
- [70-evals](../70-evals/index.md)：C4 评测
