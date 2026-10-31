# nami-agent：从零手写 Agent 配套代码

「从零手写 Agent」系列的配套代码。每一课一个目录，目录里是**学完这一课时**的完整代码，可以直接运行。

| 目录 | 对应课程 | 这一课新增 |
|---|---|---|
| lesson-01 | 第 1 课 最小循环 | `agent.py`：三个工具 + 一个 while 循环 |
| lesson-02 | 第 2 课 工具系统 | `tools.py`：注册表、统一执行器 |
| lesson-03 | 第 3 课 权限 | `permissions.py`：硬规则 → 风险分级 → 人工确认 |
| lesson-04 | 第 4 课 上下文管理 | `context.py`：截断 → 清理 → 摘要，会话持久化 |
| lesson-05 | 第 5 课 Skills | `skills.py`：AGENTS.md 常驻，技能按需加载 |
| lesson-06 | 第 6 课 接入聊天软件 | `telegram.py`、`bot.py`：常驻、聊天确认、白名单 |
| lesson-07 | 第 7 课 定时任务与心跳 | `scheduler.py`：无人值守的预授权、心跳 |
| lesson-08 | 第 8 课 MCP | `mcp_client.py`：stdio MCP 客户端；`demo_mcp_server.py`：示例服务器 |
| lesson-09 | 第 9 课 子 Agent 与多 Agent | `subagent.py`：独立上下文的子 Agent，并行只读 |
| lesson-10 | 第 10 课 计划 | `planning.py`：待办清单、由代码强制只读的计划模式 |
| lesson-11 | 第 11 课 记忆 | `memory.py`：长期记忆（每条确认）、会话检索 |

## 运行

需要 Python 3.9+。

```bash
pip install openai pytest
export API_KEY=你的模型密钥
# 默认用 DeepSeek；换别的 OpenAI 兼容模型：
# export BASE_URL=https://...   MODEL=模型名

cd lesson-05
export NAMI_WORKSPACE=~/agent-workspace   # 第 3 课起：Agent 只能动这个目录
mkdir -p $NAMI_WORKSPACE
python agent.py
```

第 6 课起的 `bot.py` 另外需要 `TG_BOT_TOKEN` 和 `TG_ALLOWED_USERS`，见第 6 课。

第 8 课起可以接入 MCP 服务器：在 `~/.nami-agent/mcp.json` 里配置，格式见第 8 课。第 12–18 课是对主流 Agent 的拆解，没有新代码。

## 环境变量

| 变量 | 作用 | 默认值 |
|---|---|---|
| `API_KEY` | 模型密钥 | 必填 |
| `BASE_URL` | OpenAI 兼容接口地址 | `https://api.deepseek.com` |
| `MODEL` | 模型名 | `deepseek-chat` |
| `NAMI_WORKSPACE` | Agent 的工作区（第 3 课起） | 启动时的当前目录 |
| `NAMI_STATE_DIR` | 会话记录、定时任务等程序状态（第 4 课起），放在工作区之外 | `~/.nami-agent` |

## 测试

第 3 课起每个目录都有测试，不需要真的调用模型：

```bash
cd lesson-11 && pytest -q
```

## 安全提醒

这是教学代码。第 3 课第八节写了这套权限机制防不住什么：它能防误操作和低成本的越界，防不了有意的攻击。请在专门的工作区目录里运行，不要指向你的主目录。
