# -*- coding: utf-8 -*-

# ***************************************************
# * File        : my_simple_agent.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : L2 —— SimpleAgent 能力对照（原 hello_agents 版已并入 tinyagent）
# ***************************************************

# python libraries
import ast
import operator

# third-party libraries
from tinyagent import TinyAgent, tool


@tool
def calculator(expression: str) -> str:
    """四则算术计算器，支持 + - * / // % ** 与括号。"""
    bin_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
    }
    unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in bin_ops:
            return bin_ops[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return unary_ops[type(node.op)](evaluate(node.operand))
        raise ValueError(f"不支持的表达式节点: {type(node).__name__}")

    return str(evaluate(ast.parse(expression, mode="eval")))


def main():
    """
    对照说明：原示例用 hello_agents 的 SimpleAgent（name/llm/system_prompt）。
    tinyagent 用一个门面覆盖其三种变体：无工具 = SimpleAgent、带工具 =
    ToolAwareAgent、codec="native" = FunctionCallAgent。
    """
    agent = TinyAgent(tools=[calculator], system="你是一个有用的AI助手")

    print(agent.run("你好！请介绍一下自己").text)
    print("-" * 40)
    result = agent.run("请帮我计算 2 + 2 * 4", session_id="simple-agent")
    print(f"{result.text}（{result.steps} 轮工具调用）")


if __name__ == "__main__":
    main()
