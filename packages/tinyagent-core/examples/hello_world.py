# -*- coding: utf-8 -*-

# python libraries
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import CalculatorTool
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 创建 LLM 实例 - 框架自动检测 provider
llm = HelloAgentsLLM()
# 或手动指定 provider(可选)
# llm = HelloAgentsLLM(provider="modelscope")

# 创建 SimpleAgent
agent = SimpleAgent(
    name="AI助手",
    llm=llm,
    system_prompt="你是一个有用的AI助手",
)

# ------------------------------
# 基础对话
# ------------------------------
response = agent.run("你好！请介绍一下自己")
print(response)

# ------------------------------
# 添加工具功能（可选）
# ------------------------------
calculator = CalculatorTool()
# agent.add_tool(calculator)

# 现在可以使用工具了
response = agent.run("请帮我计算 2 + 2 * 4")
print(response)

# ------------------------------
# 查看对话历史
# ------------------------------
print(f"历史消息数：{len(agent.get_history())}")
