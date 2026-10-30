"""Minimal quickstart: ``@tool`` + ``TinyAgent``."""

import ast
import operator

from tinyagent import TinyAgent, tool


@tool
def calculator(expression: str) -> str:
    """Arithmetic calculator supporting + - * / // % ** and parentheses."""
    bin_ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
    }
    unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in bin_ops:
            return bin_ops[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return unary_ops[type(node.op)](evaluate(node.operand))
        raise ValueError(f"unsupported node: {type(node).__name__}")

    return str(evaluate(ast.parse(expression, mode="eval")))


def main():
    agent = TinyAgent(tools=[calculator], codec="react")

    result = agent.run("你好，请介绍一下你能做什么。")
    print(f"[no-tool answer] {result.text}\n")

    result = agent.run("Compute (123 + 456) * 2 with the calculator.")
    print(f"[tool answer] {result.text} ({result.steps} tool round(s))")


if __name__ == "__main__":
    main()
