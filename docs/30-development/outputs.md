> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 数据与产物目录约定

仓库根下四个**运行时目录**：只在本机存在，一律被 `.gitignore` 忽略、不提交、不进文档检查范围（`scripts/check_docs.py` 已豁免）。

| 目录 | 用途 | 写入方 |
|---|---|---|
| `dataset/` | 实验数据、RAG 语料等输入数据 | 手动放置；脚本按需只读 |
| `downloaded_models/` | 下载的离线模型权重 | 模型下载脚本 |
| `results/` | Agent 运行产物、评测结果和隔离工作副本 | 各阶段与应用 |
| `logs/` | 运行日志：`utils/log_util` 与框架 `logs/tinyagent/`（sessions / traces） | 框架与日志器自动 |

## 规则

1. **不入库**：四个目录整体 gitignore；体积大的中间产物绝不提交。
2. **按需创建**：脚本写入前 `mkdir(parents=True, exist_ok=True)` 自建。
3. **路径自解释**：建议按 `results/<应用>/<阶段或日期>/` 分层，避免根目录散落。
4. **数据边界**：默认只读独立 fixture 或 sanitized 数据，不读取现有真实项目；访问其他路径必须经过工作区与白名单校验。

## 相关

- [environment](../00-overview/environment.md) ｜ [个人 Agent 安全边界](../../AGENTS.md)
