# -*- coding: utf-8 -*-

# ***************************************************
# * File        : hello_world.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : tinyagent v0.1 最小示例：@tool + TinyAgent
# ***************************************************

# python libraries
import ast
import operator

# local libraries
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
    # 默认 OpenAIChatModel 从 .env 读取 provider/base_url/key/model
    agent = TinyAgent(tools=[calculator], codec="react")

    result = agent.run("你好，请介绍一下你能做什么。")
    print(f"[无工具回答] {result.text}\n")

    result = agent.run("请用计算器算一下 (123 + 456) * 2")
    print(f"[工具回答] {result.text}（{result.steps} 轮工具调用）")


if __name__ == "__main__":
    main()
