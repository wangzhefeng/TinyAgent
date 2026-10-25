> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# 项目收官总结（2026-10-25）

> M0–M5 全部完成。学习地图全勾：[learning-path](../00-overview/learning-path.md)。

## 交付总览

| 交付物 | 位置 | 状态 |
|---|---|---|
| 自研框架 tinyagent（v0.3） | `packages/tinyagent-core/`（六协议 + 双 codec + Swarm/handoff + MCP 工具源，24 单测，6 篇 ADR） | ✅ |
| 学习路径 L0–L6 | `learn/`（手写三范式 → 框架对照 → LangGraph 课程三 part → 六模式实验室 → MCP/ADK/部署） | ✅ |
| Experiment Copilot | `apps/experiment_copilot/`（C0 手写版 → C1 框架版 → C3 四角色多智能体；doc_qa RAG） | ✅ |
| Survey Agent（毕业项目） | `apps/survey_agent/`（调研→评测→结论工作流自动化） | ✅ |
| 评测体系 | `evals/`（三版本同集对照，报告落 `results/evals/`） | ✅ |
| 工程与文档体系 | uv workspace、CI 三门禁、十域文档、check_docs | ✅ |

## 量化结果（实测）

- **三版本 Copilot 对照**（15/15 零失败）：C0 手写版命中率 77%/58s，C1 框架版 50%/43s（单题最快 11.5s 满分），C3 多智能体 43%/214s——**取数事实题简单循环占优，综合分析多智能体占优**，详见 [70-evals](../70-evals/index.md)。
- **MCP 验收**：框架经 stdio 挂载自建 `tsproj-ml-readonly` server，6 轮工具调用全走 MCP，干净退出。
- **Survey Agent**：五段工作流 200 秒跑通，评测阶段由 agent 自主设计（horizon 与季节周期对齐、诊断梯度）并真实执行。
- **反幻觉抽查**：C1/C3 在口径问题上均给出「不可直接比较」的严谨结论；C3 曾拒用无关场景证据。
- **成本**：全程智谱 `glm-5.3-flash`（免费档实测 429/1314 失效后按阶梯切换），M1–M5 累计成本个位数元。

## 方法论沉淀（M1–M5 的真教训 → 框架设计）

1. 教程代码的 Action 解析少切冒号 → codec 回归测试（M1）；
2. 文本协议服从性差 → 双 codec：教学用 ReAct 文本、生产用原生 function calling（M1/M3）；
3. 模型自编 Observation → 反幻觉四规则 + 错误如实回填（M1/M4 泛化为任意异常）；
4. 思考型模型超时/拥堵 → provider 预设 + 重试阶梯 + 会话可恢复（M2/M3）；
5. anyio cancel scope 跨任务限制 → MCP 桥接的单一服务协程模式（M4）。

## 后续方向（超出本方案范围）

- v0.4 Graph Runtime（[ADR-0006 提案](../20-framework/adr/0006-graph-runtime-proposal.md)）；
- Copilot C2（interrupt 审批内置化）与写操作（HITL 后）；
- `hello_agents/` 复刻版剩余能力（memory/plan_solve 等六种 agent）并入框架后移除；
- 评测扩容（模式间量化对比、LangSmith 后端对照）。

## 相关

- [重构方案与决策记录](refactor-plan-2026-10.md) ｜ [学习地图](../00-overview/learning-path.md)
