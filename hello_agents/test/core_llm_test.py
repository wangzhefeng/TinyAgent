# -*- coding: utf-8 -*-

# ***************************************************
# * File        : core_llm_test.py
# * Author      : Zhefeng Wang
# * Email       : zfwang7@gmail.com
# * Date        : 2025-12-20
# * Version     : 1.0.122023
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
from typing import Optional

from openai import OpenAI

from hello_agents.core.llm import AgentsLLM

# global variable
LOGGING_LABEL = Path(__file__).name[:-3]


class LLM(AgentsLLM):
    """
    一个自定义的 LLM 客户端，通过继承增加了对 ModelScope 的支持
    """
    def __init__(self, 
                 model: Optional[str]=None, 
                 api_key: Optional[str]=None, 
                 base_url: Optional[str]=None, 
                 provider: Optional[int]="auto",
                 **kwargs):
        # 检查 provider 是否为我们想处理的 'modelscope'
        if provider == "modelscope":
            print("正在使用自定义的 ModelScope Provider")
            self.provider = "modelscope"

            # 解析 ModelScope 的凭证
            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or "https://api-inference.modelscope.cn/v1/"

            # 验证凭证是否存在
            if not self.api_key:
                raise ValueError("ModelScope API key not found. Please set MODELSCOPE_API_KEY environment variable.")
            
            # 设置默认模型和其他参数
            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen2.5-VL-72B-Instruct"
            self.temperature = kwargs.get("temperature", 0.7)
            self.max_tokens = kwargs.get("max_tokens")
            self.timeout = kwargs.get("timeout", 60)

            # 使用获取的参数创建 OpenAI 客户端实例
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        else:
            # 如果不是 modelscope, 则完全使用父类的原始逻辑来处理
            super().__init__(model=model, api_key=api_key, base_url=base_url, **kwargs)




# 测试代码 main 函数
def main():
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    # 实例化重写的客户端，并指定 provider
    llm = LLM(provider="modelscope")
    # 准备消息
    messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]
    # 发起调用，think 等方法都已经从父类继承，无需重写
    response_stream = llm.think(messages)
    # 打印响应
    print("ModelScope Response:")
    for chunk in response_stream:
        # chunk 已经是文本片段，可以直接使用
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    main()
