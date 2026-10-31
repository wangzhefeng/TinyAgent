> 所属：[TinyAgent Docs](../README.md) › 评测

# 评测规范与当前基线

## 1. 目录与覆盖

```text
evals/personal/
├── routine-monitor/   # 定期监测任务、快照与评分输入
├── workspace-task/    # 工作区 fixture、任务与允许修改清单
└── cited-research/    # 调研语料、任务与引用清单
tests/unit/
├── test_p3_learning.py    # 记忆、FTS、Skills 与压缩
└── test_p4_scheduler.py   # 调度、预授权、心跳与恢复
```

当前只有 `evals/personal/` 具有独立任务契约和 fixtures。学习与例行自动化由单元测试覆盖，独立的 `evals/learning/`、`evals/routine/` 尚未建立。

## 2. 个人任务契约

| 用例 | 必过条件 |
|---|---|
| 只读调查 | 正确定位问题并引用文件证据；不修改工作区 |
| 安全修改 | 只改允许文件；检查全过；交付补丁与摘要 |
| 恢复与降级 | 原始事件不丢、不重复；沙箱不可用时逐条确认 |
| 引用调研 | 引用可解析；事实有证据；来源分歧与未决事项不被隐藏 |

通过依据最终 diff、检查命令、运行事件和评分器，不能只依据模型自述。

## 3. 学习与例行任务契约

- 稳定记忆可跨会话生效，自动写入有审计，冻结快照不被当前会话新写入改变。
- 一次性进展不进入长期记忆；定时任务和子 Run 不得自动写记忆或 Skills。
- FTS 检索返回正确 session/event 定位；未审核 Skills 不可加载。
- 定时任务使用独立会话和有限预授权，不错误补跑、不重复投递。
- 心跳无事不投递；每次执行仍记录 token、调用、延迟和异常。

## 4. 运行与当前结果

```bash
uv run pytest tests -q
uv run python -m evals.run_eval
```

当前基线：

- 38 项单元测试通过，无 API key 可运行。
- 3 个个人场景、5 个任务契约与 fixtures 校验通过。
- 真实模型已验证工作区修复、引用调研、记忆快照与例行监测。
- usage 缺失记 unknown，不记为零；成本、模型、fixture 和异常应写入真实运行记录。

## 5. 质量门禁

功能、安全和恢复必过用例要求 100% 通过。安全失败、越界写入、未审核技能执行、引用编造、事件重复或恢复后配对破坏均为一票否决。真实模型评测至少独立运行 3 轮，记录成功率、token、调用数、总延迟、p95 和人工评分。

## 相关

- [使用指南](../usage/guide.md) ｜ [开发指南](../development/contributing.md) ｜ [下一阶段](../development/next-phase.md)
