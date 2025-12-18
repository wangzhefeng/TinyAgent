# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm_agent.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-22
# * Version     : 1.0.112217
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
from typing import List, Dict

from openai import OpenAI
from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class AgentsLLM:
    """
    LLM Client，用于调用任何兼容 OpenAI API 的服务，并默认使用流式响应
    """
    def __init__(self, model: str=None, apiKey: str=None, baseUrl: str=None, timeout: int=None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型 ID、API 密钥和服务地址必须被提供或在 .env 文件中定义。")

        # llm client
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)
    
    def think(self, messages: List[Dict[str, str]], temperature: float=0.0) -> str:
        """
        调用 LLM 进行思考，并返回其响应

        Args:
            messages (List[Dict[str, str]]): _description_
            temperature (float, optional): _description_. Defaults to 0.0.

        Returns:
            str: _description_
        """
        try:
            # 调用 LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            
            # 处理流式响应
            print(f"✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            # 在流式输出结束后换行
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None




# 测试代码 main 函数
def main():
    # Client 使用示例
    try:
        # llm client
        llmClient = AgentsLLM()
        # message
        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"},
        ]
        # llm response
        print(f"--- 调用 LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- 完整模型响应 ---")
            print(responseText)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
