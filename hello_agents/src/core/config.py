# -*- coding: utf-8 -*-

"""
配置管理
"""

# python libraries
import os
from typing import Optional, Dict, Any

from pydantic import BaseModel


class Config(BaseModel):
    """
    Agents 配置类
    """
    
    # LLM 配置
    default_model: str = "gpt-3.5-turbo"
    default_provider: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # 系统配置
    debug: bool = False
    log_level: str = "INFO"
    
    # 其他配置
    max_history_length: int = 100
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        从环境变量创建配置
        """
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS")) if os.getenv("MAX_TOKENS") else None,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return self.model_dump()



# 测试代码 main 函数
def main():
    config = Config()
    print(config.to_dict())

if __name__ == "__main__":
    main()
