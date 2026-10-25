> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 编码风格

对齐 TinyLLM 既有风格。**迁移期旧代码保持不动；新写与重写的代码必须遵守。**

## 1. 文件组织

- `learn/`、`apps/` 下的示例代码沿用历史约定：`# -*- coding: utf-8 -*-` 声明 + 横幅注释块（File / Author / Email / Date / Version / Description / Link / Requirement）。
- 新增的框架 / 工具 / 脚本代码（`packages/`、`utils/`、`scripts/`、`tests/`）不写 utf-8 声明与横幅，用模块 docstring 开篇（对应 ruff `UP009` / `D100` 规则）。
- 分节注释：`# python libraries`（标准库与第三方）、`# global variable`，导入与全局定义分区（示例代码适用；新代码用常规分段即可）。

## 2. 导入

三段式、段内字母序：标准库 → 第三方 → 本地（`utils/`、`packages/`）。一行一个；禁 `import *`（`__init__.py` 配 `__all__` 除外）。

## 3. 日志

- 统一 `from utils.log_util import logger`；禁止调试 print 入库（演示输出放在 `main()` 中）。
- 模块级惯例：

```python
LOGGING_LABEL = Path(__file__).name[:-3]
os.environ["LOG_NAME"] = LOGGING_LABEL
from utils.log_util import logger   # 本地导入段
```

## 4. docstring 与注释

- 公开函数/类：Google 风格；首行英文一句话，正文与 Args / Returns 用中文。
- 行内注释中文为主，解释"为什么"而非"做什么"；待办以 `# TODO:` 开头并带上下文。

## 5. 命名与类型

- 函数/变量 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE`。
- 公开 API 必须类型注解，内部实现鼓励。

## 6. main guard

```python
# 测试代码 main 函数
def main():
    ...

if __name__ == "__main__":
    main()
```

## 7. 路径与运行

- 一切脚本从仓库根目录运行：`uv run python learn/level1_from_scratch/react/run.py`。
- 迁移期旧代码的 `sys.path` hack 保留；**新代码禁止新增**，改用包导入或 workspace 安装。

## 8. 依赖管理

- 新增第三方依赖须说明理由；重依赖进 `packages/tinyagent-core` 的 extras（`mcp` / `vector` / `local`）或根 dependency-groups（`dev` / `course`）。
- 框架包用下限约束；学习示例依赖跟随根锁定（`uv.lock`）。

## 9. Lint

- ruff（根 `pyproject.toml` 已配置）；提交前 `uv run ruff check .`。
- 新代码零告警；迁移期旧代码豁免历史 E / D 类告警。
