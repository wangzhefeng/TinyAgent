> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P0：真实任务、基线与迁移准备

状态：**已完成（2026-10-30）**。本文是[个人 Agent 重构总纲](refactor-plan-product.md)的 P0 执行清单；本阶段只准备任务、数据、基线和迁移方案，未删除旧资产，未替换现有 Hermes/OpenClaw。

## 1. P0 交付物

1. 三个可重建任务：定期监测与摘要、工作区任务、引用调研报告。
2. 每个任务的 fixtures、输入、允许操作、预期交付和评分规则。
3. Hermes 主对照的 9 次基线运行（3 任务 × 3 轮）及汇总报告。
4. 旧资产逐文件清单、回滚方案和 `TinyAgent-lab` 归档准备清单。

所有输入必须 sanitized；不得复制真实凭证、私人原文、真实绝对路径或 `~/projects/tsproj_ml` 数据。运行报告写 `results/evals/p0/`，不提交生成物。

## 2. 任务 A：定期监测与摘要

- **输入**：同一公开信息源的三组录制快照：无实质变化、存在有效更新、只有噪声变化；附来源 URL 和采集时间。
- **允许操作**：只读录制数据；输出摘要，不访问真实网络，不执行写/shell。
- **预期交付**：`changes / evidence / summary`；有效更新列出变化及来源，无实质变化返回约定的 `NO_UPDATE`。
- **通过条件**：有效更新无遗漏；每条变化有可解析来源；噪声不产生投递；摘要无快照外事实。
- **记录指标**：检出与误报、引用有效性、token、模型/工具调用数、延迟、人工评分（1–5）。

对应实现阶段为 P4；P0 只准备快照和 Hermes 基线，不提前实现 Scheduler。

## 3. 任务 B：工作区任务

- **输入**：独立小型 Python fixture，预置可复现缺陷、失败测试和一处文档漂移；附允许修改清单与检查命令。
- **允许操作**：list/read/search；P2 才允许在指定文件内 edit 和运行受限检查命令。
- **预期交付**：最小补丁、检查结果、修改摘要和无法完成项（如有）。
- **通过条件**：指定检查全过；只修改允许文件；测试证据可复现；无工作区外访问或写入。
- **记录指标**：任务成功率、检查通过率、越界次数、token、延迟、人工评分（1–5）。

对应实现阶段为 P1/P2；P0 保留一份未修改 fixture 作为每次运行的重置源。

## 4. 任务 C：引用调研报告

- **输入**：本地语料与录制公开网页，包含一个明确版本差异和一处来源分歧；附允许引用的路径/URL 清单。
- **允许操作**：只读检索与摘要；不得写入除报告以外的文件。
- **预期交付**：`claims / evidence / unresolved / summary`，事实 claim 关联路径或 URL，无法确认的内容列入 unresolved。
- **通过条件**：引用 100% 可解析；事实 claim 均有证据或标为不确定；版本差异和来源分歧未被抹平。
- **记录指标**：引用可解析率、证据覆盖率、无依据结论数、token、延迟、人工评分（1–5）。

对应实现阶段为 P3 的调研 Skill，不建立独立 Research 应用。

## 5. 数据与报告布局

```text
evals/
├── personal/
│   ├── routine-monitor/   # tasks.jsonl + 三组快照 + 评分输入
│   ├── workspace-task/    # 原始 fixture + tasks.jsonl + 允许修改清单
│   └── cited-research/    # 语料 + 录制网页 + tasks.jsonl + 引用清单
├── learning/              # P3 记忆与 Skills 用例
└── routine/               # P4 调度与恢复用例
results/evals/p0/          # Hermes 原始输出、运行元数据和汇总，不入库
```

每个 `tasks.jsonl` 至少含：`task_id / input / allowed_actions / expected / scoring / fixture_version`。评分器与模型输出分离，不能只让模型自评通过。

## 6. Hermes 影子基线

1. 对三个任务分别独立运行 3 轮，共 9 次；使用隔离 workspace，不复用生产会话或真实定时任务。
2. 每轮记录任务版本、模型、提示词、开始/结束时间、输出、工具/用量信息（能获取时）和异常。
3. 比较最终交付与操作边界，不比较隐藏推理，不把 Hermes 输出当标准答案。
4. 按任务硬条件评分，再记录人工质量分、token、调用数和延迟；缺失 usage 记 unknown。
5. 汇总成功率和人工评分均值、token/延迟中位数与范围，形成 P0 基线报告。OpenClaw 仅在结果解释存在疑问时补充，不强制增加运行次数。

基线用于后续个人偏好对照，不要求 TinyAgent 在每个质量或性能指标上超过 Hermes；功能、安全和恢复门禁仍必须 100% 通过。

## 7. 迁移与归档准备

- 完成旧应用、评测、课程依赖和 `sys.path` 引用扫描，将文件分为保留语义、替换、后置、删除。
- 已创建私有归档仓库 **`https://github.com/wangzhefeng/TinyAgent-lab`**；首次推送使用 `main` 分支，并记录归档提交号。
- 归档范围仅 `learn/`、课程文档及课程测试；旧 Copilot 和耦合评测直接删除，不混入归档。
- P0 只验证归档清单和迁移脚本/步骤，P5 才执行主仓删除。归档前检查文件数、git 历史、关键入口和链接。
- 回滚演练覆盖：迁移失败、归档缺失、SQLite 导入失败、P5 删除后恢复；不得影响现有 Hermes/OpenClaw。

## 8. P0 完成定义

- [x] 三个任务及 fixtures 可重复重建，输入和评分不依赖真实私有数据。
- [x] Hermes 9 次基线运行及汇总完整，异常和 unknown 有记录。
- [x] 逐文件清单无未评审项，归档范围、实际 URL 和回滚步骤明确。
- [x] 未删除旧资产，未改变现有 Hermes/OpenClaw 的渠道、凭证或定时任务。
- [x] `uv run pytest`、`uv run ruff check .`、`uv run python scripts/check_docs.py` 通过。

全部满足后进入 P1：只实现 CLI 单会话、只读工作区、SQLite 事件和 ContextView，并用任务 B 的只读部分验收。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [迁移清单](product-refactor-migration.md) ｜ [评测规范](../20-evals/application-scenarios.md)
