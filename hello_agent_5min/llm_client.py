# -*- coding: utf-8 -*-

# ***************************************************
# * File        : llm_client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-17
# * Version     : 1.0.111721
# * Description : description
# * Link        : link
# * Requirement : 相关模块版本需求(例如: numpy >= 2.1.0)
# ***************************************************

# python libraries
import sys
from pathlib import Path
ROOT = str(Path.cwd())
if ROOT not in sys.path:
    sys.path.append(ROOT)
import warnings
warnings.filterwarnings("ignore")

from openai import OpenAI

from utils.log_util import logger

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class OpenAICompatibleClient:
    """
    一个用于调用任何兼容 OpenAI API 的 LLM 服务的客户端
    """
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        调用 LLM API 生成回应

        Args:
            prompt (str): 用户提示
            system_prompt (str): 系统提示

        Returns:
            str: _description_
        """
        logger.info(f"正在调用大语言模型...")
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
            )
            answer = response.choices[0].message.content
            logger.info(f"大语言模型响应成功。")
            return answer
        except Exception as e:
            logger.info(f"调用 LLM API 时发生错误: {e}")
            return "错误：调用语言模型服务时出错。"




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
