> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 编码风格

新写与重写的代码必须遵守；历史代码保持原风格，除非进入对应重构范围。

## 1. 文件组织

- 新框架、工具和脚本使用模块 docstring 开篇，不写 utf-8 声明或历史横幅。
- import 三段式：标准库 → 第三方 → 本地；段内字母序，一行一个；禁止 `import *`（`__init__.py` 配 `__all__` 除外）。
- 保留既有文件的分节注释；新代码使用常规模块和函数分区，不照搬历史横幅。

## 2. 日志与输出

- 日志统一 `from utils.log_util import logger`，禁止调试 print 入库。
- CLI 用户输出可放在 `main()` 或渠道层；库代码不得使用 print 调试。

## 3. docstring 与注释

- 公开函数/类使用 Google 风格 docstring：首行英文一句话，正文与 Args / Returns 可用中文。
- 行内注释解释“为什么”而非复述“做什么”；待办以 `# TODO:` 开头并带上下文。
- 行为变化后同步更新相关注释和 docstring，避免描述旧行为。

## 4. 命名与类型

- 函数/变量 `snake_case`，类 `PascalCase`，常量 `UPPER_SNAKE`。
- 公开 API 必须类型注解，内部实现鼓励。

## 5. main guard

```python
# 测试代码 main 函数
def main():
    ...

if __name__ == "__main__":
    main()
```

## 6. 路径与运行

- 脚本一律从仓库根目录运行，例如 `uv run python -m tinyagent.cli --help`。
- 新代码禁止新增 `sys.path` hack，使用包导入或 workspace 安装。

## 7. 依赖管理

- 新增第三方依赖须说明理由；库依赖只进根 `[project].dependencies`。
- MCP、SOCKS 等可选能力进入 extras；开发测试依赖进入 `dependency-groups.dev`。

## 8. Lint

- 提交前运行 `uv run ruff check .`。
- 新代码零告警；迁移期旧代码仅豁免明确的历史规则。
