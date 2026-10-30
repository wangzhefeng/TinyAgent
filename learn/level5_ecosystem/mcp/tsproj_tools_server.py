# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tsproj_tools_server.py
# * Author      : Zhefeng Wang
# * Email       : wangzhefengr@163.com
# * Date        : 2026-10-25
# * Version     : 1.0.1025
# * Description : 面向 tsproj_ml 的只读 MCP server（Copilot C3 的工具服务化）
# ***************************************************

# python libraries

# third-party libraries
from mcp.server.fastmcp import FastMCP

# local libraries
from apps.experiment_copilot.copilot0 import tools as copilot_tools

# global variable
mcp_server = FastMCP("tsproj-ml-readonly")


@mcp_server.tool()
def list_configs() -> str:
    """列出 tsproj_ml 仓库 config/ 下的全部实验配置 YAML 路径。"""
    return copilot_tools.list_configs()


@mcp_server.tool()
def read_config(rel_path: str) -> str:
    """读取指定实验配置 YAML 的完整内容（相对 config/ 的路径）。"""
    return copilot_tools.read_config(rel_path)


@mcp_server.tool()
def list_results() -> str:
    """列出 tsproj_ml 已有实验结果目录（模型-策略标识）。"""
    return copilot_tools.list_results()


@mcp_server.tool()
def read_result_summary(rel_dir: str) -> str:
    """读取单个实验结果的策略、回测几何与平均指标（MAE/RMSE/MAPE/Accuracy）。"""
    return copilot_tools.read_result_summary(rel_dir)


# 测试代码 main 函数
def main():
    # stdio 传输（默认），供框架/任意 MCP client 挂载：
    #   python -m learn.level5_ecosystem.mcp.tsproj_tools_server
    mcp_server.run()


if __name__ == "__main__":
    main()
