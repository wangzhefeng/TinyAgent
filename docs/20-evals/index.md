> 所属：[TinyAgent Docs](../README.md) › [评测与观测](index.md)

# 评测与观测

## 定位

让个人 Agent 的任务完成度、安全边界、学习效果和运行成本都可验证。评测使用独立 fixtures、录制数据或 sanitized 日常任务，不依赖旧外部项目。

## 场景

- `evals/personal/`：定期监测、工作区任务、引用调研。
- `evals/learning/`：稳定记忆、历史检索、Skills 审核与压缩。
- `evals/routine/`：定时任务、有限预授权、心跳与恢复。

任务定义、输入、允许操作、预期交付和评分规则见[应用与评测规范](application-scenarios.md)。`uv run python -m evals.run_eval` 校验任务契约与 fixtures。

## 当前验证

| 阶段 | 结果 |
|---|---|
| P0 | 三个任务与 fixtures 完成；Hermes 基线 9/9 成功 |
| P1 | 14 个离线用例；真实只读缺陷调查成功 |
| P2 | 9 个安全用例；真实精确编辑后沙箱内 4/4 测试通过 |
| P3 | 8 个学习用例；冻结记忆与审核技能在真实场景生效 |
| P4 | 5 个调度用例；真实心跳投递/静默与重复防护通过 |
| P5 | 三个任务各 3 轮全部验收；归档提交 `4ff9255`；69 项测试、Ruff、文档与任务契约全绿 |

项目共 **69 项测试通过**，Ruff 和文档检查全绿。真实 usage 记录 input/output/total tokens、API/工具调用和延迟；成本缺失记 unknown，不记为零。

## 相关

- [application-scenarios](application-scenarios.md)
- [P0](../40-reference/p0-execution.md) ｜ [P1](../40-reference/p1-execution.md) ｜ [P2](../40-reference/p2-execution.md) ｜ [P3](../40-reference/p3-execution.md) ｜ [P4](../40-reference/p4-execution.md)
- [outputs 产物约定](../30-development/outputs.md)
