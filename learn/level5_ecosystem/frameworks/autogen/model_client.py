# -*- coding: utf-8 -*-

# ***************************************************
# * File        : model_client.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-11-29
# * Version     : 1.0.112918
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

from autogen_ext.models.openai import OpenAIChatCompletionClient

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


def create_openai_model_client():
    """
    创建并配置 OpenAI 模型客户端
    """
    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL_ID", "gpt-4o"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    )


# ##############################
# 如果你想使用非 OpenAI 系列的模型（如 DeepSeek、通义千问等），
# 在 0.7.4 版本中需要在 OpenAIChatCompletionClient 的参数中传入模型信息字典。
# ##############################
# DeepSeek
model_client = OpenAIChatCompletionClient(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    model_info={
        "function_calling": True,
        "max_tokens": 4096,
        "context_length": 32768,
        "vision": False,
        "json_output": True,
        "family": "deepseek",
        "structured_output": True,
    }
)




# 测试代码 main 函数
def main():
    pass

if __name__ == "__main__":
    main()
