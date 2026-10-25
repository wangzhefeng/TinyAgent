# -*- coding: utf-8 -*-

# ***************************************************
# * File        : react_with_framework.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : L2 对照 demo——用 tinyagent 框架重写 L1 手写 ReAct
# ***************************************************

# python libraries
import ast
import operator

# third-party libraries
from tinyagent import FileSessionStore, JsonlTracer, TinyAgent, tool


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
    对照 L1 手写版（learn/level1_from_scratch/react/）：
    手写 ~180 行的 Agent/工具分发/解析循环，这里收敛为声明式组装——
    @tool 自动生成 JSON Schema，TinyAgent 组装六协议，session/tracer 可选注入。
    """
    agent = TinyAgent(
        tools=[calculator],
        codec="react",
        session=FileSessionStore(),          # 会话可恢复（logs/tinyagent/sessions/）
        tracer=JsonlTracer(),                # 事件流追踪（logs/tinyagent/traces/）
    )

    result = agent.run("请用计算器算一下 2 的 10 次方", session_id="l2-demo")
    print(f"[回答] {result.text}")
    print(f"[轮数] {result.steps}，消息数 {len(result.messages)}")

    # 会话历史可加载续聊（SessionStore 协议）
    history = FileSessionStore().load_messages("l2-demo")
    print(f"[会话] l2-demo 已持久化 {len(history)} 条消息")


if __name__ == "__main__":
    main()
