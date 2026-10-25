# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tool.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 2.0.1025
# * Description : ReAct Agent 工具集：calculator（无外部依赖）+ google_search（可选）
# ***************************************************

# python libraries
import ast
import json
import operator
import os
from typing import Dict, List

# third-party libraries
import requests
from dotenv import find_dotenv, load_dotenv

# global variable
_ = load_dotenv(find_dotenv())

# 安全算术求值：仅允许数字、+ - * / // % ** 与括号
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node):
    """
    递归求值白名单内的算术表达式节点。
    """
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")


class Tools:
    """
    工具集：`toolConfig` 提供工具描述（供 system prompt 构建），
    `call` 按 name_for_model 分发到具体实现。
    """

    def __init__(self) -> None:
        self.toolConfig = self._tools()

    def _tools(self) -> List[Dict]:
        """
        工具描述信息：让模型知道可调用哪些工具、工具用途与参数。
        """
        tools = [
            {
                "name_for_human": "计算器",
                "name_for_model": "calculator",
                "description_for_model": "四则算术计算器，支持 + - * / // % ** 与括号，输入一个算术表达式字符串。",
                "parameters": [
                    {
                        "name": "expression",
                        "description": "算术表达式，例如 (123 + 456) * 2",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
            },
            {
                "name_for_human": "谷歌搜索",
                "name_for_model": "google_search",
                "description_for_model": "谷歌搜索是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。",
                "parameters": [
                    {
                        "name": "search_query",
                        "description": "搜索关键词或短语",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
            },
        ]
        return tools

    def call(self, name: str, **kwargs) -> str:
        """
        按 name_for_model 分发工具调用。

        Args:
            name (str): 工具名（name_for_model）
            **kwargs: 工具参数

        Returns:
            str: 工具执行结果文本
        """
        dispatcher = {
            "calculator": self.calculator,
            "google_search": self.google_search,
        }
        if name not in dispatcher:
            return f"未知工具: {name}，可用工具: {list(dispatcher)}"
        return dispatcher[name](**kwargs)

    def calculator(self, expression: str) -> str:
        """
        安全算术求值（ast 白名单，无 eval 任意代码风险）。

        Args:
            expression (str): 算术表达式

        Returns:
            str: 计算结果或错误信息
        """
        try:
            return str(_safe_eval(ast.parse(expression, mode="eval")))
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as e:
            return f"计算失败: {e}"

    def google_search(self, search_query: str) -> str:
        """
        谷歌搜索（serper.dev，需在 .env 配置 GOOGLE_SERPER_API_KEY，
        未配置时返回不可用提示而不报错）。

        Args:
            search_query (str): 查询内容/问题

        Returns:
            str: 查询结果摘要
        """
        api_key = os.environ.get("GOOGLE_SERPER_API_KEY")
        if not api_key:
            return "工具不可用：未配置 GOOGLE_SERPER_API_KEY（在 .env 中取消注释并填入）"

        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": search_query})
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }
        response = requests.request(
            method="POST",
            url=url,
            headers=headers,
            data=payload,
            timeout=30,
        ).json()

        return response["organic"][0]["snippet"]
