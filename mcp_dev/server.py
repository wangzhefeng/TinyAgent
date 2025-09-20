# -*- coding: utf-8 -*-

# ***************************************************
# * File        : server.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-05-17
# * Version     : 1.0.051716
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# * TODO        : 1.
# ***************************************************

__all__ = []

# python libraries
import os
import sys
ROOT = str(os.getcwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)

from mcp.server.fastmcp import FastMCP

# global variable
LOGGING_LABEL = __file__.split('/')[-1][:-3]


# Create an MCP server
mcp = FastMCP("Weather Service")


@mcp.tool()
def get_weather(location: str) -> str:
    """
    Get the current weather for a specified location.
    """
    return f"Weather in {location}: Sunny, 72°F" 


@mcp.resource("weather://{location}")
def weather_resource(location: str) -> str:
    """
    Provide weather data as a resource
    """
    return f"Weather data for {location}: Sunny, 72°F"


@mcp.prompt()
def weather_report(location: str) -> str:
    """
    Create a weather report prompt.
    """
    return f"""You are a weather reporter. Weather report for {location}?"""




# 测试代码 main 函数
def main():
    # mcp.run(transport="sse", port = "3001")
    mcp.run()
    
    """
    $ mcp dev server.py
    """

if __name__ == "__main__":
    main()
