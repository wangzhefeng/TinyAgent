> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 数据与产物目录约定

仓库根下四个**运行时目录**：只在本机存在，一律被 `.gitignore` 忽略、不提交、不进文档检查范围（`scripts/check_docs.py` 已豁免）。

| 目录 | 用途 | 写入方 |
|---|---|---|
| `dataset/` | 实验数据、RAG 语料等输入数据 | 手动放置；脚本按需只读 |
| `downloaded_models/` | 下载的离线模型权重（如 InternLM2，供 `learn/level1_from_scratch/react/llm_local.py` 使用） | `down_model.py` 等下载脚本 |
| `results/` | 模型 / Agent 运行产物：实验输出、评测结果（M5 起 `evals/` 的产出落此处） | 各示例与应用 |
| `logs/` | 运行日志：`utils/log_util`（`logs/<LOG_NAME>/`）与框架 `logs/tinyagent/`（sessions / traces） | 框架与日志器自动 |

## 规则

1. **不入库**：四个目录整体 gitignore；体积大的中间产物绝不提交（`AGENTS.md` 禁止事项）。
2. **按需创建**：脚本写入前 `mkdir(parents=True, exist_ok=True)` 自建，不依赖目录预先存在。
3. **路径自解释**：产物建议按 `results/<实验或应用名>/<版本或日期>/` 分层，避免根目录散落。
4. **读取他处数据须白名单**：示例代码只读 `dataset/` 与（Copilot 场景）`~/projects/tsproj_ml`，路径解析必须防穿越（见 [30-copilot](../30-copilot/index.md) 安全边界）。

## 相关

- [environment](../00-overview/environment.md) ｜ [Copilot 安全边界](../../AGENTS.md)
