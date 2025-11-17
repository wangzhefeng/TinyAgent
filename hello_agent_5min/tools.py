# -*- coding: utf-8 -*-

# ***************************************************
# * File        : tools.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-17
# * Version     : 1.0.111721
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import os
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")
import requests
from dotenv import find_dotenv, load_dotenv

from tavily import TavilyClient

from utils.log_util import logger

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]

# 读取本地/项目环境变量
_ = load_dotenv(find_dotenv())


# ##############################
# 工具1：查询真实天气
# ##############################
def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息

    Args:
        city (str): _description_

    Returns:
        str: _description_
    """
    # API 端点，我们请求 JSON 格式的数据
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200(成功)
        response.raise_for_status()
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data["current_condition"][0]
        weather_desc = current_condition["weatherDesc"][0]["value"]
        temp_c = current_condition["temp_C"]

        # 格式化成自然语言返回
        return f"{city} 当前天气: {weather_desc}, 气温 {temp_c} 摄氏度"
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误: 查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误: 解析天气数据失败, 可能是城市名无效 - {e}"

# ##############################
# 工具2：搜索并推荐旅游景点
# ##############################
def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用 Tavily Search API 搜索并返回优化后的景点推荐。

    Args:
        city (str): _description_
        weather (str): _description_

    Returns:
        str: _description_
    """
    # 1. 从环境变量中读取 API 密钥
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误: 未配置 TAVILY_API_KEY 环境变量"
    
    # 2. 初始化 Tavily Client
    tavily = TavilyClient(api_key=api_key)

    # 3. 构造一个精确的查询
    query = f"'{city}' 在'{weather}' 天气下最值得去的旅游景点推荐及理由"

    try:
        # 4. 调用 API，include_answer=True 会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        # 5. Tavily 返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        # 如果没有综合性回答， 则格式化原始结果
        formatted_results = [
            f"- {result['title']}: {result['content']}"
            for result in response.get("results", [])
        ]
        if not formatted_results:
            return "抱歉，没有找到相关的旅游景点推荐。"
        
        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)
    except Exception as e:
        return f"错误: 执行 Tavily 搜索时出现问题 - {e}"


# ##############################
# 将所有功率函数放入一个字典，供主循环调用
# ##############################
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}




# 测试代码 main 函数
def main():
    res = get_weather("Shanghai")
    print(res)

    res = get_attraction("Shanghai", "Clear")
    print(res)

if __name__ == "__main__":
    main()
